"""
PvP Rooms API — PostgreSQL + WebSocket.
"""
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional, List
import secrets

from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models import RoomStatus
from app.repositories.room_repository import RoomRepository
from app.services import PvPGameEngine, ProvablyFairEngine
from app.services.escrow import EscrowService
from app.services.websocket_manager import ws_manager

router = APIRouter(prefix="/api/pvp", tags=["PvP"])

engine = PvPGameEngine()


# ═══════════════════════════════════════════════════════════════════════
# Schemas
# ═══════════════════════════════════════════════════════════════════════

class CreateRoomRequest(BaseModel):
    room_type: str = "classic"
    min_bet_ton: Decimal = Field(default=Decimal("1"), ge=0)
    max_bet_ton: Optional[Decimal] = None
    max_players: int = Field(default=10, ge=2, le=50)


class CreateRoomResponse(BaseModel):
    room_code: str
    server_seed_hash: str
    status: str
    min_bet_ton: Decimal
    max_bet_ton: Optional[Decimal]
    max_players: int
    countdown_seconds: int


class PlaceBetRequest(BaseModel):
    user_id: int
    user_telegram_id: int
    user_name: str
    user_avatar: Optional[str] = None
    gift_address: str
    gift_name: str
    gift_image_url: Optional[str] = None
    gift_value_ton: Decimal


class BetInfo(BaseModel):
    bet_id: int
    user_id: int
    user_name: str
    user_avatar: Optional[str] = None
    gift_name: str
    gift_image_url: Optional[str] = None
    gift_value_ton: Decimal
    tickets_count: int
    win_chance_percent: Decimal


class RoomState(BaseModel):
    room_code: str
    room_type: str = "classic"
    status: str
    total_pool_ton: Decimal
    total_bets: int
    total_players: int
    bets: List[BetInfo]
    server_seed_hash: str
    countdown_seconds: int = 30
    online_count: int = 0


class SpinResultResponse(BaseModel):
    room_code: str
    winner_user_id: int
    winner_user_name: str
    winning_ticket: int
    total_tickets: int
    spin_degree: Decimal
    winnings_ton: Decimal
    house_fee_ton: Decimal
    server_seed: str


# ═══════════════════════════════════════════════════════════════════════
# Endpoints
# ═══════════════════════════════════════════════════════════════════════

@router.post("/rooms", response_model=CreateRoomResponse)
async def create_room(
    req: CreateRoomRequest,
    db: AsyncSession = Depends(get_db),
):
    """Create new PvP room with provably fair seed."""
    repo = RoomRepository(db)

    room_code = secrets.token_urlsafe(8)[:8].upper()
    room_params = engine.create_room(
        room_code=room_code,
        min_bet_ton=req.min_bet_ton,
        max_bet_ton=req.max_bet_ton,
        max_players=req.max_players,
    )

    room = await repo.create_room(**room_params)

    return CreateRoomResponse(
        room_code=room.room_code,
        server_seed_hash=room.server_seed_hash,
        status=room.status.value,
        min_bet_ton=room.min_bet_ton,
        max_bet_ton=room.max_bet_ton,
        max_players=room.max_players,
        countdown_seconds=room.countdown_seconds,
    )


@router.post("/rooms/{room_code}/bet")
async def place_bet(
    room_code: str,
    req: PlaceBetRequest,
    db: AsyncSession = Depends(get_db),
    x_wallet_address: Optional[str] = Header(None),
):
    """
    Place bet in room.

    Optionally verifies NFT ownership if X-Wallet-Address header provided.
    """
    repo = RoomRepository(db)

    room = await repo.get_room(room_code)
    if not room:
        raise HTTPException(404, "Room not found")

    if room.status not in (RoomStatus.WAITING, RoomStatus.COUNTDOWN):
        raise HTTPException(400, "Room is not accepting bets")

    if req.gift_value_ton < room.min_bet_ton:
        raise HTTPException(400, f"Minimum bet is {room.min_bet_ton} TON")

    if room.max_bet_ton and req.gift_value_ton > room.max_bet_ton:
        raise HTTPException(400, f"Maximum bet is {room.max_bet_ton} TON")

    # Verify NFT ownership if wallet provided
    if x_wallet_address:
        escrow = EscrowService(
            db,
            tonapi_key=getattr(settings, "TONAPI_KEY", None),
        )
        try:
            price = await escrow.verify_and_price_nft(
                x_wallet_address,
                req.gift_address,
            )
            if price is None:
                raise HTTPException(403, "NFT ownership verification failed or NFT already in use")
        finally:
            await escrow.close()

    # Check NFT not already locked
    locked = await repo.is_nft_locked(req.gift_address)
    if locked:
        raise HTTPException(409, "This NFT is already in an active game")

    # Add bet
    bet = await repo.add_bet(
        room,
        user_id=req.user_id,
        user_telegram_id=req.user_telegram_id,
        user_name=req.user_name,
        user_avatar=req.user_avatar,
        gift_address=req.gift_address,
        gift_name=req.gift_name,
        gift_image_url=req.gift_image_url,
        gift_value_ton=req.gift_value_ton,
        tickets_start=0,
        tickets_end=0,
        tickets_count=0,
        win_chance_percent=Decimal("0"),
    )

    # Ensure stats exist
    await repo.get_or_create_stats(req.user_id, req.user_telegram_id)

    # Refresh room state
    room = await repo.get_room(room_code)

    # Start countdown if 2+ unique players
    unique_users = {b.user_id for b in room.bets}
    if len(unique_users) >= 2 and room.status == RoomStatus.WAITING:
        await repo.update_room(
            room_code,
            status=RoomStatus.COUNTDOWN,
            started_at=datetime.now(timezone.utc),
        )

        await ws_manager.broadcast(room_code, {
            "type": "countdown_start",
            "data": {"countdown_seconds": room.countdown_seconds},
        })

    # Broadcast bet placed
    await ws_manager.broadcast(room_code, {
        "type": "bet_placed",
        "data": {
            "bet_id": bet.id,
            "user_id": req.user_id,
            "user_name": req.user_name,
            "user_avatar": req.user_avatar,
            "gift_name": req.gift_name,
            "gift_image_url": req.gift_image_url,
            "gift_value_ton": str(req.gift_value_ton),
            "total_pool_ton": str(room.total_pool_ton),
            "total_bets": room.total_bets,
            "total_players": room.total_players,
        },
    })

    return {
        "bet_id": bet.id,
        "room_code": room_code,
        "status": room.status.value,
        "total_pool_ton": str(room.total_pool_ton),
        "total_bets": room.total_bets,
        "total_players": room.total_players,
    }


@router.get("/rooms/{room_code}", response_model=RoomState)
async def get_room(
    room_code: str,
    db: AsyncSession = Depends(get_db),
):
    """Get room state with bets and chances."""
    repo = RoomRepository(db)

    room = await repo.get_room(room_code)
    if not room:
        raise HTTPException(404, "Room not found")

    # Calculate tickets and chances
    total_tickets = engine.assign_tickets(room.bets)
    engine.calculate_win_chances(room.bets, total_tickets)

    bets_info = [
        BetInfo(
            bet_id=bet.id,
            user_id=bet.user_id,
            user_name=bet.user_name,
            user_avatar=bet.user_avatar,
            gift_name=bet.gift_name,
            gift_image_url=bet.gift_image_url,
            gift_value_ton=bet.gift_value_ton,
            tickets_count=bet.tickets_count,
            win_chance_percent=round(bet.win_chance_percent, 2),
        )
        for bet in room.bets
    ]

    return RoomState(
        room_code=room.room_code,
        room_type=room.room_type.value,
        status=room.status.value,
        total_pool_ton=room.total_pool_ton,
        total_bets=room.total_bets,
        total_players=room.total_players,
        bets=bets_info,
        server_seed_hash=room.server_seed_hash,
        countdown_seconds=room.countdown_seconds,
        online_count=ws_manager.get_room_count(room_code),
    )


@router.post("/rooms/{room_code}/spin", response_model=SpinResultResponse)
async def spin_wheel(
    room_code: str,
    client_seed: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """Spin wheel manually (auto-spin handles this normally)."""
    repo = RoomRepository(db)

    room = await repo.get_room(room_code)
    if not room:
        raise HTTPException(404, "Room not found")

    if room.status == RoomStatus.FINISHED:
        raise HTTPException(400, "Room already finished")

    unique_users = {b.user_id for b in room.bets}
    if len(unique_users) < 2:
        raise HTTPException(400, "Need at least 2 players")

    await repo.update_room(room_code, status=RoomStatus.SPINNING)
    await ws_manager.broadcast(room_code, {"type": "spin_start", "data": {}})

    result = engine.spin_wheel(room, room.bets, client_seed)

    winner_bet = next(
        (b for b in room.bets if b.id == result.winning_bet_id),
        None,
    )

    winnings, fee = engine.calculate_winnings(
        room.total_pool_ton,
        room.house_fee_percent,
    )

    await repo.update_room(
        room_code,
        status=RoomStatus.FINISHED,
        winner_user_id=result.winner_user_id,
        winner_ticket=result.winning_ticket,
        winning_spin_degree=result.spin_degree,
        finished_at=datetime.now(timezone.utc),
    )

    # Update stats
    for bet in room.bets:
        if bet.user_id == result.winner_user_id:
            await repo.update_stats_win(bet.user_id, bet.gift_value_ton, winnings)
        else:
            await repo.update_stats_loss(bet.user_id, bet.gift_value_ton)

    # Broadcast result
    await ws_manager.broadcast(room_code, {
        "type": "spin_result",
        "data": {
            "winner_user_id": result.winner_user_id,
            "winner_user_name": winner_bet.user_name if winner_bet else "Unknown",
            "winning_ticket": result.winning_ticket,
            "total_tickets": sum(b.tickets_count for b in room.bets),
            "spin_degree": str(result.spin_degree),
            "winnings_ton": str(winnings),
            "house_fee_ton": str(fee),
            "server_seed": room.server_seed,
        },
    })

    return SpinResultResponse(
        room_code=room_code,
        winner_user_id=result.winner_user_id,
        winner_user_name=winner_bet.user_name if winner_bet else "Unknown",
        winning_ticket=result.winning_ticket,
        total_tickets=sum(b.tickets_count for b in room.bets),
        spin_degree=result.spin_degree,
        winnings_ton=winnings,
        house_fee_ton=fee,
        server_seed=room.server_seed,
    )


@router.get("/rooms")
async def list_rooms(
    status: Optional[str] = None,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
):
    """List rooms."""
    repo = RoomRepository(db)

    if status:
        try:
            room_status = RoomStatus(status)
        except ValueError:
            raise HTTPException(400, f"Invalid status: {status}")
        rooms = await repo.list_rooms(status=room_status, limit=limit)
    else:
        rooms = await repo.list_rooms(limit=limit)

    return {
        "total": len(rooms),
        "rooms": [
            {
                "room_code": r.room_code,
                "room_type": r.room_type.value,
                "status": r.status.value,
                "total_pool_ton": str(r.total_pool_ton),
                "total_bets": r.total_bets,
                "total_players": r.total_players,
                "server_seed_hash": r.server_seed_hash,
                "max_players": r.max_players,
                "min_bet_ton": str(r.min_bet_ton),
                "online_count": ws_manager.get_room_count(r.room_code),
            }
            for r in rooms
        ],
    }


@router.post("/rooms/{room_code}/verify")
async def verify_result(
    room_code: str,
    server_seed: str,
    client_seed: str,
    nonce: int = 0,
    db: AsyncSession = Depends(get_db),
):
    """Verify provably fair result."""
    repo = RoomRepository(db)

    room = await repo.get_room(room_code)
    if not room:
        raise HTTPException(404, "Room not found")

    if room.status != RoomStatus.FINISHED:
        raise HTTPException(400, "Room not finished yet")

    actual_hash = ProvablyFairEngine.hash_server_seed(server_seed)
    if actual_hash != room.server_seed_hash:
        return {"valid": False, "reason": "Server seed does not match hash"}

    result = ProvablyFairEngine.generate_result(server_seed, client_seed, nonce)

    return {
        "valid": True,
        "computed_result": result,
        "server_seed_hash": actual_hash,
    }


@router.get("/stats/{user_id}")
async def get_user_stats(
    user_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get user PvP statistics."""
    repo = RoomRepository(db)
    stats = await repo.get_or_create_stats(user_id, user_id)

    return {
        "user_id": stats.user_id,
        "total_wins": stats.total_wins,
        "total_losses": stats.total_losses,
        "total_games": stats.total_games,
        "total_wagered_ton": str(stats.total_wagered_ton),
        "total_won_ton": str(stats.total_won_ton),
        "total_profit_ton": str(stats.total_profit_ton),
        "current_win_streak": stats.current_win_streak,
        "max_win_streak": stats.max_win_streak,
        "biggest_win_ton": str(stats.biggest_win_ton),
    }

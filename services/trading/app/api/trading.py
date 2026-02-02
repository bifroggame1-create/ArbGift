"""
Trading API Endpoints.

REST and WebSocket endpoints for crash/trading game.
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.database import get_db_session
from app.models.game import TradingGame, GameStatus
from app.models.bet import TradingBet, BetStatus, UserTradingStats
from app.websocket.manager import manager
from app.services.game_engine import TradingGameEngine

router = APIRouter(prefix="/api/trading", tags=["Trading"])

engine = TradingGameEngine()


# =============================================================================
# Schemas
# =============================================================================

class PlaceBetRequest(BaseModel):
    """Request to place a bet."""
    game_number: int
    user_id: int
    user_telegram_id: int
    user_name: str
    bet_amount_ton: Decimal = Field(ge=Decimal("0.1"), le=Decimal("100"))


class CashOutRequest(BaseModel):
    """Request to cash out."""
    bet_id: str


class GameResponse(BaseModel):
    """Game state response."""
    id: str
    game_number: int
    status: str
    current_multiplier: str
    server_seed_hash: str
    server_seed: Optional[str] = None
    crash_point: Optional[str] = None
    total_bets: int
    total_volume_ton: str


class BetResponse(BaseModel):
    """Bet response."""
    id: str
    game_number: int
    bet_amount_ton: str
    cash_out_multiplier: Optional[str] = None
    profit_ton: str
    status: str


class StatsResponse(BaseModel):
    """User trading statistics."""
    user_id: int
    total_games: int
    total_wins: int
    total_losses: int
    total_wagered_ton: str
    total_won_ton: str
    total_profit_ton: str
    biggest_win_ton: str
    highest_multiplier: str
    win_rate: str


# =============================================================================
# Endpoints
# =============================================================================

@router.get("/game/current", response_model=GameResponse)
async def get_current_game(
    session: AsyncSession = Depends(get_db_session),
):
    """Get current active or pending game."""
    result = await session.execute(
        select(TradingGame)
        .where(TradingGame.status.in_([GameStatus.PENDING, GameStatus.ACTIVE]))
        .order_by(desc(TradingGame.created_at))
        .limit(1)
    )
    game = result.scalar_one_or_none()

    if not game:
        raise HTTPException(404, "No active game")

    return GameResponse(
        id=game.id,
        game_number=game.game_number,
        status=game.status.value,
        current_multiplier=str(game.current_multiplier),
        server_seed_hash=game.server_seed_hash,
        server_seed=game.server_seed if game.status == GameStatus.CRASHED else None,
        crash_point=str(game.crash_point) if game.status == GameStatus.CRASHED else None,
        total_bets=game.total_bets,
        total_volume_ton=str(game.total_volume_ton),
    )


@router.post("/bet", response_model=BetResponse)
async def place_bet(
    req: PlaceBetRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Place a bet on the current game."""
    # Get current game
    result = await session.execute(
        select(TradingGame)
        .where(TradingGame.game_number == req.game_number)
        .where(TradingGame.status == GameStatus.PENDING)
    )
    game = result.scalar_one_or_none()

    if not game:
        raise HTTPException(400, "No active game to bet on")

    # Check if user already has bet in this game
    existing = await session.execute(
        select(TradingBet)
        .where(TradingBet.game_id == game.id)
        .where(TradingBet.user_id == req.user_id)
        .where(TradingBet.status == BetStatus.ACTIVE)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(400, "Already have active bet in this game")

    # Create bet
    bet = TradingBet(
        game_id=game.id,
        user_id=req.user_id,
        user_telegram_id=req.user_telegram_id,
        user_name=req.user_name,
        bet_amount_ton=req.bet_amount_ton,
        status=BetStatus.ACTIVE,
    )

    session.add(bet)

    # Update game stats
    game.total_bets += 1
    game.total_volume_ton += req.bet_amount_ton

    # Update user stats
    stats_result = await session.execute(
        select(UserTradingStats).where(UserTradingStats.user_id == req.user_id)
    )
    stats = stats_result.scalar_one_or_none()

    if not stats:
        stats = UserTradingStats(
            user_id=req.user_id,
            telegram_id=req.user_telegram_id,
            total_games=1,
            total_wagered_ton=req.bet_amount_ton,
        )
        session.add(stats)
    else:
        stats.total_games += 1
        stats.total_wagered_ton += req.bet_amount_ton

    await session.commit()
    await session.refresh(bet)

    # Broadcast new bet
    await manager.broadcast_new_bet(
        str(req.user_id),
        float(req.bet_amount_ton),
        game.game_number,
    )

    return BetResponse(
        id=bet.id,
        game_number=game.game_number,
        bet_amount_ton=str(bet.bet_amount_ton),
        cash_out_multiplier=None,
        profit_ton="0",
        status=bet.status.value,
    )


@router.post("/cashout", response_model=BetResponse)
async def cash_out(
    req: CashOutRequest,
    user_id: int,
    session: AsyncSession = Depends(get_db_session),
):
    """Cash out an active bet."""
    # Get bet
    result = await session.execute(
        select(TradingBet)
        .where(TradingBet.id == req.bet_id)
        .where(TradingBet.user_id == user_id)
        .where(TradingBet.status == BetStatus.ACTIVE)
    )
    bet = result.scalar_one_or_none()

    if not bet:
        raise HTTPException(404, "Bet not found or already cashed out")

    # Get game
    game_result = await session.execute(
        select(TradingGame).where(TradingGame.id == bet.game_id)
    )
    game = game_result.scalar_one_or_none()

    if game.status != GameStatus.ACTIVE:
        raise HTTPException(400, "Game is not active")

    # Cash out at current multiplier
    bet.cash_out_multiplier = game.current_multiplier
    bet.profit_ton = engine.calculate_profit(bet.bet_amount_ton, game.current_multiplier)
    bet.status = BetStatus.CASHED_OUT
    bet.cashed_out_at = datetime.utcnow()

    # Update user stats
    stats_result = await session.execute(
        select(UserTradingStats).where(UserTradingStats.user_id == user_id)
    )
    stats = stats_result.scalar_one_or_none()

    if stats:
        stats.total_wins += 1
        stats.total_won_ton += bet.profit_ton + bet.bet_amount_ton
        stats.total_profit_ton += bet.profit_ton

        if bet.profit_ton > stats.biggest_win_ton:
            stats.biggest_win_ton = bet.profit_ton

        if bet.cash_out_multiplier > stats.highest_multiplier:
            stats.highest_multiplier = bet.cash_out_multiplier

        stats.current_win_streak += 1
        if stats.current_win_streak > stats.max_win_streak:
            stats.max_win_streak = stats.current_win_streak

    await session.commit()

    # Broadcast cash out
    await manager.broadcast_cash_out(
        str(user_id),
        float(bet.cash_out_multiplier),
        float(bet.profit_ton),
    )

    return BetResponse(
        id=bet.id,
        game_number=game.game_number,
        bet_amount_ton=str(bet.bet_amount_ton),
        cash_out_multiplier=str(bet.cash_out_multiplier),
        profit_ton=str(bet.profit_ton),
        status=bet.status.value,
    )


@router.get("/history", response_model=List[GameResponse])
async def get_game_history(
    limit: int = 20,
    session: AsyncSession = Depends(get_db_session),
):
    """Get recent game history."""
    result = await session.execute(
        select(TradingGame)
        .where(TradingGame.status == GameStatus.CRASHED)
        .order_by(desc(TradingGame.created_at))
        .limit(limit)
    )
    games = result.scalars().all()

    return [
        GameResponse(
            id=game.id,
            game_number=game.game_number,
            status=game.status.value,
            current_multiplier=str(game.current_multiplier),
            server_seed_hash=game.server_seed_hash,
            server_seed=game.server_seed,
            crash_point=str(game.crash_point) if game.crash_point else None,
            total_bets=game.total_bets,
            total_volume_ton=str(game.total_volume_ton),
        )
        for game in games
    ]


@router.get("/stats/{user_id}", response_model=StatsResponse)
async def get_user_stats(
    user_id: int,
    session: AsyncSession = Depends(get_db_session),
):
    """Get user trading statistics."""
    result = await session.execute(
        select(UserTradingStats).where(UserTradingStats.user_id == user_id)
    )
    stats = result.scalar_one_or_none()

    if not stats:
        return StatsResponse(
            user_id=user_id,
            total_games=0,
            total_wins=0,
            total_losses=0,
            total_wagered_ton="0",
            total_won_ton="0",
            total_profit_ton="0",
            biggest_win_ton="0",
            highest_multiplier="0",
            win_rate="0",
        )

    return StatsResponse(
        user_id=stats.user_id,
        total_games=stats.total_games,
        total_wins=stats.total_wins,
        total_losses=stats.total_losses,
        total_wagered_ton=str(stats.total_wagered_ton),
        total_won_ton=str(stats.total_won_ton),
        total_profit_ton=str(stats.total_profit_ton),
        biggest_win_ton=str(stats.biggest_win_ton),
        highest_multiplier=str(stats.highest_multiplier),
        win_rate=str(round(stats.win_rate, 2)),
    )


@router.post("/verify/{game_id}")
async def verify_game(
    game_id: str,
    server_seed: str,
    session: AsyncSession = Depends(get_db_session),
):
    """Verify game was provably fair."""
    result = await session.execute(
        select(TradingGame).where(TradingGame.id == game_id)
    )
    game = result.scalar_one_or_none()

    if not game:
        raise HTTPException(404, "Game not found")

    if game.status != GameStatus.CRASHED:
        raise HTTPException(400, "Game not finished yet")

    # Verify seed hash
    actual_hash = engine.hash_server_seed(server_seed)
    if actual_hash != game.server_seed_hash:
        return {"valid": False, "reason": "Server seed does not match hash"}

    # Verify crash point
    valid = engine.verify_crash_point(
        server_seed,
        game.nonce,
        game.crash_point,
    )

    return {
        "valid": valid,
        "game_number": game.game_number,
        "crash_point": str(game.crash_point),
        "server_seed_hash": game.server_seed_hash,
        "nonce": game.nonce,
    }


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    user_id: Optional[str] = None,
):
    """WebSocket endpoint for real-time game updates."""
    await manager.connect(websocket, user_id)
    try:
        while True:
            # Keep connection alive
            data = await websocket.receive_text()
            # Echo for ping/pong
            await websocket.send_text(data)
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid

from ..models.game import TradingGame, GameStatus
from ..models.bet import Bet, BetStatus
from ..websocket.manager import manager
from ..services.game_loop import game_loop


router = APIRouter(prefix="/api/trading", tags=["trading"])


class PlaceBetRequest(BaseModel):
    game_number: int
    bet_amount: float


class CashOutRequest(BaseModel):
    bet_id: str


class GameResponse(BaseModel):
    id: str
    game_number: int
    status: str
    current_multiplier: float
    server_seed_hash: str
    server_seed: Optional[str]
    crash_point: Optional[float]
    total_bets: int
    total_volume: float


class BetResponse(BaseModel):
    id: str
    game_number: int
    bet_amount: float
    cash_out_multiplier: Optional[float]
    profit: float
    status: str


@router.get("/game/current", response_model=GameResponse)
async def get_current_game(session: AsyncSession = Depends()):
    """Get current active or pending game"""
    result = await session.execute(
        select(TradingGame)
        .where(TradingGame.status.in_([GameStatus.PENDING, GameStatus.ACTIVE]))
        .order_by(desc(TradingGame.created_at))
        .limit(1)
    )
    game = result.scalar_one_or_none()

    if not game:
        raise HTTPException(status_code=404, detail="No active game")

    return GameResponse(
        id=str(game.id),
        game_number=game.game_number,
        status=game.status.value,
        current_multiplier=game.current_multiplier,
        server_seed_hash=game.server_seed_hash,
        server_seed=game.server_seed if game.status == GameStatus.CRASHED else None,
        crash_point=game.crash_point if game.status == GameStatus.CRASHED else None,
        total_bets=game.total_bets,
        total_volume=game.total_volume
    )


@router.post("/bet", response_model=BetResponse)
async def place_bet(
    request: PlaceBetRequest,
    user_id: str,  # From auth middleware
    session: AsyncSession = Depends()
):
    """Place a bet on the current game"""
    # Get current game
    result = await session.execute(
        select(TradingGame)
        .where(TradingGame.game_number == request.game_number)
        .where(TradingGame.status == GameStatus.PENDING)
    )
    game = result.scalar_one_or_none()

    if not game:
        raise HTTPException(status_code=400, detail="No active game to bet on")

    if request.bet_amount <= 0:
        raise HTTPException(status_code=400, detail="Invalid bet amount")

    # Create bet
    bet = Bet(
        game_id=game.id,
        user_id=uuid.UUID(user_id),
        bet_amount=request.bet_amount,
        status=BetStatus.ACTIVE
    )

    session.add(bet)

    # Update game stats
    game.total_bets += 1
    game.total_volume += request.bet_amount

    await session.commit()
    await session.refresh(bet)

    # Broadcast new bet
    await manager.broadcast_new_bet(user_id, request.bet_amount, game.game_number)

    return BetResponse(
        id=str(bet.id),
        game_number=game.game_number,
        bet_amount=bet.bet_amount,
        cash_out_multiplier=None,
        profit=0.0,
        status=bet.status.value
    )


@router.post("/cashout", response_model=BetResponse)
async def cash_out(
    request: CashOutRequest,
    user_id: str,  # From auth middleware
    session: AsyncSession = Depends()
):
    """Cash out an active bet"""
    # Get bet
    result = await session.execute(
        select(Bet)
        .where(Bet.id == uuid.UUID(request.bet_id))
        .where(Bet.user_id == uuid.UUID(user_id))
        .where(Bet.status == BetStatus.ACTIVE)
    )
    bet = result.scalar_one_or_none()

    if not bet:
        raise HTTPException(status_code=404, detail="Bet not found or already cashed out")

    # Get game
    result = await session.execute(
        select(TradingGame).where(TradingGame.id == bet.game_id)
    )
    game = result.scalar_one_or_none()

    if game.status != GameStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="Game is not active")

    # Cash out at current multiplier
    bet.cash_out_multiplier = game.current_multiplier
    bet.profit = bet.bet_amount * game.current_multiplier - bet.bet_amount
    bet.status = BetStatus.CASHED_OUT
    bet.cashed_out_at = datetime.utcnow()

    await session.commit()

    # Broadcast cash out
    await manager.broadcast_cash_out(user_id, bet.cash_out_multiplier, bet.profit)

    return BetResponse(
        id=str(bet.id),
        game_number=game.game_number,
        bet_amount=bet.bet_amount,
        cash_out_multiplier=bet.cash_out_multiplier,
        profit=bet.profit,
        status=bet.status.value
    )


@router.get("/history", response_model=list[GameResponse])
async def get_game_history(
    limit: int = 20,
    session: AsyncSession = Depends()
):
    """Get recent game history"""
    result = await session.execute(
        select(TradingGame)
        .where(TradingGame.status == GameStatus.CRASHED)
        .order_by(desc(TradingGame.created_at))
        .limit(limit)
    )
    games = result.scalars().all()

    return [
        GameResponse(
            id=str(game.id),
            game_number=game.game_number,
            status=game.status.value,
            current_multiplier=game.current_multiplier,
            server_seed_hash=game.server_seed_hash,
            server_seed=game.server_seed,
            crash_point=game.crash_point,
            total_bets=game.total_bets,
            total_volume=game.total_volume
        )
        for game in games
    ]


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, user_id: Optional[str] = None):
    """WebSocket endpoint for real-time game updates"""
    await manager.connect(websocket, user_id)
    try:
        while True:
            # Keep connection alive
            data = await websocket.receive_text()
            # Echo for ping/pong
            await websocket.send_text(data)
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)

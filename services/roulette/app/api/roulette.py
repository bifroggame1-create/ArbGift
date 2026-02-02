"""
Roulette API endpoints.
"""
from decimal import Decimal
from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db_session
from app.models.game import RouletteGame, GameStatus
from app.models.bet import RouletteBet, BetType, BetStatus
from app.services.roulette_engine import RouletteEngine

router = APIRouter(prefix="/api/v1", tags=["roulette"])


# ============================================================
# SCHEMAS
# ============================================================

class BetRequest(BaseModel):
    """Request to place a bet."""
    bet_type: BetType
    bet_value: str = Field(..., description="Number(s) or selection")
    bet_amount_ton: Decimal = Field(..., gt=0)


class BetResponse(BaseModel):
    """Bet response."""
    id: str
    game_number: int
    bet_type: BetType
    bet_value: str
    bet_amount_ton: Decimal
    payout_multiplier: Decimal
    status: BetStatus
    created_at: datetime

    class Config:
        from_attributes = True


class GameResponse(BaseModel):
    """Game response."""
    id: int
    game_number: int
    status: GameStatus
    winning_number: Optional[int] = None
    winning_color: Optional[str] = None
    server_seed_hash: str
    server_seed: Optional[str] = None
    total_bets: int
    total_volume_ton: Decimal
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class SpinResultResponse(BaseModel):
    """Spin result response."""
    game_number: int
    winning_number: int
    winning_color: str
    server_seed: str
    your_bets: List[BetResponse]
    total_profit_ton: Decimal


class VerifyRequest(BaseModel):
    """Verification request."""
    server_seed: str
    client_seed: str
    nonce: int


class VerifyResponse(BaseModel):
    """Verification response."""
    valid: bool
    calculated_result: int
    calculated_color: str


# ============================================================
# GAME STATE (in-memory for now, replace with Redis/DB)
# ============================================================

current_game: Optional[RouletteGame] = None
game_counter = 1


# ============================================================
# ENDPOINTS
# ============================================================

@router.get("/game/current", response_model=GameResponse)
async def get_current_game(
    session: AsyncSession = Depends(get_db_session),
):
    """Get current game or create new one."""
    global current_game, game_counter
    
    # Get or create current game
    result = await session.execute(
        select(RouletteGame)
        .where(RouletteGame.status == GameStatus.PENDING)
        .order_by(RouletteGame.id.desc())
        .limit(1)
    )
    game = result.scalar_one_or_none()
    
    if not game:
        # Create new game
        server_seed = RouletteEngine.generate_server_seed()
        server_seed_hash = RouletteEngine.hash_seed(server_seed)
        
        game = RouletteGame(
            game_number=game_counter,
            status=GameStatus.PENDING,
            server_seed_hash=server_seed_hash,
            server_seed=server_seed,
            client_seed="default",
            nonce=game_counter,
        )
        session.add(game)
        await session.commit()
        await session.refresh(game)
        
        game_counter += 1
    
    # Hide server seed until game is complete
    response_seed = game.server_seed if game.status == GameStatus.COMPLETED else None
    
    return GameResponse(
        id=game.id,
        game_number=game.game_number,
        status=game.status,
        winning_number=game.winning_number,
        winning_color=game.winning_color,
        server_seed_hash=game.server_seed_hash,
        server_seed=response_seed,
        total_bets=game.total_bets,
        total_volume_ton=game.total_volume_ton or Decimal("0"),
        created_at=game.created_at,
        completed_at=game.completed_at,
    )


@router.post("/bet", response_model=BetResponse)
async def place_bet(
    bet: BetRequest,
    user_id: str = Query(..., description="Telegram user ID"),
    session: AsyncSession = Depends(get_db_session),
):
    """Place a bet on current game."""
    # Validate bet
    is_valid, error = RouletteEngine.validate_bet(
        bet.bet_type,
        bet.bet_value,
        bet.bet_amount_ton,
    )
    if not is_valid:
        raise HTTPException(status_code=400, detail=error)
    
    # Get current pending game
    result = await session.execute(
        select(RouletteGame)
        .where(RouletteGame.status == GameStatus.PENDING)
        .order_by(RouletteGame.id.desc())
        .limit(1)
    )
    game = result.scalar_one_or_none()
    
    if not game:
        raise HTTPException(status_code=400, detail="No active game")
    
    # Create bet
    payout_multiplier = RouletteEngine.get_payout_multiplier(bet.bet_type)
    
    new_bet = RouletteBet(
        game_id=game.id,
        user_id=user_id,
        bet_type=bet.bet_type,
        bet_value=bet.bet_value,
        bet_amount_ton=bet.bet_amount_ton,
        payout_multiplier=payout_multiplier,
        status=BetStatus.ACTIVE,
    )
    session.add(new_bet)
    
    # Update game stats
    game.total_bets += 1
    game.total_volume_ton = (game.total_volume_ton or Decimal("0")) + bet.bet_amount_ton
    
    await session.commit()
    await session.refresh(new_bet)
    
    return BetResponse(
        id=str(new_bet.id),
        game_number=game.game_number,
        bet_type=new_bet.bet_type,
        bet_value=new_bet.bet_value,
        bet_amount_ton=new_bet.bet_amount_ton,
        payout_multiplier=new_bet.payout_multiplier,
        status=new_bet.status,
        created_at=new_bet.created_at,
    )


@router.post("/spin", response_model=SpinResultResponse)
async def spin_wheel(
    user_id: str = Query(..., description="Telegram user ID"),
    session: AsyncSession = Depends(get_db_session),
):
    """Spin the wheel and get results for current game."""
    global game_counter
    
    # Get current pending game
    result = await session.execute(
        select(RouletteGame)
        .where(RouletteGame.status == GameStatus.PENDING)
        .order_by(RouletteGame.id.desc())
        .limit(1)
    )
    game = result.scalar_one_or_none()
    
    if not game:
        raise HTTPException(status_code=400, detail="No active game")
    
    if game.total_bets == 0:
        raise HTTPException(status_code=400, detail="No bets placed")
    
    # Generate result
    winning_number = RouletteEngine.generate_result(
        game.server_seed,
        game.client_seed or "default",
        game.nonce,
    )
    winning_color = RouletteEngine.get_color(winning_number)
    
    # Update game
    game.status = GameStatus.COMPLETED
    game.winning_number = winning_number
    game.winning_color = winning_color
    game.completed_at = datetime.utcnow()
    
    # Process all bets
    bets_result = await session.execute(
        select(RouletteBet).where(RouletteBet.game_id == game.id)
    )
    all_bets = bets_result.scalars().all()
    
    user_bets = []
    total_profit = Decimal("0")
    total_payout = Decimal("0")
    
    for bet in all_bets:
        won = RouletteEngine.check_bet_wins(
            bet.bet_type,
            bet.bet_value,
            winning_number,
        )
        
        if won:
            bet.status = BetStatus.WON
            bet.profit_ton = bet.bet_amount_ton * bet.payout_multiplier
            total_payout += bet.profit_ton + bet.bet_amount_ton
        else:
            bet.status = BetStatus.LOST
            bet.profit_ton = -bet.bet_amount_ton
        
        # Track user's bets
        if bet.user_id == user_id:
            user_bets.append(BetResponse(
                id=str(bet.id),
                game_number=game.game_number,
                bet_type=bet.bet_type,
                bet_value=bet.bet_value,
                bet_amount_ton=bet.bet_amount_ton,
                payout_multiplier=bet.payout_multiplier,
                status=bet.status,
                created_at=bet.created_at,
            ))
            total_profit += bet.profit_ton
    
    game.total_payout_ton = total_payout
    
    await session.commit()
    
    return SpinResultResponse(
        game_number=game.game_number,
        winning_number=winning_number,
        winning_color=winning_color,
        server_seed=game.server_seed,
        your_bets=user_bets,
        total_profit_ton=total_profit,
    )


@router.get("/history", response_model=List[GameResponse])
async def get_game_history(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """Get recent completed games."""
    result = await session.execute(
        select(RouletteGame)
        .where(RouletteGame.status == GameStatus.COMPLETED)
        .order_by(RouletteGame.id.desc())
        .limit(limit)
    )
    games = result.scalars().all()
    
    return [
        GameResponse(
            id=g.id,
            game_number=g.game_number,
            status=g.status,
            winning_number=g.winning_number,
            winning_color=g.winning_color,
            server_seed_hash=g.server_seed_hash,
            server_seed=g.server_seed,
            total_bets=g.total_bets,
            total_volume_ton=g.total_volume_ton or Decimal("0"),
            created_at=g.created_at,
            completed_at=g.completed_at,
        )
        for g in games
    ]


@router.post("/verify", response_model=VerifyResponse)
async def verify_result(request: VerifyRequest):
    """Verify a game result using provably fair algorithm."""
    calculated_result = RouletteEngine.generate_result(
        request.server_seed,
        request.client_seed,
        request.nonce,
    )
    calculated_color = RouletteEngine.get_color(calculated_result)
    
    return VerifyResponse(
        valid=True,
        calculated_result=calculated_result,
        calculated_color=calculated_color,
    )


@router.get("/bets/my", response_model=List[BetResponse])
async def get_my_bets(
    user_id: str = Query(..., description="Telegram user ID"),
    limit: int = Query(50, ge=1, le=200),
    session: AsyncSession = Depends(get_db_session),
):
    """Get user's bet history."""
    result = await session.execute(
        select(RouletteBet, RouletteGame.game_number)
        .join(RouletteGame, RouletteBet.game_id == RouletteGame.id)
        .where(RouletteBet.user_id == user_id)
        .order_by(RouletteBet.created_at.desc())
        .limit(limit)
    )
    rows = result.all()
    
    return [
        BetResponse(
            id=str(bet.id),
            game_number=game_number,
            bet_type=bet.bet_type,
            bet_value=bet.bet_value,
            bet_amount_ton=bet.bet_amount_ton,
            payout_multiplier=bet.payout_multiplier,
            status=bet.status,
            created_at=bet.created_at,
        )
        for bet, game_number in rows
    ]

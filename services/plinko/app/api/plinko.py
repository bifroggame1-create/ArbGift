"""
Plinko API endpoints — v2: Stars currency, multi-ball, risk levels, DB persistence.
"""
import hashlib
import secrets
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings, MULTIPLIER_SETS, VALID_RISK_LEVELS, VALID_ROW_COUNTS
from app.database import get_db_session
from app.models.drop import PlinkoDrop
from app.services.plinko_engine import PlinkoEngine

router = APIRouter(prefix="/api/v1", tags=["plinko"])

engine = PlinkoEngine()

# Nonce tracking per user (in-memory, should be Redis in production)
user_nonces: dict = {}


# ============================================================
# SCHEMAS
# ============================================================

class PlayRequest(BaseModel):
    bet_amount_stars: int = Field(..., gt=0)
    risk_level: str = Field("medium")
    row_count: int = Field(12)
    ball_count: int = Field(1, ge=1, le=10)
    client_seed: Optional[str] = None


class DropResult(BaseModel):
    id: str
    path: List[List[float]]
    landing_slot: int
    multiplier: float
    bet_amount: float
    payout: float
    profit: float
    server_seed_hash: str
    server_seed: str
    client_seed: str
    nonce: int
    risk_level: str
    row_count: int
    created_at: datetime


class PlayResponse(BaseModel):
    drops: List[DropResult]
    new_balance_stars: int
    total_payout: float
    total_profit: float


class ConfigResponse(BaseModel):
    multiplier_sets: Dict[str, Dict[str, List[float]]]
    min_bet_stars: int
    max_bet_stars: int
    max_balls_per_play: int
    valid_risk_levels: List[str]
    valid_row_counts: List[int]


class VerifyRequest(BaseModel):
    server_seed: str
    client_seed: str
    nonce: int
    bet_amount: float
    risk_level: str = "medium"
    row_count: int = 12


class VerifyResponse(BaseModel):
    valid: bool
    landing_slot: int
    multiplier: float
    path: List[List[float]]


class HistoryItem(BaseModel):
    id: str
    landing_slot: int
    multiplier: float
    bet_amount: float
    payout: float
    profit: float
    risk_level: str
    row_count: int
    created_at: datetime


# ============================================================
# ENDPOINTS
# ============================================================

@router.get("/config", response_model=ConfigResponse)
async def get_config():
    """Get full game configuration including all multiplier sets."""
    # Convert int keys to string for JSON serialization
    serializable = {}
    for risk, rows_dict in MULTIPLIER_SETS.items():
        serializable[risk] = {str(rows): mults for rows, mults in rows_dict.items()}

    return ConfigResponse(
        multiplier_sets=serializable,
        min_bet_stars=settings.MIN_BET_STARS,
        max_bet_stars=settings.MAX_BET_STARS,
        max_balls_per_play=settings.MAX_BALLS_PER_PLAY,
        valid_risk_levels=sorted(VALID_RISK_LEVELS),
        valid_row_counts=sorted(VALID_ROW_COUNTS),
    )


@router.post("/play", response_model=PlayResponse)
async def play_plinko(
    request: PlayRequest,
    user_id: str = Query(..., description="Telegram user ID"),
    session: AsyncSession = Depends(get_db_session),
):
    """Play plinko — drop one or more balls."""
    # Validate params
    if request.risk_level not in VALID_RISK_LEVELS:
        raise HTTPException(400, f"Invalid risk_level. Must be one of: {VALID_RISK_LEVELS}")
    if request.row_count not in VALID_ROW_COUNTS:
        raise HTTPException(400, f"Invalid row_count. Must be one of: {VALID_ROW_COUNTS}")
    if request.bet_amount_stars < settings.MIN_BET_STARS:
        raise HTTPException(400, f"Minimum bet is {settings.MIN_BET_STARS} Stars")
    if request.bet_amount_stars > settings.MAX_BET_STARS:
        raise HTTPException(400, f"Maximum bet is {settings.MAX_BET_STARS} Stars")
    if request.ball_count > settings.MAX_BALLS_PER_PLAY:
        raise HTTPException(400, f"Maximum {settings.MAX_BALLS_PER_PLAY} balls per play")

    total_cost = request.bet_amount_stars * request.ball_count
    # TODO: check user balance from main app DB and deduct

    client_seed = request.client_seed or secrets.token_hex(16)

    # Get/increment nonce
    if user_id not in user_nonces:
        user_nonces[user_id] = 0

    drops: List[DropResult] = []
    total_payout = 0.0
    total_profit = 0.0

    for i in range(request.ball_count):
        nonce = user_nonces[user_id]
        user_nonces[user_id] += 1

        server_seed = secrets.token_hex(32)
        server_seed_hash = hashlib.sha256(server_seed.encode()).hexdigest()

        result = engine.generate_drop(
            server_seed=server_seed,
            client_seed=client_seed,
            nonce=nonce,
            bet_amount=float(request.bet_amount_stars),
            risk_level=request.risk_level,
            row_count=request.row_count,
        )

        drop_id = str(uuid.uuid4())

        # Persist to DB
        db_drop = PlinkoDrop(
            id=uuid.UUID(drop_id),
            user_id=user_id,
            risk_level=request.risk_level,
            row_count=request.row_count,
            currency="stars",
            bet_amount=float(request.bet_amount_stars),
            landing_slot=result["landing_slot"],
            multiplier=result["multiplier"],
            payout=result["payout"],
            profit=result["profit"],
            path=result["path"],
            server_seed_hash=server_seed_hash,
            server_seed=server_seed,
            client_seed=client_seed,
            nonce=nonce,
        )
        session.add(db_drop)

        drop_result = DropResult(
            id=drop_id,
            path=result["path"],
            landing_slot=result["landing_slot"],
            multiplier=result["multiplier"],
            bet_amount=float(request.bet_amount_stars),
            payout=result["payout"],
            profit=result["profit"],
            server_seed_hash=server_seed_hash,
            server_seed=server_seed,
            client_seed=client_seed,
            nonce=nonce,
            risk_level=request.risk_level,
            row_count=request.row_count,
            created_at=datetime.utcnow(),
        )
        drops.append(drop_result)
        total_payout += result["payout"]
        total_profit += result["profit"]

    await session.commit()

    return PlayResponse(
        drops=drops,
        new_balance_stars=0,  # TODO: return actual balance after deduction
        total_payout=round(total_payout, 2),
        total_profit=round(total_profit, 2),
    )


@router.post("/verify", response_model=VerifyResponse)
async def verify_drop(request: VerifyRequest):
    """Verify a drop result is provably fair."""
    try:
        result = engine.generate_drop(
            server_seed=request.server_seed,
            client_seed=request.client_seed,
            nonce=request.nonce,
            bet_amount=request.bet_amount,
            risk_level=request.risk_level,
            row_count=request.row_count,
        )
    except ValueError as e:
        raise HTTPException(400, str(e))

    return VerifyResponse(
        valid=True,
        landing_slot=result["landing_slot"],
        multiplier=result["multiplier"],
        path=result["path"],
    )


@router.get("/history", response_model=List[HistoryItem])
async def get_history(
    user_id: str = Query(..., description="Telegram user ID"),
    limit: int = Query(50, ge=1, le=200),
    session: AsyncSession = Depends(get_db_session),
):
    """Get user's drop history."""
    stmt = (
        select(PlinkoDrop)
        .where(PlinkoDrop.user_id == user_id)
        .order_by(desc(PlinkoDrop.created_at))
        .limit(limit)
    )
    result = await session.execute(stmt)
    rows = result.scalars().all()

    return [
        HistoryItem(
            id=str(row.id),
            landing_slot=row.landing_slot,
            multiplier=row.multiplier,
            bet_amount=row.bet_amount,
            payout=row.payout,
            profit=row.profit,
            risk_level=row.risk_level,
            row_count=row.row_count,
            created_at=row.created_at,
        )
        for row in rows
    ]


@router.get("/stats")
async def get_stats(
    user_id: str = Query(..., description="Telegram user ID"),
    session: AsyncSession = Depends(get_db_session),
):
    """Get user's plinko statistics."""
    from sqlalchemy import func

    stmt = select(
        func.count(PlinkoDrop.id).label("total_drops"),
        func.coalesce(func.sum(PlinkoDrop.bet_amount), 0).label("total_wagered"),
        func.coalesce(func.sum(PlinkoDrop.payout), 0).label("total_won"),
        func.coalesce(func.sum(PlinkoDrop.profit), 0).label("total_profit"),
        func.coalesce(func.max(PlinkoDrop.payout), 0).label("biggest_win"),
        func.coalesce(func.max(PlinkoDrop.multiplier), 0).label("biggest_multiplier"),
    ).where(PlinkoDrop.user_id == user_id)

    result = await session.execute(stmt)
    row = result.one()

    return {
        "total_drops": row.total_drops,
        "total_wagered_stars": round(float(row.total_wagered), 2),
        "total_won_stars": round(float(row.total_won), 2),
        "total_profit_stars": round(float(row.total_profit), 2),
        "biggest_win_stars": round(float(row.biggest_win), 2),
        "biggest_multiplier": round(float(row.biggest_multiplier), 2),
    }

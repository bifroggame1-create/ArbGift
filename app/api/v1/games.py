"""
Games API endpoints.

Handles game plays with user balance management.
"""
import logging
import hashlib
import secrets
import uuid
from decimal import Decimal
from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Header
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.models.user import User
from app.services.plinko_engine import PlinkoEngine

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize Plinko engine
plinko_engine = PlinkoEngine()

# Nonce tracking per user (in-memory, should be Redis in production)
user_nonces: dict = {}


# ============================================================
# SCHEMAS
# ============================================================

class PlinkoPlayRequest(BaseModel):
    """Plinko play request."""
    bet_amount_stars: int = Field(..., gt=0, description="Bet amount in Stars")
    risk_level: str = Field(..., pattern="^(low|medium|high)$")
    row_count: int = Field(..., description="Number of rows (8, 12, or 16)")
    ball_count: int = Field(1, ge=1, le=10, description="Number of balls to drop")
    client_seed: Optional[str] = None


class DropResult(BaseModel):
    """Single ball drop result."""
    id: str
    path: List[List[float]]
    landing_slot: int
    multiplier: float
    bet_amount: int
    payout: int
    profit: int
    server_seed_hash: str
    server_seed: str
    client_seed: str
    nonce: int
    risk_level: str
    row_count: int
    created_at: str


class PlinkoPlayResponse(BaseModel):
    """Plinko play response."""
    drops: List[DropResult]
    new_balance_stars: int
    total_payout: int
    total_profit: int


# ============================================================
# HELPERS
# ============================================================

async def get_user_by_telegram_init_data(
    session: AsyncSession,
    init_data: str
) -> Optional[User]:
    """
    Get user from Telegram init data.

    For now, we'll parse the user ID from init data.
    In production, you should validate the init data signature.
    """
    # TODO: Implement proper Telegram WebApp init data validation
    # For now, just extract user_id from query string
    try:
        from urllib.parse import parse_qs
        params = parse_qs(init_data)

        # Try to get user from 'user' parameter (JSON)
        if 'user' in params:
            import json
            user_data = json.loads(params['user'][0])
            telegram_id = user_data.get('id')
        else:
            # Fallback: try to find id parameter
            telegram_id = params.get('id', [None])[0]

        if not telegram_id:
            return None

        from sqlalchemy import select
        result = await session.execute(
            select(User).where(User.telegram_id == int(telegram_id))
        )
        return result.scalar_one_or_none()
    except Exception as e:
        logger.error(f"Failed to parse init data: {e}")
        return None


# ============================================================
# ENDPOINTS
# ============================================================

@router.get("/games/plinko/config")
async def get_plinko_config():
    """
    Get Plinko game configuration.

    Returns multiplier sets, valid risk levels, row counts, and bet limits.
    """
    from app.config import MULTIPLIER_SETS, VALID_RISK_LEVELS, VALID_ROW_COUNTS

    return {
        "multiplier_sets": MULTIPLIER_SETS,
        "valid_risk_levels": list(VALID_RISK_LEVELS),
        "valid_row_counts": list(VALID_ROW_COUNTS),
        "min_bet_stars": 10,
        "max_bet_stars": 10000,
        "max_balls_per_play": 10,
    }


@router.post("/games/plinko/play", response_model=PlinkoPlayResponse)
async def play_plinko(
    request: PlinkoPlayRequest,
    x_telegram_init_data: str = Header(..., alias="X-Telegram-Init-Data"),
    session: AsyncSession = Depends(get_db_session),
):
    """
    Play Plinko game - integrated version (no external service).

    1. Validates user and balance
    2. Deducts bet amount
    3. Generates drops using local Plinko engine
    4. Updates user balance with payout
    5. Updates user stats
    """
    # Get user from init data
    user = await get_user_by_telegram_init_data(session, x_telegram_init_data)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # Calculate total cost
    total_cost = request.bet_amount_stars * request.ball_count

    # Check balance
    if user.balance_stars < total_cost:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient balance. Required: {total_cost}, Available: {user.balance_stars}"
        )

    # Deduct bet amount
    user.balance_stars -= total_cost

    # Generate drops using local engine
    client_seed = request.client_seed or secrets.token_hex(16)
    user_id = str(user.telegram_id)

    # Get/increment nonce
    if user_id not in user_nonces:
        user_nonces[user_id] = 0

    drops: List[DropResult] = []
    total_payout = 0
    total_profit = 0

    try:
        for i in range(request.ball_count):
            nonce = user_nonces[user_id]
            user_nonces[user_id] += 1

            server_seed = secrets.token_hex(32)
            server_seed_hash = hashlib.sha256(server_seed.encode()).hexdigest()

            result = plinko_engine.generate_drop(
                server_seed=server_seed,
                client_seed=client_seed,
                nonce=nonce,
                bet_amount=float(request.bet_amount_stars),
                risk_level=request.risk_level,
                row_count=request.row_count,
            )

            drop_id = str(uuid.uuid4())

            drop_result = DropResult(
                id=drop_id,
                path=result["path"],
                landing_slot=result["landing_slot"],
                multiplier=result["multiplier"],
                bet_amount=request.bet_amount_stars,
                payout=int(result["payout"]),
                profit=int(result["profit"]),
                server_seed_hash=server_seed_hash,
                server_seed=server_seed,
                client_seed=client_seed,
                nonce=nonce,
                risk_level=request.risk_level,
                row_count=request.row_count,
                created_at=datetime.utcnow().isoformat(),
            )
            drops.append(drop_result)
            total_payout += int(result["payout"])
            total_profit += int(result["profit"])

    except Exception as e:
        # Refund on error
        user.balance_stars += total_cost
        await session.commit()
        logger.error(f"Plinko engine error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Game engine error: {str(e)}")

    # Add payout to balance
    user.balance_stars += total_payout

    # Update user stats
    user.games_played += request.ball_count
    user.total_wagered_ton += Decimal(total_cost) / Decimal(1000)  # Convert stars to TON equivalent

    if total_profit > 0:
        user.games_won += 1
        user.total_won_ton += Decimal(total_payout) / Decimal(1000)
        user.current_win_streak += 1
        if user.current_win_streak > user.best_win_streak:
            user.best_win_streak = user.current_win_streak

        if Decimal(total_profit) / Decimal(1000) > user.biggest_win_ton:
            user.biggest_win_ton = Decimal(total_profit) / Decimal(1000)
    else:
        user.total_lost_ton += Decimal(abs(total_profit)) / Decimal(1000)
        user.current_win_streak = 0

    user.net_profit_ton = user.total_won_ton - user.total_lost_ton
    user.last_seen_at = datetime.utcnow()

    await session.commit()
    await session.refresh(user)

    logger.info(
        f"Plinko play: user={user.telegram_id}, bet={total_cost}, "
        f"payout={total_payout}, profit={total_profit}, new_balance={user.balance_stars}"
    )

    return PlinkoPlayResponse(
        drops=drops,
        new_balance_stars=user.balance_stars,
        total_payout=total_payout,
        total_profit=total_profit,
    )

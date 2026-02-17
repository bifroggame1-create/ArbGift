"""
Games API endpoints.

Handles game plays with user balance management.
"""
import logging
import httpx
from decimal import Decimal
from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Header
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.models.user import User
from app.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()


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
    path: List[List[int]]
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

@router.post("/games/plinko/play", response_model=PlinkoPlayResponse)
async def play_plinko(
    request: PlinkoPlayRequest,
    x_telegram_init_data: str = Header(..., alias="X-Telegram-Init-Data"),
    session: AsyncSession = Depends(get_db_session),
):
    """
    Play Plinko game.

    1. Validates user and balance
    2. Deducts bet amount
    3. Calls Plinko service for game logic
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

    # Call Plinko service
    plinko_url = getattr(settings, 'PLINKO_SERVICE_URL', 'http://localhost:8001')

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{plinko_url}/api/v1/play",
                params={
                    "user_id": str(user.telegram_id),
                },
                json={
                    "bet_amount_stars": request.bet_amount_stars,
                    "risk_level": request.risk_level,
                    "row_count": request.row_count,
                    "ball_count": request.ball_count,
                    "client_seed": request.client_seed or "",
                }
            )
            response.raise_for_status()
            plinko_result = response.json()
    except httpx.HTTPError as e:
        # Refund on error
        user.balance_stars += total_cost
        await session.commit()
        logger.error(f"Plinko service error: {e}")
        raise HTTPException(status_code=503, detail="Game service unavailable")

    # Parse drops
    drops = plinko_result.get("drops", [])
    total_payout = sum(drop.get("payout", 0) for drop in drops)
    total_profit = total_payout - total_cost

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
        drops=[DropResult(**drop) for drop in drops],
        new_balance_stars=user.balance_stars,
        total_payout=total_payout,
        total_profit=total_profit,
    )

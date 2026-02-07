"""
Referral system API endpoints.

Provides REST API for:
- Viewing referrals and earnings
- Claiming referral rewards
- Referral statistics and leaderboards
"""
import logging
from decimal import Decimal
from datetime import datetime
from typing import Optional, List

from fastapi import APIRouter, Depends, Query, HTTPException, Header
from pydantic import BaseModel, Field
from sqlalchemy import select, func, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.models.user import User
from app.models.referral import Referral, ReferralReward, ReferralTier

logger = logging.getLogger(__name__)
router = APIRouter()


# ============================================================
# SCHEMAS
# ============================================================

class ReferredUserSchema(BaseModel):
    """Referred user info."""
    id: int
    telegram_id: int
    username: Optional[str]
    display_name: str
    level: int
    is_active: bool
    registered_at: datetime


class ReferralSchema(BaseModel):
    """Referral relationship."""
    id: int
    referred_user: ReferredUserSchema
    commission_percent: Decimal
    total_earned_ton: Decimal
    total_commission_paid_ton: Decimal
    referral_activities_count: int
    is_active: bool
    last_activity_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class ReferralRewardSchema(BaseModel):
    """Referral reward payment."""
    id: int
    amount_ton: Decimal
    source_type: str
    source_amount_ton: Decimal
    created_at: datetime

    class Config:
        from_attributes = True


class ReferralStatsSchema(BaseModel):
    """Referral statistics."""
    # Counts
    total_referrals: int
    active_referrals: int
    inactive_referrals: int

    # Tier info
    current_tier: str
    current_commission_percent: Decimal
    next_tier: Optional[str]
    referrals_to_next_tier: int

    # Earnings
    total_earned_ton: Decimal
    total_commission_paid_ton: Decimal
    pending_rewards_ton: Decimal

    # Activity
    total_activities: int
    last_reward_at: Optional[datetime]


class ReferralListResponse(BaseModel):
    """Paginated referral list."""
    total: int
    active: int
    inactive: int
    referrals: List[ReferralSchema]


class ReferralLeaderboardEntry(BaseModel):
    """Leaderboard entry."""
    rank: int
    user_id: int
    username: Optional[str]
    display_name: str
    referrals_count: int
    total_earned_ton: Decimal


# ============================================================
# HELPERS
# ============================================================

def get_tier_info(referrals_count: int) -> tuple[str, Decimal, Optional[str], int]:
    """
    Get tier information based on referrals count.

    Returns: (current_tier, commission_percent, next_tier, referrals_to_next)
    """
    if referrals_count >= 201:
        return ("platinum", Decimal("10.0"), None, 0)
    elif referrals_count >= 51:
        return ("gold", Decimal("7.0"), "platinum", 201 - referrals_count)
    elif referrals_count >= 11:
        return ("silver", Decimal("5.0"), "gold", 51 - referrals_count)
    else:
        return ("bronze", Decimal("3.0"), "silver", 11 - referrals_count)


async def get_user_by_telegram_id(
    session: AsyncSession,
    telegram_id: int
) -> Optional[User]:
    """Get user by Telegram ID."""
    result = await session.execute(
        select(User).where(User.telegram_id == telegram_id)
    )
    return result.scalar_one_or_none()


# ============================================================
# ENDPOINTS
# ============================================================

@router.get("/my-referrals", response_model=ReferralListResponse)
async def get_my_referrals(
    telegram_id: int = Header(..., alias="X-Telegram-User-Id"),
    status: Optional[str] = Query(None, regex="^(active|inactive)$"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_db_session),
):
    """
    Get my referrals.

    Returns list of users referred by current user.
    """
    user = await get_user_by_telegram_id(session, telegram_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Build query
    query = (
        select(Referral)
        .where(Referral.referrer_id == user.id)
    )

    if status == "active":
        query = query.where(Referral.is_active == True)
    elif status == "inactive":
        query = query.where(Referral.is_active == False)

    # Get total count
    count_result = await session.execute(
        select(func.count()).select_from(query.subquery())
    )
    total = count_result.scalar()

    # Get active/inactive counts
    active_result = await session.execute(
        select(func.count())
        .select_from(Referral)
        .where(and_(Referral.referrer_id == user.id, Referral.is_active == True))
    )
    active = active_result.scalar()

    # Get paginated results
    query = query.order_by(desc(Referral.created_at)).limit(limit).offset(offset)
    result = await session.execute(query)
    referrals = result.scalars().all()

    # Enrich with user data
    enriched_referrals = []
    for referral in referrals:
        referred_user = await session.get(User, referral.referred_id)
        if referred_user:
            referral_data = {
                **referral.__dict__,
                "referred_user": ReferredUserSchema(
                    id=referred_user.id,
                    telegram_id=referred_user.telegram_id,
                    username=referred_user.username,
                    display_name=referred_user.display_name,
                    level=referred_user.level,
                    is_active=referred_user.is_active,
                    registered_at=referred_user.created_at,
                )
            }
            enriched_referrals.append(referral_data)

    return ReferralListResponse(
        total=total,
        active=active,
        inactive=total - active,
        referrals=enriched_referrals,
    )


@router.get("/stats", response_model=ReferralStatsSchema)
async def get_referral_stats(
    telegram_id: int = Header(..., alias="X-Telegram-User-Id"),
    session: AsyncSession = Depends(get_db_session),
):
    """
    Get referral statistics.

    Returns comprehensive stats about referral performance.
    """
    user = await get_user_by_telegram_id(session, telegram_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get referral counts
    total_result = await session.execute(
        select(func.count())
        .select_from(Referral)
        .where(Referral.referrer_id == user.id)
    )
    total_referrals = total_result.scalar()

    active_result = await session.execute(
        select(func.count())
        .select_from(Referral)
        .where(and_(Referral.referrer_id == user.id, Referral.is_active == True))
    )
    active_referrals = active_result.scalar()

    # Get tier info
    current_tier, commission_percent, next_tier, to_next = get_tier_info(total_referrals)

    # Get earnings
    earnings_result = await session.execute(
        select(
            func.sum(Referral.total_earned_ton),
            func.sum(Referral.total_commission_paid_ton),
        )
        .where(Referral.referrer_id == user.id)
    )
    earnings_row = earnings_result.first()
    total_earned = earnings_row[0] or Decimal("0")
    total_paid = earnings_row[1] or Decimal("0")
    pending = total_earned - total_paid

    # Get activities count
    activities_result = await session.execute(
        select(func.sum(Referral.referral_activities_count))
        .where(Referral.referrer_id == user.id)
    )
    total_activities = activities_result.scalar() or 0

    # Get last reward time
    last_reward_result = await session.execute(
        select(ReferralReward.created_at)
        .where(ReferralReward.recipient_id == user.id)
        .order_by(desc(ReferralReward.created_at))
        .limit(1)
    )
    last_reward_at = last_reward_result.scalar_one_or_none()

    return ReferralStatsSchema(
        total_referrals=total_referrals,
        active_referrals=active_referrals,
        inactive_referrals=total_referrals - active_referrals,
        current_tier=current_tier,
        current_commission_percent=commission_percent,
        next_tier=next_tier,
        referrals_to_next_tier=to_next,
        total_earned_ton=total_earned,
        total_commission_paid_ton=total_paid,
        pending_rewards_ton=pending,
        total_activities=total_activities,
        last_reward_at=last_reward_at,
    )


@router.get("/rewards", response_model=List[ReferralRewardSchema])
async def get_referral_rewards(
    telegram_id: int = Header(..., alias="X-Telegram-User-Id"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_db_session),
):
    """
    Get referral reward history.

    Returns list of all referral rewards received.
    """
    user = await get_user_by_telegram_id(session, telegram_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    result = await session.execute(
        select(ReferralReward)
        .where(ReferralReward.recipient_id == user.id)
        .order_by(desc(ReferralReward.created_at))
        .limit(limit)
        .offset(offset)
    )

    rewards = result.scalars().all()

    return rewards


@router.post("/claim")
async def claim_referral_rewards(
    telegram_id: int = Header(..., alias="X-Telegram-User-Id"),
    session: AsyncSession = Depends(get_db_session),
):
    """
    Claim pending referral rewards.

    Transfers all pending rewards to user's balance.
    """
    user = await get_user_by_telegram_id(session, telegram_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Calculate pending rewards
    result = await session.execute(
        select(
            func.sum(Referral.total_earned_ton),
            func.sum(Referral.total_commission_paid_ton),
        )
        .where(Referral.referrer_id == user.id)
    )
    row = result.first()
    total_earned = row[0] or Decimal("0")
    total_paid = row[1] or Decimal("0")
    pending = total_earned - total_paid

    if pending <= 0:
        raise HTTPException(status_code=400, detail="No pending rewards")

    # Transfer to user balance
    user.balance_ton += pending
    user.referral_earnings_ton += pending

    # Update all referrals as paid
    referrals_result = await session.execute(
        select(Referral).where(Referral.referrer_id == user.id)
    )
    referrals = referrals_result.scalars().all()

    for referral in referrals:
        unpaid = referral.total_earned_ton - referral.total_commission_paid_ton
        if unpaid > 0:
            referral.total_commission_paid_ton = referral.total_earned_ton

    await session.commit()

    logger.info(f"Claimed referral rewards: {user.telegram_id} - {pending} TON")

    return {
        "success": True,
        "claimed_amount_ton": pending,
        "new_balance_ton": user.balance_ton,
    }


@router.get("/leaderboard", response_model=List[ReferralLeaderboardEntry])
async def get_referral_leaderboard(
    limit: int = Query(100, ge=1, le=500),
    session: AsyncSession = Depends(get_db_session),
):
    """
    Get referral leaderboard.

    Top users by referral count and earnings.
    """
    result = await session.execute(
        select(
            User.id,
            User.username,
            User.first_name,
            User.referrals_count,
            User.referral_earnings_ton,
        )
        .where(User.referrals_count > 0)
        .order_by(desc(User.referrals_count))
        .limit(limit)
    )

    entries = []
    for rank, row in enumerate(result.all(), start=1):
        display_name = row.username or row.first_name or f"User{row.id}"
        entries.append(
            ReferralLeaderboardEntry(
                rank=rank,
                user_id=row.id,
                username=row.username,
                display_name=display_name,
                referrals_count=row.referrals_count,
                total_earned_ton=row.referral_earnings_ton,
            )
        )

    return entries

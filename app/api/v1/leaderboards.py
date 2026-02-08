"""
Leaderboards API endpoints.

Provides REST API for:
- Global leaderboards (all-time, weekly, monthly, daily)
- Multiple categories (profit, wins, wagered, staking, referrals)
- User rankings and position tracking
"""
import logging
from decimal import Decimal
from datetime import datetime
from typing import Optional, List

from fastapi import APIRouter, Depends, Query, HTTPException, Header
from pydantic import BaseModel, Field
from sqlalchemy import select, func, and_, or_, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.models.user import User
from app.models.leaderboard import LeaderboardEntry, LeaderboardType, LeaderboardCategory

logger = logging.getLogger(__name__)
router = APIRouter()


# ============================================================
# SCHEMAS
# ============================================================

class LeaderboardEntrySchema(BaseModel):
    """Leaderboard entry."""
    rank: int
    previous_rank: Optional[int]
    rank_change: int

    # User info
    user_id: int
    telegram_id: int
    username: Optional[str]
    display_name: str

    # Score
    score_value: Decimal

    # Period (for weekly/monthly/daily)
    period_start: Optional[datetime]
    period_end: Optional[datetime]

    updated_at: datetime

    class Config:
        from_attributes = True


class LeaderboardResponse(BaseModel):
    """Leaderboard response."""
    leaderboard_type: str
    category: str
    total_entries: int
    entries: List[LeaderboardEntrySchema]
    my_rank: Optional[int]


class UserRankingSchema(BaseModel):
    """User's ranking across all leaderboards."""
    leaderboard_type: str
    category: str
    rank: int
    previous_rank: Optional[int]
    rank_change: int
    score_value: Decimal


# ============================================================
# HELPERS
# ============================================================

async def get_user_by_telegram_id(
    session: AsyncSession,
    telegram_id: int
) -> Optional[User]:
    """Get user by Telegram ID."""
    result = await session.execute(
        select(User).where(User.telegram_id == telegram_id)
    )
    return result.scalar_one_or_none()


def get_display_name(username: Optional[str], user_id: int) -> str:
    """Get display name for user."""
    return username or f"User{user_id}"


# ============================================================
# ENDPOINTS
# ============================================================

@router.get("/", response_model=LeaderboardResponse)
async def get_leaderboard(
    type: str = Query("WEEKLY", pattern="^(ALL_TIME|WEEKLY|MONTHLY|DAILY)$"),
    category: str = Query("TOTAL_PROFIT", pattern="^(TOTAL_PROFIT|BIGGEST_WIN|WIN_STREAK|TOTAL_WAGERED|STAKING_REWARDS|REFERRAL_EARNINGS)$"),
    limit: int = Query(100, ge=1, le=500),
    telegram_id: Optional[int] = Header(None, alias="X-Telegram-User-Id"),
    session: AsyncSession = Depends(get_db_session),
):
    """
    Get leaderboard.

    Types:
    - ALL_TIME: All-time rankings
    - WEEKLY: This week's rankings
    - MONTHLY: This month's rankings
    - DAILY: Today's rankings

    Categories:
    - TOTAL_PROFIT: Top earners (total_won - total_lost)
    - BIGGEST_WIN: Biggest single win
    - WIN_STREAK: Best winning streak
    - TOTAL_WAGERED: Most wagered
    - STAKING_REWARDS: Most staking rewards earned
    - REFERRAL_EARNINGS: Most referral earnings
    """
    # Parse enums
    lb_type = LeaderboardType(type)
    lb_category = LeaderboardCategory(category)

    # Get leaderboard entries
    result = await session.execute(
        select(LeaderboardEntry)
        .where(and_(
            LeaderboardEntry.leaderboard_type == lb_type,
            LeaderboardEntry.category == lb_category,
        ))
        .order_by(LeaderboardEntry.rank)
        .limit(limit)
    )
    entries = result.scalars().all()

    # Get total count
    count_result = await session.execute(
        select(func.count())
        .select_from(LeaderboardEntry)
        .where(and_(
            LeaderboardEntry.leaderboard_type == lb_type,
            LeaderboardEntry.category == lb_category,
        ))
    )
    total = count_result.scalar()

    # Enrich with display names and rank changes
    enriched_entries = []
    for entry in entries:
        entry_data = LeaderboardEntrySchema(
            rank=entry.rank,
            previous_rank=entry.previous_rank,
            rank_change=entry.rank_change,
            user_id=entry.user_id,
            telegram_id=entry.telegram_id,
            username=entry.username,
            display_name=get_display_name(entry.username, entry.user_id),
            score_value=entry.score_value,
            period_start=entry.period_start,
            period_end=entry.period_end,
            updated_at=entry.updated_at,
        )
        enriched_entries.append(entry_data)

    # Get user's rank if authenticated
    my_rank = None
    if telegram_id:
        user = await get_user_by_telegram_id(session, telegram_id)
        if user:
            my_rank_result = await session.execute(
                select(LeaderboardEntry.rank)
                .where(and_(
                    LeaderboardEntry.user_id == user.id,
                    LeaderboardEntry.leaderboard_type == lb_type,
                    LeaderboardEntry.category == lb_category,
                ))
            )
            my_rank = my_rank_result.scalar_one_or_none()

    return LeaderboardResponse(
        leaderboard_type=type,
        category=category,
        total_entries=total,
        entries=enriched_entries,
        my_rank=my_rank,
    )


@router.get("/my-rankings", response_model=List[UserRankingSchema])
async def get_my_rankings(
    telegram_id: int = Header(..., alias="X-Telegram-User-Id"),
    type: Optional[str] = Query(None, pattern="^(ALL_TIME|WEEKLY|MONTHLY|DAILY)$"),
    session: AsyncSession = Depends(get_db_session),
):
    """
    Get my rankings across all leaderboards.

    Returns user's position in all leaderboard categories.
    Optionally filter by leaderboard type.
    """
    user = await get_user_by_telegram_id(session, telegram_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Build query
    query = select(LeaderboardEntry).where(LeaderboardEntry.user_id == user.id)

    if type:
        lb_type = LeaderboardType(type)
        query = query.where(LeaderboardEntry.leaderboard_type == lb_type)

    # Get all rankings
    result = await session.execute(query.order_by(LeaderboardEntry.rank))
    entries = result.scalars().all()

    # Convert to schema
    rankings = []
    for entry in entries:
        rankings.append(
            UserRankingSchema(
                leaderboard_type=entry.leaderboard_type.value,
                category=entry.category.value,
                rank=entry.rank,
                previous_rank=entry.previous_rank,
                rank_change=entry.rank_change,
                score_value=entry.score_value,
            )
        )

    return rankings


@router.get("/top-gainers", response_model=List[LeaderboardEntrySchema])
async def get_top_gainers(
    limit: int = Query(10, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """
    Get top gainers (biggest rank improvements).

    Returns users who improved their rank the most recently.
    """
    result = await session.execute(
        select(LeaderboardEntry)
        .where(and_(
            LeaderboardEntry.previous_rank.is_not(None),
            LeaderboardEntry.leaderboard_type == LeaderboardType.WEEKLY,
            LeaderboardEntry.category == LeaderboardCategory.TOTAL_PROFIT,
        ))
        .order_by(desc(LeaderboardEntry.previous_rank - LeaderboardEntry.rank))
        .limit(limit)
    )
    entries = result.scalars().all()

    # Enrich
    enriched = []
    for entry in entries:
        enriched.append(
            LeaderboardEntrySchema(
                rank=entry.rank,
                previous_rank=entry.previous_rank,
                rank_change=entry.rank_change,
                user_id=entry.user_id,
                telegram_id=entry.telegram_id,
                username=entry.username,
                display_name=get_display_name(entry.username, entry.user_id),
                score_value=entry.score_value,
                period_start=entry.period_start,
                period_end=entry.period_end,
                updated_at=entry.updated_at,
            )
        )

    return enriched


@router.post("/update/{telegram_id}")
async def update_leaderboard_entry(
    telegram_id: int,
    admin_key: str = Header(..., alias="X-Admin-Key"),
    session: AsyncSession = Depends(get_db_session),
):
    """
    Update leaderboard entry for a user (admin only).

    Recalculates user's score across all leaderboards.
    This should be called periodically or after significant user activity.
    """
    # TODO: Implement proper admin authentication
    if not admin_key:
        raise HTTPException(status_code=403, detail="Admin access required")

    user = await get_user_by_telegram_id(session, telegram_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Calculate scores for all categories
    scores = {
        LeaderboardCategory.TOTAL_PROFIT: user.net_profit_ton,
        LeaderboardCategory.BIGGEST_WIN: user.biggest_win_ton,
        LeaderboardCategory.WIN_STREAK: Decimal(str(user.best_win_streak)),
        LeaderboardCategory.TOTAL_WAGERED: user.total_wagered_ton,
        LeaderboardCategory.STAKING_REWARDS: user.total_staking_rewards_ton,
        LeaderboardCategory.REFERRAL_EARNINGS: user.referral_earnings_ton,
    }

    updated_count = 0

    # Update all leaderboard types
    for lb_type in LeaderboardType:
        for category, score_value in scores.items():
            # Find or create entry
            result = await session.execute(
                select(LeaderboardEntry)
                .where(and_(
                    LeaderboardEntry.user_id == user.id,
                    LeaderboardEntry.leaderboard_type == lb_type,
                    LeaderboardEntry.category == category,
                ))
            )
            entry = result.scalar_one_or_none()

            if entry:
                # Update existing entry
                entry.score_value = score_value
                entry.username = user.username
                entry.updated_at = datetime.utcnow()
            else:
                # Create new entry
                entry = LeaderboardEntry(
                    user_id=user.id,
                    telegram_id=user.telegram_id,
                    username=user.username,
                    leaderboard_type=lb_type,
                    category=category,
                    rank=999999,  # Will be recalculated
                    score_value=score_value,
                )
                session.add(entry)

            updated_count += 1

    await session.commit()

    logger.info(f"Updated leaderboard entries for user {telegram_id}: {updated_count} entries")

    return {
        "success": True,
        "user_id": user.id,
        "telegram_id": telegram_id,
        "updated_entries": updated_count,
    }


@router.post("/recalculate-ranks")
async def recalculate_all_ranks(
    admin_key: str = Header(..., alias="X-Admin-Key"),
    session: AsyncSession = Depends(get_db_session),
):
    """
    Recalculate ranks for all leaderboards (admin only).

    This should be run periodically (e.g., every 5-10 minutes) to update rankings.
    """
    # TODO: Implement proper admin authentication
    if not admin_key:
        raise HTTPException(status_code=403, detail="Admin access required")

    updated_count = 0

    # Recalculate for each leaderboard type and category
    for lb_type in LeaderboardType:
        for category in LeaderboardCategory:
            # Get all entries for this leaderboard, sorted by score
            result = await session.execute(
                select(LeaderboardEntry)
                .where(and_(
                    LeaderboardEntry.leaderboard_type == lb_type,
                    LeaderboardEntry.category == category,
                ))
                .order_by(desc(LeaderboardEntry.score_value))
            )
            entries = result.scalars().all()

            # Update ranks
            for rank, entry in enumerate(entries, start=1):
                entry.previous_rank = entry.rank
                entry.rank = rank
                updated_count += 1

    await session.commit()

    logger.info(f"Recalculated ranks for all leaderboards: {updated_count} entries updated")

    return {
        "success": True,
        "updated_entries": updated_count,
    }

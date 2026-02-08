"""
User API endpoints.

Provides REST API for:
- User registration/authentication
- User profile management
- User statistics
- Balance operations
"""
import logging
import secrets
from datetime import datetime
from decimal import Decimal
from typing import Optional, List

from fastapi import APIRouter, Depends, Query, HTTPException, Header
from pydantic import BaseModel, Field
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.models.user import User

logger = logging.getLogger(__name__)
router = APIRouter()


# ============================================================
# SCHEMAS
# ============================================================

class UserStatsSchema(BaseModel):
    """User statistics."""
    # Game stats
    games_played: int
    games_won: int
    win_rate: float
    current_win_streak: int
    best_win_streak: int

    # Financial stats
    total_wagered_ton: Decimal
    total_won_ton: Decimal
    total_lost_ton: Decimal
    net_profit_ton: Decimal
    biggest_win_ton: Decimal

    # Staking stats
    total_staked_value_ton: Decimal
    active_stakes_count: int
    total_staking_rewards_ton: Decimal

    # Referral stats
    referrals_count: int
    referral_earnings_ton: Decimal


class UserProfileSchema(BaseModel):
    """User profile response."""
    id: int
    telegram_id: int
    username: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    display_name: str
    is_premium: bool

    # Wallet
    wallet_address: Optional[str]
    wallet_connected: bool

    # Balances
    balance_ton: Decimal
    balance_stars: int

    # Gamification
    level: int
    xp: int
    badges_earned: List[str]

    # Referral
    referral_code: str

    # Status
    is_active: bool
    last_seen_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class UserCreateRequest(BaseModel):
    """User registration request."""
    telegram_id: int = Field(..., description="Telegram user ID")
    username: Optional[str] = Field(None, max_length=255)
    first_name: Optional[str] = Field(None, max_length=255)
    last_name: Optional[str] = Field(None, max_length=255)
    language_code: Optional[str] = Field(None, max_length=10)
    is_premium: bool = Field(False)
    referred_by_code: Optional[str] = Field(None, description="Referral code")


class UserUpdateRequest(BaseModel):
    """User profile update request."""
    username: Optional[str] = Field(None, max_length=255)
    first_name: Optional[str] = Field(None, max_length=255)
    last_name: Optional[str] = Field(None, max_length=255)
    wallet_address: Optional[str] = Field(None, max_length=66)


class BalanceUpdateRequest(BaseModel):
    """Balance update request (admin only)."""
    amount_ton: Optional[Decimal] = None
    amount_stars: Optional[int] = None
    operation: str = Field(..., pattern="^(add|subtract|set)$")


# ============================================================
# HELPERS
# ============================================================

def generate_referral_code(telegram_id: int) -> str:
    """Generate unique referral code."""
    return f"ref{telegram_id}"


async def get_user_by_telegram_id(
    session: AsyncSession,
    telegram_id: int
) -> Optional[User]:
    """Get user by Telegram ID."""
    result = await session.execute(
        select(User).where(User.telegram_id == telegram_id)
    )
    return result.scalar_one_or_none()


async def get_user_by_referral_code(
    session: AsyncSession,
    referral_code: str
) -> Optional[User]:
    """Get user by referral code."""
    result = await session.execute(
        select(User).where(User.referral_code == referral_code)
    )
    return result.scalar_one_or_none()


# ============================================================
# ENDPOINTS
# ============================================================

@router.post("/register", response_model=UserProfileSchema, status_code=201)
async def register_user(
    request: UserCreateRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """
    Register a new user.

    - Creates user with Telegram data
    - Generates unique referral code
    - Links to referrer if referral code provided
    - Returns user profile
    """
    # Check if user already exists
    existing_user = await get_user_by_telegram_id(session, request.telegram_id)
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="User already registered"
        )

    # Find referrer if code provided
    referred_by_id = None
    if request.referred_by_code:
        referrer = await get_user_by_referral_code(session, request.referred_by_code)
        if referrer:
            referred_by_id = referrer.id

    # Generate referral code
    referral_code = generate_referral_code(request.telegram_id)

    # Create user
    user = User(
        telegram_id=request.telegram_id,
        username=request.username,
        first_name=request.first_name,
        last_name=request.last_name,
        language_code=request.language_code,
        is_premium=request.is_premium,
        referral_code=referral_code,
        referred_by_id=referred_by_id,
    )

    session.add(user)
    await session.commit()
    await session.refresh(user)

    logger.info(f"User registered: {user.telegram_id} ({user.display_name})")

    # Update referrer stats if applicable
    if referred_by_id:
        referrer = await session.get(User, referred_by_id)
        if referrer:
            referrer.referrals_count += 1
            await session.commit()

    return user


@router.get("/me", response_model=UserProfileSchema)
async def get_current_user(
    telegram_id: int = Header(..., alias="X-Telegram-User-Id"),
    session: AsyncSession = Depends(get_db_session),
):
    """
    Get current user profile.

    Requires X-Telegram-User-Id header with Telegram user ID.
    """
    user = await get_user_by_telegram_id(session, telegram_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Update last seen
    user.last_seen_at = datetime.utcnow()
    await session.commit()

    return user


@router.get("/{user_id}", response_model=UserProfileSchema)
async def get_user_profile(
    user_id: int,
    session: AsyncSession = Depends(get_db_session),
):
    """
    Get user profile by user ID.

    Public endpoint for viewing other users' profiles.
    """
    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


@router.patch("/me", response_model=UserProfileSchema)
async def update_user_profile(
    request: UserUpdateRequest,
    telegram_id: int = Header(..., alias="X-Telegram-User-Id"),
    session: AsyncSession = Depends(get_db_session),
):
    """
    Update current user profile.

    Allows updating username, names, and wallet address.
    """
    user = await get_user_by_telegram_id(session, telegram_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Update fields
    if request.username is not None:
        user.username = request.username
    if request.first_name is not None:
        user.first_name = request.first_name
    if request.last_name is not None:
        user.last_name = request.last_name
    if request.wallet_address is not None:
        user.wallet_address = request.wallet_address
        user.wallet_connected_at = datetime.utcnow()

    await session.commit()
    await session.refresh(user)

    logger.info(f"User updated: {user.telegram_id}")

    return user


@router.get("/me/stats", response_model=UserStatsSchema)
async def get_user_stats(
    telegram_id: int = Header(..., alias="X-Telegram-User-Id"),
    session: AsyncSession = Depends(get_db_session),
):
    """
    Get current user statistics.

    Returns comprehensive stats including games, staking, and referrals.
    """
    user = await get_user_by_telegram_id(session, telegram_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Calculate win rate
    win_rate = (user.games_won / user.games_played * 100) if user.games_played > 0 else 0.0

    return UserStatsSchema(
        games_played=user.games_played,
        games_won=user.games_won,
        win_rate=round(win_rate, 2),
        current_win_streak=user.current_win_streak,
        best_win_streak=user.best_win_streak,
        total_wagered_ton=user.total_wagered_ton,
        total_won_ton=user.total_won_ton,
        total_lost_ton=user.total_lost_ton,
        net_profit_ton=user.net_profit_ton,
        biggest_win_ton=user.biggest_win_ton,
        total_staked_value_ton=user.total_staked_value_ton,
        active_stakes_count=user.active_stakes_count,
        total_staking_rewards_ton=user.total_staking_rewards_ton,
        referrals_count=user.referrals_count,
        referral_earnings_ton=user.referral_earnings_ton,
    )


@router.get("/leaderboard/top", response_model=List[UserProfileSchema])
async def get_top_users(
    limit: int = Query(100, ge=1, le=500),
    order_by: str = Query("net_profit", pattern="^(net_profit|total_wagered|win_streak|level|xp)$"),
    session: AsyncSession = Depends(get_db_session),
):
    """
    Get top users by various metrics.

    - net_profit: Top earners
    - total_wagered: Most active players
    - win_streak: Best winning streaks
    - level: Highest levels
    - xp: Most XP
    """
    # Map order_by to User column
    order_column_map = {
        "net_profit": (User.total_won_ton - User.total_lost_ton).desc(),
        "total_wagered": User.total_wagered_ton.desc(),
        "win_streak": User.best_win_streak.desc(),
        "level": User.level.desc(),
        "xp": User.xp.desc(),
    }

    order_column = order_column_map.get(order_by)

    result = await session.execute(
        select(User)
        .where(User.is_active == True)
        .order_by(order_column)
        .limit(limit)
    )

    users = result.scalars().all()

    return users


@router.post("/me/balance", response_model=UserProfileSchema)
async def update_user_balance(
    request: BalanceUpdateRequest,
    telegram_id: int = Header(..., alias="X-Telegram-User-Id"),
    admin_key: str = Header(..., alias="X-Admin-Key"),
    session: AsyncSession = Depends(get_db_session),
):
    """
    Update user balance (admin only).

    Requires X-Admin-Key header for authentication.

    Operations:
    - add: Add to current balance
    - subtract: Subtract from current balance
    - set: Set balance to specific value
    """
    # TODO: Implement proper admin authentication
    # For now, just check if admin_key is provided
    if not admin_key:
        raise HTTPException(status_code=403, detail="Admin access required")

    user = await get_user_by_telegram_id(session, telegram_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Update TON balance
    if request.amount_ton is not None:
        if request.operation == "add":
            user.balance_ton += request.amount_ton
        elif request.operation == "subtract":
            user.balance_ton -= request.amount_ton
            if user.balance_ton < 0:
                raise HTTPException(status_code=400, detail="Insufficient balance")
        elif request.operation == "set":
            user.balance_ton = request.amount_ton

    # Update Stars balance
    if request.amount_stars is not None:
        if request.operation == "add":
            user.balance_stars += request.amount_stars
        elif request.operation == "subtract":
            user.balance_stars -= request.amount_stars
            if user.balance_stars < 0:
                raise HTTPException(status_code=400, detail="Insufficient balance")
        elif request.operation == "set":
            user.balance_stars = request.amount_stars

    await session.commit()
    await session.refresh(user)

    logger.info(f"Balance updated: {user.telegram_id} - TON: {user.balance_ton}, Stars: {user.balance_stars}")

    return user

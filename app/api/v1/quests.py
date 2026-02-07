"""
Quests API endpoints.

Provides REST API for:
- Daily/Weekly quests
- Quest progress tracking
- Claiming quest rewards
- Achievement system
"""
import logging
from decimal import Decimal
from datetime import datetime, timedelta
from typing import Optional, List

from fastapi import APIRouter, Depends, Query, HTTPException, Header
from pydantic import BaseModel, Field
from sqlalchemy import select, func, and_, or_, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.models.user import User
from app.models.quest import Quest, UserQuest, QuestType, QuestStatus

logger = logging.getLogger(__name__)
router = APIRouter()


# ============================================================
# SCHEMAS
# ============================================================

class QuestRewardSchema(BaseModel):
    """Quest reward details."""
    reward_ton: Decimal
    reward_stars: int
    reward_xp: int
    reward_items: List[dict]


class QuestSchema(BaseModel):
    """Quest details."""
    id: int
    quest_id: str
    type: str
    title: str
    description: Optional[str]
    icon: Optional[str]

    # Requirements
    target_action: str
    target_count: int

    # Rewards
    rewards: QuestRewardSchema

    # Availability
    is_active: bool
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    reset_period: Optional[str]

    class Config:
        from_attributes = True


class UserQuestSchema(BaseModel):
    """User quest progress."""
    id: int
    quest: QuestSchema
    current_progress: int
    target_progress: int
    progress_percent: float
    status: str

    started_at: datetime
    completed_at: Optional[datetime]
    claimed_at: Optional[datetime]
    reset_at: Optional[datetime]

    class Config:
        from_attributes = True


class QuestListResponse(BaseModel):
    """Quest list with progress."""
    total: int
    active: int
    completed: int
    quests: List[UserQuestSchema]
    next_reset: Optional[datetime]


class QuestClaimResponse(BaseModel):
    """Quest claim result."""
    success: bool
    quest_id: str
    rewards_ton: Decimal
    rewards_stars: int
    rewards_xp: int
    new_balance_ton: Decimal
    new_balance_stars: int
    new_xp: int
    new_level: int


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


def calculate_next_reset(quest_type: QuestType) -> Optional[datetime]:
    """Calculate next quest reset time."""
    now = datetime.utcnow()

    if quest_type == QuestType.DAILY:
        # Reset at midnight UTC
        tomorrow = now.date() + timedelta(days=1)
        return datetime.combine(tomorrow, datetime.min.time())

    elif quest_type == QuestType.WEEKLY:
        # Reset on Monday 00:00 UTC
        days_until_monday = (7 - now.weekday()) % 7
        if days_until_monday == 0:
            days_until_monday = 7
        next_monday = now.date() + timedelta(days=days_until_monday)
        return datetime.combine(next_monday, datetime.min.time())

    return None  # Achievement quests don't reset


async def create_user_quest_if_needed(
    session: AsyncSession,
    user: User,
    quest: Quest,
) -> UserQuest:
    """Create user quest progress if doesn't exist."""
    # Check if already exists
    result = await session.execute(
        select(UserQuest)
        .where(and_(
            UserQuest.user_id == user.id,
            UserQuest.quest_id == quest.id,
        ))
    )
    user_quest = result.scalar_one_or_none()

    if not user_quest:
        # Create new progress
        user_quest = UserQuest(
            user_id=user.id,
            quest_id=quest.id,
            current_progress=0,
            target_progress=quest.target_count,
            status=QuestStatus.ACTIVE,
            reset_at=calculate_next_reset(quest.type),
        )
        session.add(user_quest)
        await session.commit()
        await session.refresh(user_quest)

    return user_quest


async def check_and_reset_quests(
    session: AsyncSession,
    user: User,
):
    """Check and reset expired quests."""
    now = datetime.utcnow()

    # Find expired quests
    result = await session.execute(
        select(UserQuest)
        .where(and_(
            UserQuest.user_id == user.id,
            UserQuest.reset_at.is_not(None),
            UserQuest.reset_at <= now,
            UserQuest.status != QuestStatus.CLAIMED,
        ))
    )
    expired_quests = result.scalars().all()

    for user_quest in expired_quests:
        # Get quest details
        quest = await session.get(Quest, user_quest.quest_id)
        if quest and quest.is_active:
            # Reset progress
            user_quest.current_progress = 0
            user_quest.status = QuestStatus.ACTIVE
            user_quest.started_at = now
            user_quest.completed_at = None
            user_quest.claimed_at = None
            user_quest.reset_at = calculate_next_reset(quest.type)

    await session.commit()


# ============================================================
# ENDPOINTS
# ============================================================

@router.get("/daily", response_model=QuestListResponse)
async def get_daily_quests(
    telegram_id: int = Header(..., alias="X-Telegram-User-Id"),
    session: AsyncSession = Depends(get_db_session),
):
    """
    Get daily quests with progress.

    Daily quests reset every day at midnight UTC.
    """
    user = await get_user_by_telegram_id(session, telegram_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Reset expired quests
    await check_and_reset_quests(session, user)

    # Get active daily quests
    result = await session.execute(
        select(Quest)
        .where(and_(
            Quest.type == QuestType.DAILY,
            Quest.is_active == True,
        ))
    )
    quests = result.scalars().all()

    # Get or create user progress for each quest
    user_quests = []
    for quest in quests:
        user_quest = await create_user_quest_if_needed(session, user, quest)

        # Calculate progress percent
        progress_percent = (user_quest.current_progress / user_quest.target_progress * 100) if user_quest.target_progress > 0 else 0

        # Enrich with quest data
        quest_data = UserQuestSchema(
            id=user_quest.id,
            quest=QuestSchema(
                **quest.__dict__,
                rewards=QuestRewardSchema(
                    reward_ton=quest.reward_ton,
                    reward_stars=quest.reward_stars,
                    reward_xp=quest.reward_xp,
                    reward_items=quest.reward_items,
                )
            ),
            current_progress=user_quest.current_progress,
            target_progress=user_quest.target_progress,
            progress_percent=round(progress_percent, 1),
            status=user_quest.status.value,
            started_at=user_quest.started_at,
            completed_at=user_quest.completed_at,
            claimed_at=user_quest.claimed_at,
            reset_at=user_quest.reset_at,
        )
        user_quests.append(quest_data)

    # Count statuses
    active = sum(1 for q in user_quests if q.status == "ACTIVE")
    completed = sum(1 for q in user_quests if q.status in ["COMPLETED", "CLAIMED"])

    # Next reset time
    next_reset = calculate_next_reset(QuestType.DAILY)

    return QuestListResponse(
        total=len(user_quests),
        active=active,
        completed=completed,
        quests=user_quests,
        next_reset=next_reset,
    )


@router.get("/weekly", response_model=QuestListResponse)
async def get_weekly_quests(
    telegram_id: int = Header(..., alias="X-Telegram-User-Id"),
    session: AsyncSession = Depends(get_db_session),
):
    """
    Get weekly quests with progress.

    Weekly quests reset every Monday at midnight UTC.
    """
    user = await get_user_by_telegram_id(session, telegram_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Reset expired quests
    await check_and_reset_quests(session, user)

    # Get active weekly quests
    result = await session.execute(
        select(Quest)
        .where(and_(
            Quest.type == QuestType.WEEKLY,
            Quest.is_active == True,
        ))
    )
    quests = result.scalars().all()

    # Get or create user progress for each quest
    user_quests = []
    for quest in quests:
        user_quest = await create_user_quest_if_needed(session, user, quest)

        # Calculate progress percent
        progress_percent = (user_quest.current_progress / user_quest.target_progress * 100) if user_quest.target_progress > 0 else 0

        # Enrich with quest data
        quest_data = UserQuestSchema(
            id=user_quest.id,
            quest=QuestSchema(
                **quest.__dict__,
                rewards=QuestRewardSchema(
                    reward_ton=quest.reward_ton,
                    reward_stars=quest.reward_stars,
                    reward_xp=quest.reward_xp,
                    reward_items=quest.reward_items,
                )
            ),
            current_progress=user_quest.current_progress,
            target_progress=user_quest.target_progress,
            progress_percent=round(progress_percent, 1),
            status=user_quest.status.value,
            started_at=user_quest.started_at,
            completed_at=user_quest.completed_at,
            claimed_at=user_quest.claimed_at,
            reset_at=user_quest.reset_at,
        )
        user_quests.append(quest_data)

    # Count statuses
    active = sum(1 for q in user_quests if q.status == "ACTIVE")
    completed = sum(1 for q in user_quests if q.status in ["COMPLETED", "CLAIMED"])

    # Next reset time
    next_reset = calculate_next_reset(QuestType.WEEKLY)

    return QuestListResponse(
        total=len(user_quests),
        active=active,
        completed=completed,
        quests=user_quests,
        next_reset=next_reset,
    )


@router.get("/achievements", response_model=QuestListResponse)
async def get_achievements(
    telegram_id: int = Header(..., alias="X-Telegram-User-Id"),
    session: AsyncSession = Depends(get_db_session),
):
    """
    Get achievements.

    Achievements are one-time quests that don't reset.
    """
    user = await get_user_by_telegram_id(session, telegram_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get active achievements
    result = await session.execute(
        select(Quest)
        .where(and_(
            Quest.type == QuestType.ACHIEVEMENT,
            Quest.is_active == True,
        ))
    )
    quests = result.scalars().all()

    # Get or create user progress for each quest
    user_quests = []
    for quest in quests:
        user_quest = await create_user_quest_if_needed(session, user, quest)

        # Calculate progress percent
        progress_percent = (user_quest.current_progress / user_quest.target_progress * 100) if user_quest.target_progress > 0 else 0

        # Enrich with quest data
        quest_data = UserQuestSchema(
            id=user_quest.id,
            quest=QuestSchema(
                **quest.__dict__,
                rewards=QuestRewardSchema(
                    reward_ton=quest.reward_ton,
                    reward_stars=quest.reward_stars,
                    reward_xp=quest.reward_xp,
                    reward_items=quest.reward_items,
                )
            ),
            current_progress=user_quest.current_progress,
            target_progress=user_quest.target_progress,
            progress_percent=round(progress_percent, 1),
            status=user_quest.status.value,
            started_at=user_quest.started_at,
            completed_at=user_quest.completed_at,
            claimed_at=user_quest.claimed_at,
            reset_at=user_quest.reset_at,
        )
        user_quests.append(quest_data)

    # Count statuses
    active = sum(1 for q in user_quests if q.status == "ACTIVE")
    completed = sum(1 for q in user_quests if q.status in ["COMPLETED", "CLAIMED"])

    return QuestListResponse(
        total=len(user_quests),
        active=active,
        completed=completed,
        quests=user_quests,
        next_reset=None,  # Achievements don't reset
    )


@router.post("/claim/{user_quest_id}", response_model=QuestClaimResponse)
async def claim_quest_reward(
    user_quest_id: int,
    telegram_id: int = Header(..., alias="X-Telegram-User-Id"),
    session: AsyncSession = Depends(get_db_session),
):
    """
    Claim quest rewards.

    Quest must be completed (progress >= target).
    Rewards transferred to user balance.
    """
    user = await get_user_by_telegram_id(session, telegram_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get user quest
    user_quest = await session.get(UserQuest, user_quest_id)
    if not user_quest or user_quest.user_id != user.id:
        raise HTTPException(status_code=404, detail="Quest not found")

    # Check if already claimed
    if user_quest.status == QuestStatus.CLAIMED:
        raise HTTPException(status_code=400, detail="Quest already claimed")

    # Check if completed
    if user_quest.current_progress < user_quest.target_progress:
        raise HTTPException(status_code=400, detail="Quest not completed yet")

    # Get quest details
    quest = await session.get(Quest, user_quest.quest_id)
    if not quest:
        raise HTTPException(status_code=404, detail="Quest template not found")

    # Apply rewards
    user.balance_ton += quest.reward_ton
    user.balance_stars += quest.reward_stars
    user.xp += quest.reward_xp

    # Check for level up (simple: 100 XP per level)
    old_level = user.level
    new_level = (user.xp // 100) + 1
    if new_level > old_level:
        user.level = new_level
        logger.info(f"User leveled up: {user.telegram_id} - Level {new_level}")

    # Mark quest as claimed
    user_quest.status = QuestStatus.CLAIMED
    user_quest.claimed_at = datetime.utcnow()

    await session.commit()

    logger.info(f"Quest claimed: {user.telegram_id} - {quest.quest_id}")

    return QuestClaimResponse(
        success=True,
        quest_id=quest.quest_id,
        rewards_ton=quest.reward_ton,
        rewards_stars=quest.reward_stars,
        rewards_xp=quest.reward_xp,
        new_balance_ton=user.balance_ton,
        new_balance_stars=user.balance_stars,
        new_xp=user.xp,
        new_level=user.level,
    )


@router.post("/progress/{quest_id}")
async def update_quest_progress(
    quest_id: str,
    increment: int = 1,
    telegram_id: int = Header(..., alias="X-Telegram-User-Id"),
    session: AsyncSession = Depends(get_db_session),
):
    """
    Update quest progress (internal API for game services).

    Increments quest progress when user completes actions.
    """
    user = await get_user_by_telegram_id(session, telegram_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get quest by quest_id
    result = await session.execute(
        select(Quest).where(Quest.quest_id == quest_id)
    )
    quest = result.scalar_one_or_none()
    if not quest:
        raise HTTPException(status_code=404, detail="Quest not found")

    # Get or create user quest
    user_quest = await create_user_quest_if_needed(session, user, quest)

    # Update progress (if not already completed)
    if user_quest.status == QuestStatus.ACTIVE:
        user_quest.current_progress += increment

        # Check if completed
        if user_quest.current_progress >= user_quest.target_progress:
            user_quest.status = QuestStatus.COMPLETED
            user_quest.completed_at = datetime.utcnow()
            logger.info(f"Quest completed: {user.telegram_id} - {quest.quest_id}")

        await session.commit()

    return {
        "success": True,
        "quest_id": quest_id,
        "current_progress": user_quest.current_progress,
        "target_progress": user_quest.target_progress,
        "status": user_quest.status.value,
    }

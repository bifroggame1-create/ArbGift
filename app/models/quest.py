"""Daily quests and achievements models."""
from datetime import datetime, date
from decimal import Decimal
from enum import Enum
from typing import Optional

from sqlalchemy import String, Integer, BigInteger, Numeric, Boolean, Date, DateTime, ForeignKey, Index, Enum as SQLEnum, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import func

from app.core.database import Base


class QuestType(str, Enum):
    """Типы квестов."""
    DAILY = "daily"         # Ежедневные квесты (обновляются каждый день)
    WEEKLY = "weekly"       # Еженедельные
    ACHIEVEMENT = "achievement"  # Одноразовые достижения


class QuestStatus(str, Enum):
    """Статус квеста."""
    ACTIVE = "active"
    COMPLETED = "completed"
    CLAIMED = "claimed"  # награда получена


class Quest(Base):
    """
    Квест/Достижение.

    Шаблон квеста, который пользователи выполняют.
    """
    __tablename__ = "quests"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Метаданные
    quest_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)  # "daily_stake_gift"
    type: Mapped[QuestType] = mapped_column(SQLEnum(QuestType), nullable=False, index=True)

    # Описание
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    icon: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)  # emoji

    # Условия выполнения
    target_action: Mapped[str] = mapped_column(String(100), nullable=False)  # "stake_gift", "win_game", etc.
    target_count: Mapped[int] = mapped_column(Integer, default=1)  # сколько раз нужно выполнить
    target_params: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)  # доп параметры

    # Награды
    reward_ton: Mapped[Decimal] = mapped_column(Numeric(18, 9), default=Decimal("0"))
    reward_stars: Mapped[int] = mapped_column(Integer, default=0)
    reward_xp: Mapped[int] = mapped_column(Integer, default=0)

    # Доступность
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    required_level: Mapped[int] = mapped_column(Integer, default=1)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )


class UserQuest(Base):
    """
    Прогресс пользователя по квесту.
    """
    __tablename__ = "user_quests"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    quest_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("quests.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Прогресс
    current_count: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[QuestStatus] = mapped_column(SQLEnum(QuestStatus), default=QuestStatus.ACTIVE)

    # Timestamps
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    claimed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Для daily/weekly квестов - дата сброса
    reset_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    __table_args__ = (
        Index("ix_user_quest_user_status", "user_id", "status"),
        Index("ix_user_quest_reset_date", "reset_date"),
    )

    @property
    def progress_percent(self) -> float:
        """Процент выполнения."""
        # Получаем target_count из quest (потребуется join)
        return 0.0  # Placeholder

    @property
    def is_completed(self) -> bool:
        """Завершен ли квест."""
        return self.status in [QuestStatus.COMPLETED, QuestStatus.CLAIMED]


class Badge(Base):
    """
    NFT Badge/Achievement.

    Награды за достижения, отображаются как NFT в профиле.
    """
    __tablename__ = "badges"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Метаданные
    badge_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=False)

    # Визуал
    icon: Mapped[str] = mapped_column(String(10), nullable=False)  # emoji
    image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    rarity: Mapped[str] = mapped_column(String(50), default="common")  # common, rare, epic, legendary

    # Условие получения
    requirement_type: Mapped[str] = mapped_column(String(100), nullable=False)  # "total_stakes", "total_won", etc.
    requirement_value: Mapped[int] = mapped_column(Integer, nullable=False)

    # Бонусы от бейджа
    bonus_apy_percent: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal("0"))  # +10% APY
    bonus_referral_percent: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal("0"))

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )


class UserBadge(Base):
    """
    Бейджи, полученные пользователем.
    """
    __tablename__ = "user_badges"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    badge_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("badges.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Когда получен
    earned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    # Отображается ли в профиле
    is_equipped: Mapped[bool] = mapped_column(Boolean, default=False)

    __table_args__ = (
        Index("ix_user_badge_user_badge", "user_id", "badge_id", unique=True),
    )

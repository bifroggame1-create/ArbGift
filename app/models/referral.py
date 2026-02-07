"""Referral system models."""
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional

from sqlalchemy import String, Integer, BigInteger, Numeric, DateTime, ForeignKey, Index, Enum as SQLEnum, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import func

from app.core.database import Base


class ReferralTier(str, Enum):
    """Уровни реферальной программы."""
    BRONZE = "bronze"      # 0-10 рефералов, 3% комиссия
    SILVER = "silver"      # 11-50 рефералов, 5% комиссия
    GOLD = "gold"          # 51-200 рефералов, 7% комиссия
    PLATINUM = "platinum"  # 201+ рефералов, 10% комиссия


class Referral(Base):
    """
    Реферальная связь.

    Отслеживает кто кого пригласил и сколько заработал.
    """
    __tablename__ = "referrals"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Кто пригласил
    referrer_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Кого пригласили
    referred_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Комиссия (% от earnings приглашенного)
    commission_percent: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal("5.0"))

    # Статистика
    total_earned_ton: Mapped[Decimal] = mapped_column(Numeric(18, 9), default=Decimal("0"))
    total_commission_paid_ton: Mapped[Decimal] = mapped_column(Numeric(18, 9), default=Decimal("0"))
    referral_activities_count: Mapped[int] = mapped_column(Integer, default=0)

    # Активность реферала
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_activity_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    __table_args__ = (
        Index("ix_referral_referrer_referred", "referrer_id", "referred_id", unique=True),
    )


class ReferralReward(Base):
    """
    История выплат реферальных наград.
    """
    __tablename__ = "referral_rewards"

    id: Mapped[int] = mapped_column(primary_key=True)

    referral_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("referrals.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Кто получил награду (referrer)
    recipient_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Сумма награды
    amount_ton: Mapped[Decimal] = mapped_column(Numeric(18, 9), nullable=False)

    # Причина награды
    source_type: Mapped[str] = mapped_column(String(50), nullable=False)  # stake, game_win, deposit
    source_amount_ton: Mapped[Decimal] = mapped_column(Numeric(18, 9), nullable=False)

    # Timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    __table_args__ = (
        Index("ix_reward_recipient_created", "recipient_id", "created_at"),
    )

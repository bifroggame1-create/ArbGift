"""
Staking Models.

По образцу Rolls.codes стейкинга.
"""
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional
from uuid import uuid4

from sqlalchemy import (
    String, Integer, BigInteger, Numeric, Boolean,
    DateTime, ForeignKey, Index, Enum as SQLEnum,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class StakeStatus(str, Enum):
    """Статус стейка."""
    ACTIVE = "active"        # Активный стейк
    COMPLETED = "completed"  # Успешно завершен (получена награда)
    WITHDRAWN = "withdrawn"  # Снят досрочно (штраф)
    EXPIRED = "expired"      # Истек без забора


class StakePeriod(str, Enum):
    """Период стейкинга."""
    WEEK_1 = "1w"    # 1 неделя - 5% APY
    WEEK_2 = "2w"    # 2 недели - 8% APY
    MONTH_1 = "1m"   # 1 месяц - 12% APY
    MONTH_3 = "3m"   # 3 месяца - 20% APY


class Stake(Base):
    """
    Стейк NFT гифта.

    Пользователь блокирует гифт на определенный срок
    и получает награду в конце периода.
    """
    __tablename__ = "stakes"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    # Владелец
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    user_telegram_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    user_name: Mapped[str] = mapped_column(String(255), nullable=False)

    # NFT гифт
    gift_address: Mapped[str] = mapped_column(String(128), nullable=False, unique=True)
    gift_name: Mapped[str] = mapped_column(String(255), nullable=False)
    gift_image_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    gift_value_ton: Mapped[Decimal] = mapped_column(Numeric(18, 9), nullable=False)
    gift_rarity: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # common, rare, epic, etc.

    # Параметры стейка
    period: Mapped[StakePeriod] = mapped_column(
        SQLEnum(StakePeriod),
        nullable=False,
    )
    apy_percent: Mapped[Decimal] = mapped_column(Numeric(6, 2), nullable=False)  # увеличил до 6 для 600%
    rarity_multiplier: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal("1.0"))
    collection_set_bonus: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal("0"))
    auto_compound: Mapped[bool] = mapped_column(Boolean, default=False)  # auto-reinvest rewards

    # Расчет награды
    expected_reward_ton: Mapped[Decimal] = mapped_column(Numeric(18, 9), nullable=False)
    actual_reward_ton: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 9), nullable=True)

    # Штраф за досрочный вывод (% от стоимости)
    early_withdrawal_penalty_percent: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        default=Decimal("10"),  # 10% штраф
    )
    penalty_paid_ton: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 9), nullable=True)

    # Статус
    status: Mapped[StakeStatus] = mapped_column(
        SQLEnum(StakeStatus),
        default=StakeStatus.ACTIVE,
        index=True,
    )

    # Время
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    unlocks_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Transaction hashes
    stake_tx_hash: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    unstake_tx_hash: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)

    __table_args__ = (
        Index("ix_stake_user_status", "user_id", "status"),
        Index("ix_stake_unlocks_at", "unlocks_at"),
    )

    @property
    def is_unlockable(self) -> bool:
        """Можно ли разблокировать без штрафа."""
        return datetime.utcnow() >= self.unlocks_at

    @property
    def days_remaining(self) -> int:
        """Дней до разблокировки."""
        if self.is_unlockable:
            return 0
        delta = self.unlocks_at - datetime.utcnow()
        return max(0, delta.days)


class UserStakingStats(Base):
    """
    Статистика стейкинга пользователя.
    """
    __tablename__ = "user_staking_stats"

    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)

    # Общая статистика
    total_stakes: Mapped[int] = mapped_column(Integer, default=0)
    active_stakes: Mapped[int] = mapped_column(Integer, default=0)
    completed_stakes: Mapped[int] = mapped_column(Integer, default=0)

    # Значения в TON
    total_staked_ton: Mapped[Decimal] = mapped_column(Numeric(18, 9), default=Decimal("0"))
    currently_staked_ton: Mapped[Decimal] = mapped_column(Numeric(18, 9), default=Decimal("0"))
    total_rewards_earned_ton: Mapped[Decimal] = mapped_column(Numeric(18, 9), default=Decimal("0"))
    total_penalties_paid_ton: Mapped[Decimal] = mapped_column(Numeric(18, 9), default=Decimal("0"))

    # Время
    first_stake_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    last_stake_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    @property
    def net_profit_ton(self) -> Decimal:
        """Чистая прибыль."""
        return self.total_rewards_earned_ton - self.total_penalties_paid_ton

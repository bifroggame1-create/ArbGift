"""User model for authentication and profile."""
from datetime import datetime
from typing import Optional
from decimal import Decimal

from sqlalchemy import String, BigInteger, Integer, Numeric, Boolean, DateTime, func, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class User(Base):
    """
    User model.

    Основная модель пользователя для всех сервисов.
    """
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Telegram data
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False, index=True)
    username: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    first_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    language_code: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    is_premium: Mapped[bool] = mapped_column(Boolean, default=False)

    # TON Connect
    wallet_address: Mapped[Optional[str]] = mapped_column(String(66), nullable=True, index=True)

    # Balances
    balance_ton: Mapped[Decimal] = mapped_column(Numeric(18, 9), default=Decimal("0"))
    balance_stars: Mapped[Integer] = mapped_column(Integer, default=0)

    # Referral system
    referral_code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    referred_by_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    referral_count: Mapped[int] = mapped_column(Integer, default=0)
    referral_earnings_ton: Mapped[Decimal] = mapped_column(Numeric(18, 9), default=Decimal("0"))

    # Levels & XP
    level: Mapped[int] = mapped_column(Integer, default=1)
    xp: Mapped[int] = mapped_column(Integer, default=0)

    # Achievements
    badges_earned: Mapped[list] = mapped_column(JSONB, default=[])  # список badge IDs

    # Stats
    total_wagered_ton: Mapped[Decimal] = mapped_column(Numeric(18, 9), default=Decimal("0"))
    total_won_ton: Mapped[Decimal] = mapped_column(Numeric(18, 9), default=Decimal("0"))
    total_lost_ton: Mapped[Decimal] = mapped_column(Numeric(18, 9), default=Decimal("0"))
    games_played: Mapped[int] = mapped_column(Integer, default=0)
    games_won: Mapped[int] = mapped_column(Integer, default=0)

    # Staking stats
    total_staked_value_ton: Mapped[Decimal] = mapped_column(Numeric(18, 9), default=Decimal("0"))
    active_stakes_count: Mapped[int] = mapped_column(Integer, default=0)
    total_staking_rewards_ton: Mapped[Decimal] = mapped_column(Numeric(18, 9), default=Decimal("0"))

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    last_login_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        onupdate=func.now(),
    )

    __table_args__ = (
        Index("ix_user_level_xp", "level", "xp"),
        Index("ix_user_balance", "balance_ton"),
    )

    @property
    def net_profit_ton(self) -> Decimal:
        """Чистая прибыль от игр."""
        return self.total_won_ton - self.total_lost_ton

    @property
    def win_rate(self) -> float:
        """Процент побед."""
        if self.games_played == 0:
            return 0.0
        return (self.games_won / self.games_played) * 100

    @property
    def display_name(self) -> str:
        """Отображаемое имя."""
        if self.username:
            return f"@{self.username}"
        if self.first_name:
            name = self.first_name
            if self.last_name:
                name += f" {self.last_name}"
            return name
        return f"User {self.telegram_id}"

    def __repr__(self) -> str:
        return f"<User {self.display_name} ({self.telegram_id})>"

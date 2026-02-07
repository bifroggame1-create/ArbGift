"""Leaderboard models."""
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional

from sqlalchemy import String, Integer, BigInteger, Numeric, DateTime, ForeignKey, Index, Enum as SQLEnum, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import func

from app.core.database import Base


class LeaderboardType(str, Enum):
    """Типы лидерборда."""
    ALL_TIME = "all_time"        # За все время
    WEEKLY = "weekly"            # За неделю
    MONTHLY = "monthly"          # За месяц
    DAILY = "daily"              # За день


class LeaderboardCategory(str, Enum):
    """Категории лидерборда."""
    TOTAL_PROFIT = "total_profit"        # По общей прибыли
    BIGGEST_WIN = "biggest_win"          # По макс. выигрышу
    WIN_STREAK = "win_streak"            # По серии побед
    TOTAL_WAGERED = "total_wagered"      # По общей сумме ставок
    STAKING_REWARDS = "staking_rewards"  # По наградам от стейкинга
    REFERRAL_EARNINGS = "referral_earnings"  # По реферальным наградам


class LeaderboardEntry(Base):
    """
    Запись в лидерборде.

    Обновляется периодически (раз в 5-10 минут).
    """
    __tablename__ = "leaderboard_entries"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Пользователь
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    telegram_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    username: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Тип и категория
    leaderboard_type: Mapped[LeaderboardType] = mapped_column(
        SQLEnum(LeaderboardType),
        nullable=False,
        index=True,
    )
    category: Mapped[LeaderboardCategory] = mapped_column(
        SQLEnum(LeaderboardCategory),
        nullable=False,
        index=True,
    )

    # Позиция
    rank: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    previous_rank: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Значение (метрика)
    score_value: Mapped[Decimal] = mapped_column(Numeric(18, 9), nullable=False)

    # Период (для weekly/monthly/daily)
    period_start: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    period_end: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    __table_args__ = (
        Index(
            "ix_leaderboard_type_category_rank",
            "leaderboard_type",
            "category",
            "rank",
        ),
        Index(
            "ix_leaderboard_user_type_category",
            "user_id",
            "leaderboard_type",
            "category",
            unique=True,
        ),
    )

    @property
    def rank_change(self) -> int:
        """Изменение позиции."""
        if self.previous_rank is None:
            return 0
        return self.previous_rank - self.rank  # положительное = улучшение


class GameHistory(Base):
    """
    История игр для статистики.

    Используется для расчета лидерборда.
    """
    __tablename__ = "game_history"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Пользователь
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Игра
    game_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # coin_flip, plinko, pvp, etc.
    game_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Ставка и результат
    bet_amount_ton: Mapped[Decimal] = mapped_column(Numeric(18, 9), nullable=False)
    bet_currency: Mapped[str] = mapped_column(String(20), default="TON")  # TON, STARS, GIFT

    payout_amount_ton: Mapped[Decimal] = mapped_column(Numeric(18, 9), default=Decimal("0"))
    multiplier: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("0"))

    profit_ton: Mapped[Decimal] = mapped_column(Numeric(18, 9), nullable=False)  # может быть отрицательным

    # Результат
    is_win: Mapped[bool] = mapped_column(Boolean, nullable=False)

    # Provably Fair
    server_seed_hash: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    client_seed: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    nonce: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Timestamp
    played_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        index=True,
    )

    __table_args__ = (
        Index("ix_game_history_user_played", "user_id", "played_at"),
        Index("ix_game_history_type_played", "game_type", "played_at"),
    )

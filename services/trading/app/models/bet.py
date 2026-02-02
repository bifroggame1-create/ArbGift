"""
Trading Bet Model.

SQLAlchemy 2.0 style with Mapped[] annotations.
"""
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional
from uuid import uuid4

from sqlalchemy import String, BigInteger, Numeric, DateTime, ForeignKey, Index, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class BetStatus(str, Enum):
    """Bet status."""
    ACTIVE = "active"          # Bet placed, game running
    CASHED_OUT = "cashed_out"  # User cashed out before crash
    LOST = "lost"              # User didn't cash out before crash


class TradingBet(Base):
    """
    Trading/Crash game bet.

    User places bet and can cash out at any time before crash.
    """
    __tablename__ = "trading_bets"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    # Relations
    game_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("trading_games.id"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    user_telegram_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    user_name: Mapped[str] = mapped_column(String(255), nullable=False)

    # Bet details
    bet_amount_ton: Mapped[Decimal] = mapped_column(Numeric(18, 9), nullable=False)
    cash_out_multiplier: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    profit_ton: Mapped[Decimal] = mapped_column(Numeric(18, 9), default=Decimal("0"))

    # Status
    status: Mapped[BetStatus] = mapped_column(
        SQLEnum(BetStatus),
        default=BetStatus.ACTIVE,
        nullable=False,
        index=True,
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    cashed_out_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    __table_args__ = (
        Index("ix_trading_bet_game_user", "game_id", "user_id"),
    )

    def __repr__(self) -> str:
        return f"<TradingBet {self.bet_amount_ton} TON @ {self.cash_out_multiplier}x>"


class UserTradingStats(Base):
    """User trading statistics."""
    __tablename__ = "user_trading_stats"

    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)

    # Stats
    total_games: Mapped[int] = mapped_column(default=0)
    total_wins: Mapped[int] = mapped_column(default=0)
    total_losses: Mapped[int] = mapped_column(default=0)

    # Volume
    total_wagered_ton: Mapped[Decimal] = mapped_column(Numeric(18, 9), default=Decimal("0"))
    total_won_ton: Mapped[Decimal] = mapped_column(Numeric(18, 9), default=Decimal("0"))
    total_profit_ton: Mapped[Decimal] = mapped_column(Numeric(18, 9), default=Decimal("0"))

    # Records
    biggest_win_ton: Mapped[Decimal] = mapped_column(Numeric(18, 9), default=Decimal("0"))
    highest_multiplier: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("0"))
    current_win_streak: Mapped[int] = mapped_column(default=0)
    max_win_streak: Mapped[int] = mapped_column(default=0)

    @property
    def win_rate(self) -> Decimal:
        """Win rate percentage."""
        if self.total_games == 0:
            return Decimal("0")
        return Decimal(self.total_wins) / Decimal(self.total_games) * 100

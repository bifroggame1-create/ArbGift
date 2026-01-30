"""
Bet model for tracking player bets.
"""
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional
from uuid import uuid4

from sqlalchemy import String, Numeric, DateTime, Boolean, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.game import Game


class Bet(Base, TimestampMixin):
    """
    Bet model representing a player's bet in a game.

    Tracks:
    - Bet amount
    - Cash out timing and multiplier
    - Win/loss status and payout amount
    """

    __tablename__ = "bets"

    # Primary key
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    # Foreign keys
    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    game_id: Mapped[int] = mapped_column(
        ForeignKey("games.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Bet details
    amount: Mapped[Decimal] = mapped_column(
        Numeric(precision=18, scale=9),
        nullable=False,
    )

    # Auto cash-out multiplier (optional)
    auto_cashout_at: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(precision=10, scale=2),
        nullable=True,
    )

    # Cash out details (populated when player cashes out)
    cashed_out: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    cashed_out_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    cashout_multiplier: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(precision=10, scale=2),
        nullable=True,
    )

    # Result (computed after game ends)
    won: Mapped[Optional[bool]] = mapped_column(
        Boolean,
        nullable=True,  # Null until game ends
    )
    payout: Mapped[Decimal] = mapped_column(
        Numeric(precision=18, scale=9),
        default=Decimal("0"),
        nullable=False,
    )
    profit: Mapped[Decimal] = mapped_column(
        Numeric(precision=18, scale=9),
        default=Decimal("0"),
        nullable=False,
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="bets",
        lazy="joined",
    )
    game: Mapped["Game"] = relationship(
        "Game",
        back_populates="bets",
        lazy="joined",
    )

    # Indexes
    __table_args__ = (
        Index("ix_bets_user_game", "user_id", "game_id", unique=True),
        Index("ix_bets_cashed_out", "cashed_out"),
        Index("ix_bets_won", "won"),
    )

    def __repr__(self) -> str:
        return f"<Bet(id={self.id}, amount={self.amount}, won={self.won})>"

    def calculate_payout(self, multiplier: Decimal) -> Decimal:
        """Calculate payout for a given multiplier."""
        return self.amount * multiplier

    def execute_cashout(self, multiplier: Decimal, cashout_time: datetime) -> None:
        """Execute cash out at the given multiplier."""
        self.cashed_out = True
        self.cashed_out_at = cashout_time
        self.cashout_multiplier = multiplier
        self.payout = self.calculate_payout(multiplier)
        self.profit = self.payout - self.amount
        self.won = True

    def mark_lost(self) -> None:
        """Mark bet as lost (crashed before cash out)."""
        self.won = False
        self.payout = Decimal("0")
        self.profit = -self.amount

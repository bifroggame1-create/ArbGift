"""
Game model for tracking rounds.
"""
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import String, Numeric, DateTime, Enum as SQLEnum, Index, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.bet import Bet


class GamePhase(str, Enum):
    """Game phases."""

    BETTING = "betting"      # Accepting bets
    RUNNING = "running"      # Multiplier growing
    CRASHED = "crashed"      # Round ended


class Game(Base, TimestampMixin):
    """
    Game model representing a single round.

    Each game has:
    - A predetermined crash point (provably fair)
    - Start and end timestamps
    - Associated bets
    """

    __tablename__ = "games"

    # Primary key (auto-incrementing game ID for provably fair verification)
    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    # Game state
    phase: Mapped[GamePhase] = mapped_column(
        SQLEnum(GamePhase),
        default=GamePhase.BETTING,
        nullable=False,
    )

    # Crash point (hidden until game ends)
    crash_point: Mapped[Decimal] = mapped_column(
        Numeric(precision=10, scale=2),
        nullable=False,
    )

    # Server seed hash (for provably fair verification)
    # The actual seed is revealed after the game
    server_seed_hash: Mapped[str] = mapped_column(
        String(64),  # SHA-256 hash
        nullable=False,
    )

    # Revealed server seed (populated after game ends)
    server_seed: Mapped[Optional[str]] = mapped_column(
        String(128),
        nullable=True,
    )

    # Timestamps
    betting_started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    game_started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    crashed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Aggregate statistics (computed after game ends)
    total_bets: Mapped[Decimal] = mapped_column(
        Numeric(precision=18, scale=9),
        default=Decimal("0"),
        nullable=False,
    )
    total_payouts: Mapped[Decimal] = mapped_column(
        Numeric(precision=18, scale=9),
        default=Decimal("0"),
        nullable=False,
    )
    num_players: Mapped[int] = mapped_column(
        default=0,
        nullable=False,
    )
    num_winners: Mapped[int] = mapped_column(
        default=0,
        nullable=False,
    )

    # Relationships
    bets: Mapped[List["Bet"]] = relationship(
        "Bet",
        back_populates="game",
        lazy="selectin",
    )

    # Indexes
    __table_args__ = (
        Index("ix_games_phase", "phase"),
        Index("ix_games_created_at", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<Game(id={self.id}, phase={self.phase}, crash_point={self.crash_point})>"

    @property
    def is_betting_open(self) -> bool:
        """Check if betting is still open."""
        return self.phase == GamePhase.BETTING

    @property
    def is_running(self) -> bool:
        """Check if game is currently running."""
        return self.phase == GamePhase.RUNNING

    @property
    def is_ended(self) -> bool:
        """Check if game has ended."""
        return self.phase == GamePhase.CRASHED

    @property
    def house_profit(self) -> Decimal:
        """Calculate house profit for this round."""
        return self.total_bets - self.total_payouts

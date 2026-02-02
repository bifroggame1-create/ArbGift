"""
Trading Game Model.

SQLAlchemy 2.0 style with Mapped[] annotations.
"""
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional
from uuid import uuid4

from sqlalchemy import String, Integer, Numeric, DateTime, Index, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class GameStatus(str, Enum):
    """Game status."""
    PENDING = "pending"      # Accepting bets
    ACTIVE = "active"        # Multiplier is growing
    CRASHED = "crashed"      # Game ended
    COMPLETED = "completed"  # Payouts processed


class TradingGame(Base):
    """
    Trading/Crash game.

    Multiplier grows until it crashes at a pre-determined point.
    """
    __tablename__ = "trading_games"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    game_number: Mapped[int] = mapped_column(
        Integer,
        unique=True,
        nullable=False,
        index=True,
    )

    # Game state
    status: Mapped[GameStatus] = mapped_column(
        SQLEnum(GameStatus),
        default=GameStatus.PENDING,
        nullable=False,
        index=True,
    )
    current_multiplier: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        default=Decimal("1.00"),
        nullable=False,
    )
    crash_point: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(10, 2),
        nullable=True,
    )

    # Provably fair
    server_seed_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    server_seed: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    nonce: Mapped[int] = mapped_column(Integer, nullable=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    crashed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Stats
    total_bets: Mapped[int] = mapped_column(Integer, default=0)
    total_volume_ton: Mapped[Decimal] = mapped_column(
        Numeric(18, 9),
        default=Decimal("0"),
    )

    __table_args__ = (
        Index("ix_trading_game_status_created", "status", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<TradingGame #{self.game_number} {self.status.value} {self.current_multiplier}x>"

"""
User model for balance tracking.
"""
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, List, Optional
from uuid import uuid4

from sqlalchemy import String, Numeric, DateTime, func, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.bet import Bet


class User(Base, TimestampMixin):
    """
    User model for tracking balances and authentication.

    Users are identified by their TON wallet address or internal user ID.
    """

    __tablename__ = "users"

    # Primary key
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    # Wallet address (optional, for TON integration)
    wallet_address: Mapped[Optional[str]] = mapped_column(
        String(68),  # TON address format
        unique=True,
        nullable=True,
        index=True,
    )

    # Username (optional, for display)
    username: Mapped[Optional[str]] = mapped_column(
        String(64),
        nullable=True,
    )

    # Balance in TON (with high precision)
    balance: Mapped[Decimal] = mapped_column(
        Numeric(precision=18, scale=9),  # Up to 18 digits, 9 decimal places
        default=Decimal("0"),
        nullable=False,
    )

    # Statistics
    total_wagered: Mapped[Decimal] = mapped_column(
        Numeric(precision=18, scale=9),
        default=Decimal("0"),
        nullable=False,
    )
    total_won: Mapped[Decimal] = mapped_column(
        Numeric(precision=18, scale=9),
        default=Decimal("0"),
        nullable=False,
    )
    games_played: Mapped[int] = mapped_column(
        default=0,
        nullable=False,
    )
    games_won: Mapped[int] = mapped_column(
        default=0,
        nullable=False,
    )

    # Last activity
    last_active_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Relationships
    bets: Mapped[List["Bet"]] = relationship(
        "Bet",
        back_populates="user",
        lazy="selectin",
    )

    # Indexes
    __table_args__ = (
        Index("ix_users_balance", "balance"),
        Index("ix_users_last_active", "last_active_at"),
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, balance={self.balance})>"

    @property
    def net_profit(self) -> Decimal:
        """Calculate net profit/loss."""
        return self.total_won - self.total_wagered

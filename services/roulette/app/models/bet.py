"""RouletteBet model."""
from datetime import datetime
from typing import Optional, TYPE_CHECKING
import enum

from sqlalchemy import String, Integer, Numeric, DateTime, Enum, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
import uuid

from app.database import Base
from app.models.base import TimestampMixin

if TYPE_CHECKING:
    from app.models.game import RouletteGame


class BetType(str, enum.Enum):
    """Types of roulette bets."""
    STRAIGHT = "straight"  # Single number (35:1)
    SPLIT = "split"  # Two numbers (17:1)
    STREET = "street"  # Three numbers (11:1)
    CORNER = "corner"  # Four numbers (8:1)
    LINE = "line"  # Six numbers (5:1)
    COLUMN = "column"  # Column (2:1)
    DOZEN = "dozen"  # 1-12, 13-24, 25-36 (2:1)
    RED = "red"  # Red (1:1)
    BLACK = "black"  # Black (1:1)
    ODD = "odd"  # Odd (1:1)
    EVEN = "even"  # Even (1:1)
    LOW = "low"  # 1-18 (1:1)
    HIGH = "high"  # 19-36 (1:1)


class BetStatus(str, enum.Enum):
    """Bet status."""
    ACTIVE = "active"  # Waiting for result
    WON = "won"  # Bet won
    LOST = "lost"  # Bet lost


class RouletteBet(Base, TimestampMixin):
    """Roulette bet model."""

    __tablename__ = "roulette_bets"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Relations
    game_id: Mapped[int] = mapped_column(
        ForeignKey("roulette_games.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)  # Telegram user ID
    
    # Bet details
    bet_type: Mapped[BetType] = mapped_column(Enum(BetType), nullable=False)
    bet_value: Mapped[str] = mapped_column(String(100), nullable=False)  # Number(s) or color/parity
    bet_amount_ton: Mapped[Numeric] = mapped_column(Numeric(18, 9), nullable=False)
    
    # Payout
    payout_multiplier: Mapped[Numeric] = mapped_column(Numeric(5, 2), nullable=False)
    profit_ton: Mapped[Numeric] = mapped_column(Numeric(18, 9), default=0)
    
    # Status
    status: Mapped[BetStatus] = mapped_column(
        Enum(BetStatus),
        default=BetStatus.ACTIVE,
        nullable=False,
        index=True,
    )
    
    # Relationships
    game: Mapped["RouletteGame"] = relationship("RouletteGame", back_populates="bets")

    def __repr__(self) -> str:
        return f"<RouletteBet {self.bet_type.value}:{self.bet_value} {self.bet_amount_ton} TON>"

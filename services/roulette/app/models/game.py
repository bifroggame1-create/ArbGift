"""RouletteGame model."""
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
import enum

from sqlalchemy import String, Integer, Numeric, DateTime, Enum, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import TimestampMixin

if TYPE_CHECKING:
    from app.models.bet import RouletteBet


class GameStatus(str, enum.Enum):
    """Roulette game status."""
    PENDING = "pending"  # Accepting bets
    SPINNING = "spinning"  # Wheel is spinning
    COMPLETED = "completed"  # Game finished, results calculated


class RouletteGame(Base, TimestampMixin):
    """Roulette game model."""

    __tablename__ = "roulette_games"

    id: Mapped[int] = mapped_column(primary_key=True)
    game_number: Mapped[int] = mapped_column(Integer, unique=True, nullable=False, index=True)
    
    # Game state
    status: Mapped[GameStatus] = mapped_column(
        Enum(GameStatus),
        default=GameStatus.PENDING,
        nullable=False,
        index=True,
    )
    
    # Result
    winning_number: Mapped[Optional[int]] = mapped_column(Integer)
    winning_color: Mapped[Optional[str]] = mapped_column(String(10))  # red, black, green
    
    # Provably fair
    server_seed_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    server_seed: Mapped[Optional[str]] = mapped_column(String(128))  # Revealed after game
    client_seed: Mapped[Optional[str]] = mapped_column(String(128))
    nonce: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # Timing
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    # Stats
    total_bets: Mapped[int] = mapped_column(Integer, default=0)
    total_volume_ton: Mapped[Numeric] = mapped_column(Numeric(18, 9), default=0)
    total_payout_ton: Mapped[Numeric] = mapped_column(Numeric(18, 9), default=0)
    
    # Relationships
    bets: Mapped[List["RouletteBet"]] = relationship(
        "RouletteBet",
        back_populates="game",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<RouletteGame #{self.game_number} {self.status.value}>"

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import enum
import uuid

Base = declarative_base()


class GameStatus(str, enum.Enum):
    PENDING = "pending"
    ACTIVE = "active"
    CRASHED = "crashed"
    COMPLETED = "completed"


class TradingGame(Base):
    __tablename__ = "trading_games"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    game_number = Column(Integer, unique=True, nullable=False, index=True)

    # Game state
    status = Column(Enum(GameStatus), default=GameStatus.PENDING, nullable=False, index=True)
    current_multiplier = Column(Float, default=1.0, nullable=False)
    crash_point = Column(Float, nullable=True)  # Pre-determined crash point

    # Provably fair
    server_seed_hash = Column(String(64), nullable=False)
    server_seed = Column(String(128), nullable=True)  # Revealed after crash
    nonce = Column(Integer, nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    started_at = Column(DateTime, nullable=True)
    crashed_at = Column(DateTime, nullable=True)

    # Meta
    total_bets = Column(Integer, default=0)
    total_volume = Column(Float, default=0.0)

    def __repr__(self):
        return f"<TradingGame #{self.game_number} {self.status.value} {self.current_multiplier}x>"

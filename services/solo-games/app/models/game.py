from sqlalchemy import Column, Integer, String, Float, DateTime, Enum, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import enum
import uuid

Base = declarative_base()


class GameType(str, enum.Enum):
    PLINKO = "solo_plinko"
    GONKA = "solo_race"
    ESCAPE = "solo_escape"


class GameResult(Base):
    __tablename__ = "solo_game_results"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Identifiers
    user_id = Column(String, nullable=False, index=True)
    game_type = Column(Enum(GameType), nullable=False, index=True)

    # Bet
    bet_amount = Column(Float, nullable=False)
    multiplier = Column(Float, nullable=False)
    payout = Column(Float, nullable=False)
    profit = Column(Float, nullable=False)

    # Result data (game-specific)
    result_data = Column(JSON, nullable=False)
    # Plinko: { "landing_slot": int, "path": [...] }
    # Gonka: { "cell_index": int, "mode": "lite|hard" }
    # Escape: { "escaped": bool, "duration_ms": int }

    # Provably fair
    server_seed_hash = Column(String(64), nullable=False)
    server_seed = Column(String(128), nullable=False)
    client_seed = Column(String(64), nullable=True)
    nonce = Column(Integer, nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<GameResult {self.game_type.value} {self.bet_amount}x{self.multiplier}={self.payout}>"

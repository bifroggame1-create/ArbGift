from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
import uuid

from .game import Base


class BetStatus(str, enum.Enum):
    ACTIVE = "active"
    CASHED_OUT = "cashed_out"
    LOST = "lost"


class Bet(Base):
    __tablename__ = "trading_bets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Relations
    game_id = Column(UUID(as_uuid=True), ForeignKey('trading_games.id'), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Bet details
    bet_amount = Column(Float, nullable=False)
    cash_out_multiplier = Column(Float, nullable=True)
    profit = Column(Float, default=0.0)

    # Status
    status = Column(Enum(BetStatus), default=BetStatus.ACTIVE, nullable=False, index=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    cashed_out_at = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<Bet {self.bet_amount} TON @ {self.cash_out_multiplier}x = {self.profit} TON>"

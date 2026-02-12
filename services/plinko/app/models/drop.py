from sqlalchemy import Column, Integer, String, Float, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

from app.database import Base


class PlinkoDrop(Base):
    __tablename__ = "plinko_drops"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # User (Telegram ID as string)
    user_id = Column(String(32), nullable=False, index=True)

    # Game params
    risk_level = Column(String(10), nullable=False, default="medium")
    row_count = Column(Integer, nullable=False, default=12)
    currency = Column(String(10), nullable=False, default="stars")

    # Bet details
    bet_amount = Column(Float, nullable=False)

    # Result
    landing_slot = Column(Integer, nullable=False)
    multiplier = Column(Float, nullable=False)
    payout = Column(Float, nullable=False)
    profit = Column(Float, nullable=False)

    # Physics path (for animation replay)
    path = Column(JSON, nullable=False)

    # Provably fair
    server_seed_hash = Column(String(64), nullable=False)
    server_seed = Column(String(128), nullable=False)
    client_seed = Column(String(64), nullable=False)
    nonce = Column(Integer, nullable=False)

    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    def __repr__(self):
        return f"<PlinkoDrop {self.bet_amount} Stars @ {self.multiplier}x = {self.payout}>"

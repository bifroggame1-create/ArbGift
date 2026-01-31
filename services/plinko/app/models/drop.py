from sqlalchemy import Column, Integer, String, Float, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()


class PlinkoDrop(Base):
    __tablename__ = "plinko_drops"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # User
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Bet details
    bet_amount = Column(Float, nullable=False)

    # Result
    landing_slot = Column(Integer, nullable=False)  # 0-8 (9 slots)
    multiplier = Column(Float, nullable=False)
    payout = Column(Float, nullable=False)
    profit = Column(Float, nullable=False)

    # Physics path (for animation replay)
    path = Column(JSON, nullable=False)  # Array of x,y positions

    # Provably fair
    server_seed_hash = Column(String(64), nullable=False)
    server_seed = Column(String(128), nullable=False)
    client_seed = Column(String(64), nullable=False)
    nonce = Column(Integer, nullable=False)

    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<PlinkoDrop {self.bet_amount} TON @ {self.multiplier}x = {self.payout} TON>"

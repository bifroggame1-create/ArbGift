import enum
from decimal import Decimal
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, String, Enum, Integer, Boolean, DECIMAL, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from .base import Base, TimestampMixin


class UpgradeStatus(str, enum.Enum):
    """Upgrade execution status"""

    PENDING = "pending"  # Created but not spun
    SUCCESS = "success"  # Spun and won
    FAILED = "failed"  # Spun and lost


class Upgrade(Base, TimestampMixin):
    """Upgrade model for gift transformation game"""

    __tablename__ = "upgrades"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)

    # Input/Target gifts (from main app NFT table)
    input_gift_id = Column(Integer, nullable=False)
    input_gift_value_ton = Column(DECIMAL(18, 9), nullable=False)

    target_gift_id = Column(Integer, nullable=False)
    target_gift_value_ton = Column(DECIMAL(18, 9), nullable=False)

    # Probability calculation
    value_difference = Column(DECIMAL(18, 9), nullable=False)  # target - input
    success_probability = Column(DECIMAL(5, 4), nullable=False)  # 0.0000-1.0000

    # Result
    status = Column(
        Enum(UpgradeStatus), nullable=False, default=UpgradeStatus.PENDING, index=True
    )
    won = Column(Boolean, nullable=True)  # Null until spun

    # Provably fair data
    server_seed_hash = Column(String(64), nullable=False)
    server_seed = Column(String(128), nullable=True)  # Revealed after spin
    client_seed = Column(String(64), nullable=False)
    nonce = Column(Integer, nullable=False, default=1)

    # Result angle (0-360 degrees) for wheel animation
    result_angle = Column(DECIMAL(6, 2), nullable=True)

    # Timestamps
    resolved_at = Column(TIMESTAMP, nullable=True)

    # Relationship
    user = relationship("User", back_populates="upgrades")

    @property
    def value_ratio(self) -> Decimal:
        """Calculate value ratio (target / input)"""
        if self.input_gift_value_ton == 0:
            return Decimal("0")
        return self.target_gift_value_ton / self.input_gift_value_ton

    def __repr__(self):
        return f"<Upgrade {self.id} - {self.status.value} - {float(self.success_probability) * 100:.1f}%>"

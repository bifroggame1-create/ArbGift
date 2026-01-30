import enum
from decimal import Decimal
from typing import Optional
from datetime import datetime

from sqlalchemy import Column, String, Enum, Integer, Boolean, DECIMAL, TIMESTAMP, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from .base import Base, TimestampMixin


class RiskLevel(str, enum.Enum):
    """Risk level for contracts"""

    SAFE = "safe"  # x2 multiplier, 45% chance
    NORMAL = "normal"  # x8 multiplier, 11% chance
    RISKY = "risky"  # x100 multiplier, 0.9% chance


class ContractStatus(str, enum.Enum):
    """Contract execution status"""

    PENDING = "pending"  # Created but not executed
    SUCCESS = "success"  # Executed and won
    FAILED = "failed"  # Executed and lost


class Contract(Base, TimestampMixin):
    """Contract model for risk-based gift gambling"""

    __tablename__ = "contracts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)

    # Risk configuration
    risk_level = Column(Enum(RiskLevel), nullable=False, index=True)

    # Input gifts (from main app NFT table)
    input_gift_ids = Column(JSON, nullable=False)  # Array of gift IDs
    total_input_value_ton = Column(DECIMAL(18, 9), nullable=False)

    # Result
    status = Column(
        Enum(ContractStatus), nullable=False, default=ContractStatus.PENDING, index=True
    )
    won = Column(Boolean, nullable=True)  # Null until executed
    payout_multiplier = Column(DECIMAL(10, 2), nullable=True)
    payout_value_ton = Column(DECIMAL(18, 9), nullable=True)
    reward_gift_id = Column(Integer, nullable=True)  # FK to main app NFT table

    # Provably fair data
    server_seed_hash = Column(String(64), nullable=False)  # SHA-256 hash shown to client
    server_seed = Column(
        String(128), nullable=True
    )  # Revealed after execution for verification
    client_seed = Column(String(64), nullable=False)  # Provided by client
    nonce = Column(Integer, nullable=False, default=1)  # Incrementing nonce

    # Timestamps
    resolved_at = Column(TIMESTAMP, nullable=True)  # When contract was executed

    # Relationship
    user = relationship("User", back_populates="contracts")

    def __repr__(self):
        return f"<Contract {self.id} - {self.risk_level.value} - {self.status.value}>"

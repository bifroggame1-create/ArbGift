from decimal import Decimal
from sqlalchemy import Column, BigInteger, String, Integer, DECIMAL
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from .base import Base, TimestampMixin


class User(Base, TimestampMixin):
    """User model for Upgrade game service"""

    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    telegram_id = Column(BigInteger, unique=True, nullable=False, index=True)
    username = Column(String(255), nullable=True)

    # Upgrade statistics
    total_upgrades = Column(Integer, nullable=False, default=0)
    upgrades_won = Column(Integer, nullable=False, default=0)
    total_value_risked_ton = Column(DECIMAL(18, 9), nullable=False, default=Decimal("0"))
    total_value_won_ton = Column(DECIMAL(18, 9), nullable=False, default=Decimal("0"))

    # Relationships
    upgrades = relationship("Upgrade", back_populates="user", lazy="dynamic")

    @property
    def win_rate(self) -> float:
        """Calculate win rate percentage"""
        if self.total_upgrades == 0:
            return 0.0
        return (self.upgrades_won / self.total_upgrades) * 100

    @property
    def net_profit_ton(self) -> Decimal:
        """Calculate net profit/loss"""
        return self.total_value_won_ton - self.total_value_risked_ton

    def __repr__(self):
        return f"<User {self.telegram_id} - {self.total_upgrades} upgrades>"

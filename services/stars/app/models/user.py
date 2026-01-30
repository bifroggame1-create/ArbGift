"""
User model for storing Telegram user data and stars balance.
"""

from sqlalchemy import Column, BigInteger, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from typing import Optional

from .base import Base


class User(Base):
    """
    User model representing a Telegram user in the system.

    Attributes:
        telegram_id: Unique Telegram user ID
        username: Telegram username (optional)
        first_name: User's first name
        last_name: User's last name (optional)
        stars_balance: Current balance of purchased stars
        total_stars_purchased: Total stars ever purchased
        is_active: Whether user is active
        created_at: Account creation timestamp
        updated_at: Last update timestamp
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False, index=True)
    username = Column(String(255), nullable=True)
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)

    # Stars tracking
    stars_balance = Column(Integer, default=0, nullable=False)
    total_stars_purchased = Column(Integer, default=0, nullable=False)

    # Status
    is_active = Column(Boolean, default=True, nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    orders = relationship("Order", back_populates="user", lazy="selectin")

    def __repr__(self) -> str:
        return f"<User(telegram_id={self.telegram_id}, username={self.username})>"

    @property
    def full_name(self) -> str:
        """Get user's full name."""
        parts = []
        if self.first_name:
            parts.append(self.first_name)
        if self.last_name:
            parts.append(self.last_name)
        return " ".join(parts) if parts else f"User {self.telegram_id}"

    def add_stars(self, amount: int) -> None:
        """
        Add stars to user's balance.

        Args:
            amount: Number of stars to add
        """
        self.stars_balance += amount
        self.total_stars_purchased += amount

    def deduct_stars(self, amount: int) -> bool:
        """
        Deduct stars from user's balance.

        Args:
            amount: Number of stars to deduct

        Returns:
            bool: True if deduction successful, False if insufficient balance
        """
        if self.stars_balance >= amount:
            self.stars_balance -= amount
            return True
        return False

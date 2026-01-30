"""
Order model for tracking star purchase orders.
"""

from sqlalchemy import Column, Integer, BigInteger, String, DateTime, Numeric, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from decimal import Decimal
from datetime import datetime, timedelta
from typing import Optional
import enum
import uuid

from .base import Base
from app.config import settings


class OrderStatus(str, enum.Enum):
    """Order status enumeration."""
    PENDING = "pending"          # Order created, awaiting payment
    AWAITING_PAYMENT = "awaiting_payment"  # Payment address generated
    PAYMENT_RECEIVED = "payment_received"  # TON payment confirmed
    PROCESSING = "processing"    # Stars being delivered
    COMPLETED = "completed"      # Stars delivered successfully
    FAILED = "failed"           # Order failed
    EXPIRED = "expired"         # Payment timeout
    REFUNDED = "refunded"       # Payment refunded


class Order(Base):
    """
    Order model for tracking Telegram Stars purchases.

    Attributes:
        id: Unique order ID
        order_uuid: Public UUID for order tracking
        user_id: Foreign key to User
        telegram_id: Telegram user ID (for quick lookups)
        stars_amount: Number of stars to purchase
        ton_price: Price in TON
        usd_price: Price in USD (for reference)
        status: Current order status
        tx_hash: TON transaction hash (after payment)
        invoice_url: Telegram invoice URL
        payment_address: TON payment address
        payment_memo: Payment memo for identification
        expires_at: Order expiration time
        paid_at: Payment confirmation time
        completed_at: Stars delivery completion time
        created_at: Order creation time
        updated_at: Last update time
    """

    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_uuid = Column(String(36), unique=True, nullable=False, index=True, default=lambda: str(uuid.uuid4()))

    # User reference
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    telegram_id = Column(BigInteger, nullable=False, index=True)

    # Order details
    stars_amount = Column(Integer, nullable=False)
    ton_price = Column(Numeric(precision=18, scale=9), nullable=False)
    usd_price = Column(Numeric(precision=10, scale=2), nullable=True)

    # Status tracking
    status = Column(
        SQLEnum(OrderStatus),
        default=OrderStatus.PENDING,
        nullable=False,
        index=True
    )

    # Payment details
    tx_hash = Column(String(64), nullable=True, unique=True, index=True)
    invoice_url = Column(String(512), nullable=True)
    payment_address = Column(String(48), nullable=True)
    payment_memo = Column(String(64), nullable=True, unique=True)

    # Timestamps
    expires_at = Column(DateTime(timezone=True), nullable=True)
    paid_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Error tracking
    error_message = Column(String(512), nullable=True)
    retry_count = Column(Integer, default=0, nullable=False)

    # Relationships
    user = relationship("User", back_populates="orders")

    def __repr__(self) -> str:
        return f"<Order(uuid={self.order_uuid}, stars={self.stars_amount}, status={self.status})>"

    @classmethod
    def create_order(
        cls,
        user_id: int,
        telegram_id: int,
        stars_amount: int,
        ton_price: Decimal,
        usd_price: Optional[Decimal] = None,
    ) -> "Order":
        """
        Factory method to create a new order.

        Args:
            user_id: Database user ID
            telegram_id: Telegram user ID
            stars_amount: Number of stars to purchase
            ton_price: Price in TON
            usd_price: Price in USD (optional)

        Returns:
            Order: New order instance
        """
        expiry_time = datetime.utcnow() + timedelta(minutes=settings.PAYMENT_TIMEOUT_MINUTES)

        return cls(
            user_id=user_id,
            telegram_id=telegram_id,
            stars_amount=stars_amount,
            ton_price=ton_price,
            usd_price=usd_price,
            status=OrderStatus.PENDING,
            expires_at=expiry_time,
            payment_memo=f"STARS-{uuid.uuid4().hex[:12].upper()}",
        )

    def mark_awaiting_payment(self, payment_address: str, invoice_url: Optional[str] = None) -> None:
        """Mark order as awaiting payment."""
        self.status = OrderStatus.AWAITING_PAYMENT
        self.payment_address = payment_address
        if invoice_url:
            self.invoice_url = invoice_url

    def mark_payment_received(self, tx_hash: str) -> None:
        """Mark order as payment received."""
        self.status = OrderStatus.PAYMENT_RECEIVED
        self.tx_hash = tx_hash
        self.paid_at = datetime.utcnow()

    def mark_processing(self) -> None:
        """Mark order as processing (delivering stars)."""
        self.status = OrderStatus.PROCESSING

    def mark_completed(self) -> None:
        """Mark order as completed."""
        self.status = OrderStatus.COMPLETED
        self.completed_at = datetime.utcnow()

    def mark_failed(self, error_message: str) -> None:
        """Mark order as failed."""
        self.status = OrderStatus.FAILED
        self.error_message = error_message

    def mark_expired(self) -> None:
        """Mark order as expired."""
        self.status = OrderStatus.EXPIRED

    @property
    def is_expired(self) -> bool:
        """Check if order has expired."""
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at

    @property
    def is_payable(self) -> bool:
        """Check if order can still be paid."""
        return (
            self.status in [OrderStatus.PENDING, OrderStatus.AWAITING_PAYMENT]
            and not self.is_expired
        )

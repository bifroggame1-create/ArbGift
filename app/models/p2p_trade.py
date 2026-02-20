"""P2P Trade model for internal gift marketplace."""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional, TYPE_CHECKING

from sqlalchemy import (
    String,
    Numeric,
    DateTime,
    Integer,
    Boolean,
    ForeignKey,
    Enum as SAEnum,
    Index,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.inventory import UserGiftInventory


class TradeStatus(str, Enum):
    """Status of P2P trade listing."""
    ACTIVE = "active"  # Listed and available for purchase
    SOLD = "sold"  # Successfully sold
    CANCELLED = "cancelled"  # Cancelled by seller
    EXPIRED = "expired"  # Expired (if we add time limits)


class P2PTrade(Base):
    """
    P2P Gift NFT marketplace listing.

    Users can list their inventory gifts for sale to other users.
    Trades are settled internally without blockchain transactions.
    """
    __tablename__ = "p2p_trades"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Seller
    seller_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    inventory_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("user_gift_inventory.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Pricing
    price_ton: Mapped[Decimal] = mapped_column(
        Numeric(18, 9),
        nullable=False,
        index=True,
    )
    price_stars: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(18, 2),
        nullable=True,
    )

    # Pricing metadata
    floor_price_ton: Mapped[Decimal] = mapped_column(
        Numeric(18, 9),
        default=Decimal("0"),
    )
    discount_percent: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 2),
        nullable=True,
    )

    # Buyer (when sold)
    buyer_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Status
    status: Mapped[TradeStatus] = mapped_column(
        SAEnum(TradeStatus),
        default=TradeStatus.ACTIVE,
        index=True,
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        index=True,
    )
    sold_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    cancelled_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        onupdate=func.now(),
    )

    # Features
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False)
    views_count: Mapped[int] = mapped_column(Integer, default=0)

    # Relationships
    seller: Mapped["User"] = relationship("User", foreign_keys=[seller_id], back_populates="p2p_listings")
    buyer: Mapped[Optional["User"]] = relationship("User", foreign_keys=[buyer_id])
    inventory_item: Mapped["UserGiftInventory"] = relationship("UserGiftInventory")

    __table_args__ = (
        # Fast queries for active listings
        Index("ix_p2p_active_listings", "status", "created_at"),
        # Fast queries by price
        Index("ix_p2p_price_range", "status", "price_ton"),
        # Fast queries for user's listings
        Index("ix_p2p_seller_listings", "seller_id", "status"),
    )

    @property
    def is_active(self) -> bool:
        """Check if listing is active."""
        return self.status == TradeStatus.ACTIVE

    @property
    def is_sold(self) -> bool:
        """Check if listing was sold."""
        return self.status == TradeStatus.SOLD

    def __repr__(self) -> str:
        return f"<P2PTrade id={self.id} seller_id={self.seller_id} price={self.price_ton} status={self.status}>"

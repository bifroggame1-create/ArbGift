"""Listing model."""
from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlalchemy import String, Boolean, Numeric, DateTime, ForeignKey, func, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.nft import NFT
    from app.models.market import Market


class Listing(Base):
    """Active marketplace listing model."""

    __tablename__ = "listings"

    id: Mapped[int] = mapped_column(primary_key=True)
    nft_id: Mapped[int] = mapped_column(
        ForeignKey("nfts.id", ondelete="CASCADE"),
        nullable=False,
    )
    market_id: Mapped[int] = mapped_column(
        ForeignKey("markets.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Market-specific ID
    market_listing_id: Mapped[str] = mapped_column(String(200), nullable=False)

    # Pricing
    price_raw: Mapped[Numeric] = mapped_column(Numeric(24, 9), nullable=False)
    currency: Mapped[str] = mapped_column(String(20), nullable=False, default="TON")
    price_ton: Mapped[Numeric] = mapped_column(Numeric(18, 9), nullable=False, index=True)

    # Seller
    seller_address: Mapped[Optional[str]] = mapped_column(String(66))

    # URLs
    listing_url: Mapped[Optional[str]] = mapped_column(String(500))

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    listed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Sync tracking
    last_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    first_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        onupdate=func.now(),
    )

    # Relationships
    nft: Mapped["NFT"] = relationship("NFT", back_populates="listings")
    market: Mapped["Market"] = relationship("Market", back_populates="listings")

    # Constraints
    __table_args__ = (
        UniqueConstraint("market_id", "market_listing_id", name="uq_listings_market_nft"),
    )

    def __repr__(self) -> str:
        return f"<Listing {self.market_listing_id} on market {self.market_id}>"

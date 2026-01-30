"""NFT model."""
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING

from sqlalchemy import String, Text, Boolean, Integer, Numeric, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.collection import Collection
    from app.models.listing import Listing


class NFT(Base):
    """NFT item model."""

    __tablename__ = "nfts"

    id: Mapped[int] = mapped_column(primary_key=True)
    address: Mapped[str] = mapped_column(String(66), unique=True, nullable=False, index=True)
    collection_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("collections.id", ondelete="CASCADE"),
        nullable=False,
    )
    index: Mapped[Optional[int]] = mapped_column(Integer)

    # Basic info
    name: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)

    # Media
    image_url: Mapped[Optional[str]] = mapped_column(String(500))
    image_cdn_url: Mapped[Optional[str]] = mapped_column(String(500))
    animation_url: Mapped[Optional[str]] = mapped_column(String(500))
    animation_cdn_url: Mapped[Optional[str]] = mapped_column(String(500))

    # Denormalized attributes for search
    rarity: Mapped[Optional[str]] = mapped_column(String(50), index=True)
    backdrop: Mapped[Optional[str]] = mapped_column(String(100))
    model: Mapped[Optional[str]] = mapped_column(String(100))
    symbol: Mapped[Optional[str]] = mapped_column(String(100))
    pattern: Mapped[Optional[str]] = mapped_column(String(100))

    # Full attributes
    attributes: Mapped[Optional[List[dict]]] = mapped_column(JSONB, default=[])

    # Owner
    owner_address: Mapped[Optional[str]] = mapped_column(String(66), index=True)

    # Sale status (denormalized)
    is_on_sale: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    lowest_price_ton: Mapped[Optional[Numeric]] = mapped_column(Numeric(18, 9))
    lowest_price_market: Mapped[Optional[str]] = mapped_column(String(50))

    # Raw data
    raw_metadata: Mapped[Optional[dict]] = mapped_column(JSONB)
    metadata_url: Mapped[Optional[str]] = mapped_column(String(500))
    metadata_resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

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
    collection: Mapped["Collection"] = relationship(
        "Collection",
        back_populates="nfts",
    )
    listings: Mapped[List["Listing"]] = relationship(
        "Listing",
        back_populates="nft",
        lazy="dynamic",
    )

    def __repr__(self) -> str:
        return f"<NFT {self.name} ({self.address[:8]}...)>"

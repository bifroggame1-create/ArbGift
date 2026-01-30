"""Collection model."""
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING

from sqlalchemy import String, Text, Boolean, Integer, Numeric, DateTime, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.nft import NFT


class Collection(Base):
    """NFT Collection model."""

    __tablename__ = "collections"

    id: Mapped[int] = mapped_column(primary_key=True)
    address: Mapped[str] = mapped_column(String(66), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[Optional[str]] = mapped_column(String(100), unique=True, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    image_url: Mapped[Optional[str]] = mapped_column(String(500))
    cover_url: Mapped[Optional[str]] = mapped_column(String(500))
    external_url: Mapped[Optional[str]] = mapped_column(String(500))

    # Stats
    total_items: Mapped[int] = mapped_column(Integer, default=0)
    owners_count: Mapped[int] = mapped_column(Integer, default=0)
    floor_price_ton: Mapped[Optional[Numeric]] = mapped_column(Numeric(18, 9))
    total_volume_ton: Mapped[Optional[Numeric]] = mapped_column(Numeric(18, 9), default=0)
    volume_24h_ton: Mapped[Optional[Numeric]] = mapped_column(Numeric(18, 9), default=0)

    # Flags
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    is_telegram_gift: Mapped[bool] = mapped_column(Boolean, default=False)

    # Raw data
    raw_metadata: Mapped[Optional[dict]] = mapped_column(JSONB)

    # Indexing state
    last_indexed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    indexing_status: Mapped[str] = mapped_column(String(20), default="pending")

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
    nfts: Mapped[List["NFT"]] = relationship(
        "NFT",
        back_populates="collection",
        lazy="dynamic",
    )

    def __repr__(self) -> str:
        return f"<Collection {self.name} ({self.address[:8]}...)>"

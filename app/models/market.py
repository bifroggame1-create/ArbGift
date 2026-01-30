"""Market model."""
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING

from sqlalchemy import String, Boolean, Integer, Numeric, DateTime, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.listing import Listing


class Market(Base):
    """Marketplace model."""

    __tablename__ = "markets"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    website_url: Mapped[Optional[str]] = mapped_column(String(255))
    api_base_url: Mapped[Optional[str]] = mapped_column(String(255))

    # Fees (percentage, 0-100)
    fee_buy_percent: Mapped[Numeric] = mapped_column(Numeric(5, 2), default=0)
    fee_sell_percent: Mapped[Numeric] = mapped_column(Numeric(5, 2), default=0)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    priority: Mapped[int] = mapped_column(Integer, default=0)

    # Adapter config
    config: Mapped[Optional[dict]] = mapped_column(JSONB, default={})

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
    listings: Mapped[List["Listing"]] = relationship(
        "Listing",
        back_populates="market",
        lazy="dynamic",
    )

    def __repr__(self) -> str:
        return f"<Market {self.name} ({self.slug})>"

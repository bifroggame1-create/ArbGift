"""Sale model."""
from datetime import datetime
from typing import Optional

from sqlalchemy import String, BigInteger, Numeric, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Sale(Base):
    """Completed sale model."""

    __tablename__ = "sales"

    id: Mapped[int] = mapped_column(primary_key=True)
    nft_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("nfts.id", ondelete="SET NULL"),
    )
    collection_id: Mapped[int] = mapped_column(
        ForeignKey("collections.id", ondelete="CASCADE"),
        nullable=False,
    )
    market_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("markets.id", ondelete="SET NULL"),
    )

    # NFT snapshot
    nft_address: Mapped[str] = mapped_column(String(66), nullable=False, index=True)
    nft_name: Mapped[Optional[str]] = mapped_column(String(300))

    # Pricing
    price_raw: Mapped[Numeric] = mapped_column(Numeric(24, 9), nullable=False)
    currency: Mapped[str] = mapped_column(String(20), nullable=False)
    price_ton: Mapped[Numeric] = mapped_column(Numeric(18, 9), nullable=False, index=True)

    # Parties
    buyer_address: Mapped[Optional[str]] = mapped_column(String(66))
    seller_address: Mapped[Optional[str]] = mapped_column(String(66))

    # Transaction
    tx_hash: Mapped[Optional[str]] = mapped_column(String(66), unique=True, index=True)
    tx_lt: Mapped[Optional[int]] = mapped_column(BigInteger)

    # Timestamps
    sold_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    def __repr__(self) -> str:
        return f"<Sale {self.nft_address[:8]}... for {self.price_ton} TON>"

"""User Gift Inventory model."""
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
    from app.models.nft import NFT


class GiftAcquisitionSource(str, Enum):
    """How user acquired the gift."""
    MARKET_PURCHASE = "market_purchase"  # Bought from external marketplace
    GAME_WIN = "game_win"  # Won from game (PvP, Contracts, etc)
    TRANSFER_RECEIVED = "transfer_received"  # Received from another user
    P2P_TRADE = "p2p_trade"  # Internal P2P market trade
    ADMIN_GRANT = "admin_grant"  # Granted by admin
    REFERRAL_REWARD = "referral_reward"  # Referral program reward
    QUEST_REWARD = "quest_reward"  # Quest/achievement reward
    TELEGRAM_IMPORT = "telegram_import"  # Imported from Telegram via MTProto


class UserGiftInventory(Base):
    """
    User's Gift NFT inventory.

    Tracks which users own which Gift NFTs for use in games and P2P trading.
    Links Telegram Gift ownership with platform gameplay.
    """
    __tablename__ = "user_gift_inventory"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Ownership
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    gift_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("nfts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Telegram Gift identifiers (from MTProto API)
    telegram_msg_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)
    telegram_saved_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    telegram_slug: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)

    # Acquisition info
    acquired_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    source: Mapped[GiftAcquisitionSource] = mapped_column(
        SAEnum(GiftAcquisitionSource),
        default=GiftAcquisitionSource.TELEGRAM_IMPORT,
    )
    acquisition_details: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Cached floor price at acquisition time (for historical tracking)
    floor_price_ton_at_acquisition: Mapped[Decimal] = mapped_column(
        Numeric(18, 9),
        default=Decimal("0"),
    )

    # Current floor price (cached from collection, updated periodically)
    current_floor_price_ton: Mapped[Decimal] = mapped_column(
        Numeric(18, 9),
        default=Decimal("0"),
    )
    last_price_update_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Status flags
    is_staked: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    is_locked: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    locked_reason: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    locked_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Transferability
    is_transferable: Mapped[bool] = mapped_column(Boolean, default=True)
    transfer_fee_stars: Mapped[int] = mapped_column(Integer, default=0)

    # Timestamps
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        onupdate=func.now(),
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="gift_inventory")
    gift: Mapped["NFT"] = relationship("NFT")

    __table_args__ = (
        # Prevent duplicate ownership
        Index("ix_user_gift_unique", "user_id", "gift_id", unique=True),
        # Fast queries for locked/staked items
        Index("ix_inventory_status", "user_id", "is_locked", "is_staked"),
        # Fast queries by Telegram identifiers
        Index("ix_telegram_identifiers", "telegram_msg_id", "telegram_slug"),
    )

    @property
    def is_available_for_betting(self) -> bool:
        """Check if gift can be used for game betting."""
        return not self.is_locked and not self.is_staked and self.is_transferable

    @property
    def profit_loss_ton(self) -> Decimal:
        """Calculate profit/loss since acquisition."""
        return self.current_floor_price_ton - self.floor_price_ton_at_acquisition

    def __repr__(self) -> str:
        return f"<UserGiftInventory user_id={self.user_id} gift_id={self.gift_id}>"

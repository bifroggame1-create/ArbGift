"""Gift Transfer Audit Log model."""
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
    Text,
    Enum as SAEnum,
    Index,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.nft import NFT


class TransferReason(str, Enum):
    """Why the gift was transferred."""
    GAME_PAYOUT = "game_payout"  # Winner received gift from game
    P2P_TRADE = "p2p_trade"  # Internal marketplace trade
    MANUAL_TRANSFER = "manual_transfer"  # User-initiated transfer
    ADMIN_TRANSFER = "admin_transfer"  # Admin action
    REFUND = "refund"  # Refund after cancelled game


class TransferStatus(str, Enum):
    """Status of transfer operation."""
    PENDING = "pending"  # Initiated, not yet executed
    TELEGRAM_PENDING = "telegram_pending"  # Waiting for Telegram MTProto confirmation
    COMPLETED = "completed"  # Successfully transferred
    FAILED = "failed"  # Transfer failed
    REVERTED = "reverted"  # Transfer was rolled back


class GiftTransferLog(Base):
    """
    Audit log for all Gift NFT transfers.

    Tracks ownership changes for security, debugging, and dispute resolution.
    Every gift transfer (game wins, trades, manual sends) is logged here.
    """
    __tablename__ = "gift_transfer_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Transfer parties
    from_user_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    to_user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Gift being transferred
    gift_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("nfts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    inventory_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("user_gift_inventory.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Transfer details
    reason: Mapped[TransferReason] = mapped_column(
        SAEnum(TransferReason),
        nullable=False,
        index=True,
    )
    status: Mapped[TransferStatus] = mapped_column(
        SAEnum(TransferStatus),
        default=TransferStatus.PENDING,
        index=True,
    )

    # Gift value at transfer time (for historical tracking)
    gift_value_ton: Mapped[Decimal] = mapped_column(
        Numeric(18, 9),
        default=Decimal("0"),
    )

    # Related entities
    game_round_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)
    trade_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)

    # Telegram MTProto data
    telegram_msg_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    telegram_transaction_hash: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    mtproto_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    mtproto_response: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Error handling
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)

    # Timestamps
    initiated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        onupdate=func.now(),
    )

    # Relationships
    from_user: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[from_user_id],
    )
    to_user: Mapped["User"] = relationship(
        "User",
        foreign_keys=[to_user_id],
    )
    gift: Mapped["NFT"] = relationship("NFT")

    __table_args__ = (
        # Fast queries for user transfer history
        Index("ix_transfer_from_user_created", "from_user_id", "initiated_at"),
        Index("ix_transfer_to_user_created", "to_user_id", "initiated_at"),
        # Fast queries for gift transfer history
        Index("ix_transfer_gift_created", "gift_id", "initiated_at"),
        # Fast queries for pending transfers
        Index("ix_transfer_status_created", "status", "initiated_at"),
    )

    def __repr__(self) -> str:
        return f"<GiftTransferLog from={self.from_user_id} to={self.to_user_id} gift={self.gift_id} status={self.status}>"

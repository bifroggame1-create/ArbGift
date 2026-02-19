from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional, TYPE_CHECKING

from sqlalchemy import String, Numeric, DateTime, Integer, JSON, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.nft import NFT


class OperationStatus(str, Enum):
    PENDING = "pending"
    APPLIED = "applied"
    FAILED = "failed"


class OperationType(str, Enum):
    BET = "bet"
    PAYOUT = "payout"
    REFUND = "refund"
    DEPOSIT = "deposit"
    WITHDRAW = "withdraw"


class BetCurrency(str, Enum):
    """Currency used for betting."""
    TON = "TON"
    STARS = "STARS"
    GIFT = "GIFT"  # Telegram Gift NFT


class BalanceOperation(Base):
    __tablename__ = "balance_operations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    operation_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), index=True)
    op_type: Mapped[OperationType] = mapped_column(SAEnum(OperationType), index=True)
    status: Mapped[OperationStatus] = mapped_column(SAEnum(OperationStatus), default=OperationStatus.PENDING)

    # Traditional currency amounts
    amount_ton: Mapped[Decimal] = mapped_column(Numeric(18, 9), default=Decimal("0"))
    amount_stars: Mapped[int] = mapped_column(Integer, default=0)

    # Gift NFT betting support
    bet_currency: Mapped[BetCurrency] = mapped_column(
        SAEnum(BetCurrency),
        default=BetCurrency.TON,
        index=True,
    )
    gift_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("nfts.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    gift_value_ton: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(18, 9),
        nullable=True,
    )  # Floor price at bet time

    request_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    response_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    user: Mapped["User"] = relationship("User")
    gift: Mapped[Optional["NFT"]] = relationship("NFT")

"""
Gift Inventory API endpoints.

Provides REST API for:
- User gift inventory management
- Gift locking/unlocking for bets
- Gift transfer between users
- Inventory synchronization with Telegram
"""
import logging
from datetime import datetime
from decimal import Decimal
from typing import Optional, List

from fastapi import APIRouter, Depends, Query, HTTPException, Header
from pydantic import BaseModel, Field
from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db_session
from app.core.auth import get_verified_telegram_id
from app.core.ratelimit import limiter
from app.models.user import User
from app.models.nft import NFT
from app.models.collection import Collection
from app.models.inventory import UserGiftInventory, GiftAcquisitionSource
from app.models.gift_transfer_log import GiftTransferLog, TransferReason, TransferStatus

logger = logging.getLogger(__name__)
router = APIRouter()


# ============================================================
# SCHEMAS
# ============================================================

class GiftNFTSchema(BaseModel):
    """Simplified Gift NFT schema."""
    id: int
    address: str
    name: str
    image_url: Optional[str]
    animation_url: Optional[str]
    gift_type: Optional[str]
    rarity: Optional[str]
    backdrop: Optional[str]
    collection_id: int

    class Config:
        from_attributes = True


class CollectionSchema(BaseModel):
    """Simplified Collection schema."""
    id: int
    name: str
    slug: str
    floor_price_ton: Optional[Decimal]

    class Config:
        from_attributes = True


class InventoryItemSchema(BaseModel):
    """User inventory item with gift details."""
    id: int
    user_id: int
    gift_id: int

    # Gift details (joined)
    gift: GiftNFTSchema

    # Telegram identifiers
    telegram_msg_id: Optional[int]
    telegram_slug: Optional[str]

    # Acquisition
    acquired_at: datetime
    source: str
    acquisition_details: Optional[str]

    # Pricing
    floor_price_ton_at_acquisition: Decimal
    current_floor_price_ton: Decimal
    profit_loss_ton: Decimal
    last_price_update_at: Optional[datetime]

    # Status
    is_staked: bool
    is_locked: bool
    locked_reason: Optional[str]
    is_transferable: bool
    transfer_fee_stars: int

    # Computed
    is_available_for_betting: bool

    class Config:
        from_attributes = True


class InventorySummarySchema(BaseModel):
    """User inventory summary statistics."""
    total_gifts: int
    total_value_ton: Decimal
    available_for_betting: int
    staked_count: int
    locked_count: int
    total_profit_loss_ton: Decimal


class AddGiftToInventoryRequest(BaseModel):
    """Add gift to user inventory (admin or MTProto sync)."""
    gift_id: int = Field(..., description="NFT ID")
    telegram_msg_id: Optional[int] = None
    telegram_slug: Optional[str] = None
    source: GiftAcquisitionSource = GiftAcquisitionSource.TELEGRAM_IMPORT
    acquisition_details: Optional[str] = None


class LockGiftRequest(BaseModel):
    """Lock gift for game betting."""
    inventory_id: int = Field(..., description="Inventory item ID")
    reason: str = Field(..., description="Why gift is locked (e.g., 'pvp_bet', 'contract_input')")


class TransferGiftRequest(BaseModel):
    """Transfer gift to another user."""
    inventory_id: int = Field(..., description="Inventory item ID")
    to_user_telegram_id: int = Field(..., description="Recipient Telegram ID")
    reason: TransferReason = TransferReason.MANUAL_TRANSFER


# ============================================================
# HELPERS
# ============================================================

async def get_user_by_telegram_id(
    session: AsyncSession,
    telegram_id: int
) -> Optional[User]:
    """Get user by Telegram ID."""
    result = await session.execute(
        select(User).where(User.telegram_id == telegram_id)
    )
    return result.scalar_one_or_none()


async def update_gift_floor_price(
    session: AsyncSession,
    inventory_item: UserGiftInventory
):
    """Update cached floor price from collection."""
    gift = await session.get(NFT, inventory_item.gift_id)
    if not gift:
        return

    collection = await session.get(Collection, gift.collection_id)
    if not collection or not collection.floor_price_ton:
        return

    inventory_item.current_floor_price_ton = collection.floor_price_ton
    inventory_item.last_price_update_at = datetime.utcnow()


# ============================================================
# ENDPOINTS
# ============================================================

@router.get("/me", response_model=List[InventoryItemSchema])
@limiter.limit("30/minute")
async def get_my_inventory(
    telegram_id: int = Depends(get_verified_telegram_id),
    session: AsyncSession = Depends(get_db_session),
    available_only: bool = Query(False, description="Only show gifts available for betting"),
    update_prices: bool = Query(False, description="Update floor prices before returning"),
):
    """
    Get current user's gift inventory.

    Returns all gifts owned by the user with current floor prices.
    Optionally filter to only available (unlocked, unstaked) gifts.
    """
    user = await get_user_by_telegram_id(session, telegram_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Build query
    query = (
        select(UserGiftInventory)
        .where(UserGiftInventory.user_id == user.id)
        .options(selectinload(UserGiftInventory.gift))
        .order_by(UserGiftInventory.acquired_at.desc())
    )

    if available_only:
        query = query.where(
            and_(
                UserGiftInventory.is_locked == False,
                UserGiftInventory.is_staked == False,
                UserGiftInventory.is_transferable == True,
            )
        )

    result = await session.execute(query)
    items = result.scalars().all()

    # Update prices if requested
    if update_prices:
        for item in items:
            await update_gift_floor_price(session, item)
        await session.commit()

    # Build response with computed fields
    response = []
    for item in items:
        response.append(InventoryItemSchema(
            id=item.id,
            user_id=item.user_id,
            gift_id=item.gift_id,
            gift=GiftNFTSchema.from_orm(item.gift),
            telegram_msg_id=item.telegram_msg_id,
            telegram_slug=item.telegram_slug,
            acquired_at=item.acquired_at,
            source=item.source.value,
            acquisition_details=item.acquisition_details,
            floor_price_ton_at_acquisition=item.floor_price_ton_at_acquisition,
            current_floor_price_ton=item.current_floor_price_ton,
            profit_loss_ton=item.profit_loss_ton,
            last_price_update_at=item.last_price_update_at,
            is_staked=item.is_staked,
            is_locked=item.is_locked,
            locked_reason=item.locked_reason,
            is_transferable=item.is_transferable,
            transfer_fee_stars=item.transfer_fee_stars,
            is_available_for_betting=item.is_available_for_betting,
        ))

    return response


@router.get("/me/summary", response_model=InventorySummarySchema)
async def get_inventory_summary(
    telegram_id: int = Depends(get_verified_telegram_id),
    session: AsyncSession = Depends(get_db_session),
):
    """
    Get inventory summary statistics.

    Returns counts and total value of user's gift inventory.
    """
    user = await get_user_by_telegram_id(session, telegram_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get all inventory items
    result = await session.execute(
        select(UserGiftInventory)
        .where(UserGiftInventory.user_id == user.id)
    )
    items = result.scalars().all()

    # Calculate statistics
    total_gifts = len(items)
    total_value = sum(item.current_floor_price_ton for item in items)
    available = sum(1 for item in items if item.is_available_for_betting)
    staked = sum(1 for item in items if item.is_staked)
    locked = sum(1 for item in items if item.is_locked)
    total_profit_loss = sum(item.profit_loss_ton for item in items)

    return InventorySummarySchema(
        total_gifts=total_gifts,
        total_value_ton=total_value,
        available_for_betting=available,
        staked_count=staked,
        locked_count=locked,
        total_profit_loss_ton=total_profit_loss,
    )


@router.post("/add", response_model=InventoryItemSchema, status_code=201)
@limiter.limit("10/minute")
async def add_gift_to_inventory(
    request: AddGiftToInventoryRequest,
    telegram_id: int = Depends(get_verified_telegram_id),
    session: AsyncSession = Depends(get_db_session),
):
    """
    Add a gift to user's inventory.

    Used by MTProto sync service or admin actions.
    Prevents duplicate ownership.
    """
    user = await get_user_by_telegram_id(session, telegram_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if gift exists
    gift = await session.get(NFT, request.gift_id)
    if not gift:
        raise HTTPException(status_code=404, detail="Gift not found")

    # Check for duplicate
    existing = await session.execute(
        select(UserGiftInventory).where(
            and_(
                UserGiftInventory.user_id == user.id,
                UserGiftInventory.gift_id == request.gift_id,
            )
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Gift already in inventory")

    # Get floor price from collection
    collection = await session.get(Collection, gift.collection_id)
    floor_price = collection.floor_price_ton if collection else Decimal("0")

    # Create inventory item
    item = UserGiftInventory(
        user_id=user.id,
        gift_id=request.gift_id,
        telegram_msg_id=request.telegram_msg_id,
        telegram_slug=request.telegram_slug,
        source=request.source,
        acquisition_details=request.acquisition_details,
        floor_price_ton_at_acquisition=floor_price,
        current_floor_price_ton=floor_price,
        last_price_update_at=datetime.utcnow(),
    )

    session.add(item)
    await session.commit()
    await session.refresh(item, ["gift"])

    logger.info(f"Gift added to inventory: user={user.telegram_id}, gift={gift.name}")

    return InventoryItemSchema(
        id=item.id,
        user_id=item.user_id,
        gift_id=item.gift_id,
        gift=GiftNFTSchema.from_orm(item.gift),
        telegram_msg_id=item.telegram_msg_id,
        telegram_slug=item.telegram_slug,
        acquired_at=item.acquired_at,
        source=item.source.value,
        acquisition_details=item.acquisition_details,
        floor_price_ton_at_acquisition=item.floor_price_ton_at_acquisition,
        current_floor_price_ton=item.current_floor_price_ton,
        profit_loss_ton=item.profit_loss_ton,
        last_price_update_at=item.last_price_update_at,
        is_staked=item.is_staked,
        is_locked=item.is_locked,
        locked_reason=item.locked_reason,
        is_transferable=item.is_transferable,
        transfer_fee_stars=item.transfer_fee_stars,
        is_available_for_betting=item.is_available_for_betting,
    )


@router.post("/lock", status_code=200)
@limiter.limit("20/minute")
async def lock_gift(
    request: LockGiftRequest,
    telegram_id: int = Depends(get_verified_telegram_id),
    session: AsyncSession = Depends(get_db_session),
):
    """
    Lock a gift for game betting.

    Prevents the gift from being used in other games or transferred
    while it's locked in an active bet.
    """
    user = await get_user_by_telegram_id(session, telegram_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get inventory item with FOR UPDATE lock (prevents race conditions)
    result = await session.execute(
        select(UserGiftInventory)
        .where(UserGiftInventory.id == request.inventory_id)
        .with_for_update()
    )
    item = result.scalar_one_or_none()

    if not item:
        raise HTTPException(status_code=404, detail="Inventory item not found")

    if item.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not your gift")

    if item.is_locked:
        raise HTTPException(status_code=400, detail=f"Gift already locked: {item.locked_reason}")

    if item.is_staked:
        raise HTTPException(status_code=400, detail="Cannot lock staked gift")

    # Lock the gift
    item.is_locked = True
    item.locked_reason = request.reason
    item.locked_at = datetime.utcnow()

    await session.commit()

    logger.info(f"Gift locked: user={user.telegram_id}, gift_id={item.gift_id}, reason={request.reason}")

    return {"success": True, "message": "Gift locked successfully"}


@router.post("/unlock/{inventory_id}", status_code=200)
@limiter.limit("20/minute")
async def unlock_gift(
    inventory_id: int,
    telegram_id: int = Depends(get_verified_telegram_id),
    session: AsyncSession = Depends(get_db_session),
):
    """
    Unlock a gift after game completion.

    Called when game is finished or cancelled to release the gift.
    """
    user = await get_user_by_telegram_id(session, telegram_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get inventory item
    item = await session.get(UserGiftInventory, inventory_id)
    if not item:
        raise HTTPException(status_code=404, detail="Inventory item not found")

    if item.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not your gift")

    # Unlock the gift
    item.is_locked = False
    item.locked_reason = None
    item.locked_at = None

    await session.commit()

    logger.info(f"Gift unlocked: user={user.telegram_id}, gift_id={item.gift_id}")

    return {"success": True, "message": "Gift unlocked successfully"}


@router.post("/transfer", status_code=202)
@limiter.limit("5/minute")
async def transfer_gift(
    request: TransferGiftRequest,
    telegram_id: int = Depends(get_verified_telegram_id),
    session: AsyncSession = Depends(get_db_session),
):
    """
    Initiate gift transfer to another user.

    Creates transfer log entry and marks status as PENDING.
    Actual Telegram MTProto transfer will be handled by background service.

    For game payouts, this will be called automatically.
    """
    # Get sender
    sender = await get_user_by_telegram_id(session, telegram_id)
    if not sender:
        raise HTTPException(status_code=404, detail="Sender not found")

    # Get recipient
    recipient = await get_user_by_telegram_id(session, request.to_user_telegram_id)
    if not recipient:
        raise HTTPException(status_code=404, detail="Recipient not found")

    if sender.id == recipient.id:
        raise HTTPException(status_code=400, detail="Cannot transfer to yourself")

    # Get inventory item with lock
    result = await session.execute(
        select(UserGiftInventory)
        .where(UserGiftInventory.id == request.inventory_id)
        .with_for_update()
    )
    item = result.scalar_one_or_none()

    if not item:
        raise HTTPException(status_code=404, detail="Inventory item not found")

    if item.user_id != sender.id:
        raise HTTPException(status_code=403, detail="Not your gift")

    if not item.is_transferable:
        raise HTTPException(status_code=400, detail="Gift is not transferable")

    if item.is_locked:
        raise HTTPException(status_code=400, detail=f"Gift is locked: {item.locked_reason}")

    if item.is_staked:
        raise HTTPException(status_code=400, detail="Cannot transfer staked gift")

    # Lock gift during transfer
    item.is_locked = True
    item.locked_reason = f"transfer_pending_to_{recipient.telegram_id}"
    item.locked_at = datetime.utcnow()

    # Create transfer log
    transfer_log = GiftTransferLog(
        from_user_id=sender.id,
        to_user_id=recipient.id,
        gift_id=item.gift_id,
        inventory_id=item.id,
        reason=request.reason,
        status=TransferStatus.PENDING,
        gift_value_ton=item.current_floor_price_ton,
    )

    session.add(transfer_log)
    await session.commit()

    logger.info(
        f"Gift transfer initiated: from={sender.telegram_id} to={recipient.telegram_id} "
        f"gift={item.gift_id} transfer_id={transfer_log.id}"
    )

    return {
        "success": True,
        "message": "Transfer initiated. MTProto service will process shortly.",
        "transfer_id": transfer_log.id,
        "status": "pending",
    }


@router.get("/transfers", response_model=List[dict])
async def get_transfer_history(
    telegram_id: int = Depends(get_verified_telegram_id),
    session: AsyncSession = Depends(get_db_session),
    limit: int = Query(50, ge=1, le=200),
):
    """
    Get user's gift transfer history (sent and received).
    """
    user = await get_user_by_telegram_id(session, telegram_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get transfers
    result = await session.execute(
        select(GiftTransferLog)
        .where(
            or_(
                GiftTransferLog.from_user_id == user.id,
                GiftTransferLog.to_user_id == user.id,
            )
        )
        .order_by(GiftTransferLog.initiated_at.desc())
        .limit(limit)
        .options(selectinload(GiftTransferLog.gift))
    )
    transfers = result.scalars().all()

    return [
        {
            "id": t.id,
            "from_user_id": t.from_user_id,
            "to_user_id": t.to_user_id,
            "gift": GiftNFTSchema.from_orm(t.gift).dict(),
            "gift_value_ton": t.gift_value_ton,
            "reason": t.reason.value,
            "status": t.status.value,
            "initiated_at": t.initiated_at,
            "completed_at": t.completed_at,
            "direction": "sent" if t.from_user_id == user.id else "received",
        }
        for t in transfers
    ]

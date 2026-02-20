"""P2P Market API endpoints."""
from decimal import Decimal
from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.core.database import get_db
from app.core.auth import get_verified_telegram_id
from app.models import (
    P2PTrade,
    TradeStatus,
    UserGiftInventory,
    User,
    NFT,
    BetCurrency,
    OperationType,
)
from app.api.v1.inventory import inventoryLock, inventoryUnlock

router = APIRouter(prefix="/p2p", tags=["P2P Market"])


# ============================================================
# SCHEMAS
# ============================================================

class GiftInfo(BaseModel):
    """Gift information in listing."""
    id: int
    name: str
    image_url: Optional[str]
    animation_url: Optional[str]
    rarity: Optional[str]
    address: str


class TradeListingResponse(BaseModel):
    """P2P trade listing response."""
    id: int
    seller_id: int
    seller_username: Optional[str]
    gift: GiftInfo
    price_ton: Decimal
    floor_price_ton: Decimal
    discount_percent: Optional[Decimal]
    status: str
    created_at: datetime
    views_count: int

    class Config:
        from_attributes = True


class CreateListingRequest(BaseModel):
    """Create P2P listing request."""
    inventory_id: int = Field(..., description="Inventory item ID to sell")
    price_ton: Decimal = Field(..., gt=0, description="Selling price in TON")


class TradeListResponse(BaseModel):
    """Paginated trade list."""
    total: int
    active_count: int
    listings: List[TradeListingResponse]


class PurchaseResponse(BaseModel):
    """Purchase response."""
    success: bool
    trade_id: int
    gift_transferred: bool
    message: str


# ============================================================
# ENDPOINTS
# ============================================================

@router.get("/listings", response_model=TradeListResponse)
async def get_active_listings(
    limit: int = 50,
    offset: int = 0,
    min_price: Optional[Decimal] = None,
    max_price: Optional[Decimal] = None,
    rarity: Optional[str] = None,
    sort_by: str = "created_at",  # created_at, price_asc, price_desc, discount
    db: AsyncSession = Depends(get_db),
):
    """
    Get active P2P listings.

    Query parameters:
    - limit: Max results (default: 50)
    - offset: Pagination offset
    - min_price: Minimum price filter
    - max_price: Maximum price filter
    - rarity: Filter by gift rarity
    - sort_by: Sort order (created_at, price_asc, price_desc, discount)
    """
    # Build query
    query = (
        select(P2PTrade)
        .options(
            joinedload(P2PTrade.inventory_item).joinedload(UserGiftInventory.gift),
            joinedload(P2PTrade.seller),
        )
        .where(P2PTrade.status == TradeStatus.ACTIVE)
    )

    # Apply filters
    if min_price is not None:
        query = query.where(P2PTrade.price_ton >= min_price)
    if max_price is not None:
        query = query.where(P2PTrade.price_ton <= max_price)

    # Rarity filter (requires join)
    if rarity:
        query = query.join(UserGiftInventory).join(NFT).where(NFT.rarity == rarity)

    # Sorting
    if sort_by == "price_asc":
        query = query.order_by(P2PTrade.price_ton.asc())
    elif sort_by == "price_desc":
        query = query.order_by(P2PTrade.price_ton.desc())
    elif sort_by == "discount":
        query = query.order_by(P2PTrade.discount_percent.desc())
    else:  # created_at
        query = query.order_by(P2PTrade.created_at.desc())

    # Count total
    count_query = select(func.count()).select_from(P2PTrade).where(P2PTrade.status == TradeStatus.ACTIVE)
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Pagination
    query = query.limit(limit).offset(offset)

    # Execute
    result = await db.execute(query)
    trades = result.unique().scalars().all()

    # Format response
    listings = []
    for trade in trades:
        gift_info = GiftInfo(
            id=trade.inventory_item.gift.id,
            name=trade.inventory_item.gift.name,
            image_url=trade.inventory_item.gift.image_url,
            animation_url=trade.inventory_item.gift.animation_url,
            rarity=trade.inventory_item.gift.rarity,
            address=trade.inventory_item.gift.address,
        )

        listings.append(TradeListingResponse(
            id=trade.id,
            seller_id=trade.seller_id,
            seller_username=trade.seller.username if trade.seller else None,
            gift=gift_info,
            price_ton=trade.price_ton,
            floor_price_ton=trade.floor_price_ton,
            discount_percent=trade.discount_percent,
            status=trade.status.value,
            created_at=trade.created_at,
            views_count=trade.views_count,
        ))

    return TradeListResponse(
        total=total,
        active_count=len(listings),
        listings=listings,
    )


@router.get("/my-listings", response_model=TradeListResponse)
async def get_my_listings(
    status_filter: Optional[str] = None,
    telegram_id: int = Depends(get_verified_telegram_id),
    db: AsyncSession = Depends(get_db),
):
    """Get user's P2P listings."""
    # Get user
    user_result = await db.execute(select(User).where(User.telegram_id == telegram_id))
    user = user_result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Build query
    query = (
        select(P2PTrade)
        .options(
            joinedload(P2PTrade.inventory_item).joinedload(UserGiftInventory.gift),
        )
        .where(P2PTrade.seller_id == user.id)
    )

    # Status filter
    if status_filter:
        try:
            status_enum = TradeStatus(status_filter)
            query = query.where(P2PTrade.status == status_enum)
        except ValueError:
            pass

    query = query.order_by(P2PTrade.created_at.desc())

    # Execute
    result = await db.execute(query)
    trades = result.unique().scalars().all()

    # Count active
    active_count = sum(1 for t in trades if t.status == TradeStatus.ACTIVE)

    # Format response
    listings = []
    for trade in trades:
        gift_info = GiftInfo(
            id=trade.inventory_item.gift.id,
            name=trade.inventory_item.gift.name,
            image_url=trade.inventory_item.gift.image_url,
            animation_url=trade.inventory_item.gift.animation_url,
            rarity=trade.inventory_item.gift.rarity,
            address=trade.inventory_item.gift.address,
        )

        listings.append(TradeListingResponse(
            id=trade.id,
            seller_id=trade.seller_id,
            seller_username=None,  # Don't show own username
            gift=gift_info,
            price_ton=trade.price_ton,
            floor_price_ton=trade.floor_price_ton,
            discount_percent=trade.discount_percent,
            status=trade.status.value,
            created_at=trade.created_at,
            views_count=trade.views_count,
        ))

    return TradeListResponse(
        total=len(listings),
        active_count=active_count,
        listings=listings,
    )


@router.post("/listings", response_model=TradeListingResponse, status_code=201)
async def create_listing(
    request: CreateListingRequest,
    telegram_id: int = Depends(get_verified_telegram_id),
    db: AsyncSession = Depends(get_db),
):
    """
    Create P2P listing.

    Locks the inventory item and creates active listing.
    """
    # Get user
    user_result = await db.execute(select(User).where(User.telegram_id == telegram_id))
    user = user_result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get inventory item
    inv_result = await db.execute(
        select(UserGiftInventory)
        .options(joinedload(UserGiftInventory.gift))
        .where(
            and_(
                UserGiftInventory.id == request.inventory_id,
                UserGiftInventory.user_id == user.id,
            )
        )
    )
    inventory_item = inv_result.scalar_one_or_none()

    if not inventory_item:
        raise HTTPException(status_code=404, detail="Gift not found in inventory")

    # Validate availability
    if not inventory_item.is_available_for_betting:
        raise HTTPException(
            status_code=400,
            detail=f"Gift is not available (locked: {inventory_item.is_locked}, staked: {inventory_item.is_staked})"
        )

    # Lock inventory item
    inventory_item.is_locked = True
    inventory_item.locked_reason = "p2p_listing"
    inventory_item.locked_at = datetime.utcnow()

    # Calculate discount
    floor_price = inventory_item.current_floor_price_ton
    discount = None
    if floor_price > 0:
        discount = ((floor_price - request.price_ton) / floor_price) * 100

    # Create listing
    trade = P2PTrade(
        seller_id=user.id,
        inventory_id=inventory_item.id,
        price_ton=request.price_ton,
        floor_price_ton=floor_price,
        discount_percent=discount if discount and discount > 0 else None,
        status=TradeStatus.ACTIVE,
    )

    db.add(trade)
    await db.commit()
    await db.refresh(trade)

    # Reload with relationships
    trade_result = await db.execute(
        select(P2PTrade)
        .options(
            joinedload(P2PTrade.inventory_item).joinedload(UserGiftInventory.gift),
        )
        .where(P2PTrade.id == trade.id)
    )
    trade = trade_result.unique().scalar_one()

    # Format response
    gift_info = GiftInfo(
        id=trade.inventory_item.gift.id,
        name=trade.inventory_item.gift.name,
        image_url=trade.inventory_item.gift.image_url,
        animation_url=trade.inventory_item.gift.animation_url,
        rarity=trade.inventory_item.gift.rarity,
        address=trade.inventory_item.gift.address,
    )

    return TradeListingResponse(
        id=trade.id,
        seller_id=trade.seller_id,
        seller_username=None,
        gift=gift_info,
        price_ton=trade.price_ton,
        floor_price_ton=trade.floor_price_ton,
        discount_percent=trade.discount_percent,
        status=trade.status.value,
        created_at=trade.created_at,
        views_count=trade.views_count,
    )


@router.delete("/listings/{trade_id}")
async def cancel_listing(
    trade_id: int,
    telegram_id: int = Depends(get_verified_telegram_id),
    db: AsyncSession = Depends(get_db),
):
    """Cancel P2P listing."""
    # Get user
    user_result = await db.execute(select(User).where(User.telegram_id == telegram_id))
    user = user_result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get trade
    trade_result = await db.execute(
        select(P2PTrade)
        .options(joinedload(P2PTrade.inventory_item))
        .where(P2PTrade.id == trade_id)
    )
    trade = trade_result.scalar_one_or_none()

    if not trade:
        raise HTTPException(status_code=404, detail="Listing not found")

    if trade.seller_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    if trade.status != TradeStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="Listing is not active")

    # Update trade
    trade.status = TradeStatus.CANCELLED
    trade.cancelled_at = datetime.utcnow()

    # Unlock inventory item
    trade.inventory_item.is_locked = False
    trade.inventory_item.locked_reason = None
    trade.inventory_item.locked_at = None

    await db.commit()

    return {"success": True, "message": "Listing cancelled"}


@router.post("/listings/{trade_id}/purchase", response_model=PurchaseResponse)
async def purchase_listing(
    trade_id: int,
    telegram_id: int = Depends(get_verified_telegram_id),
    db: AsyncSession = Depends(get_db),
):
    """Purchase P2P listing."""
    # Get buyer
    buyer_result = await db.execute(select(User).where(User.telegram_id == telegram_id))
    buyer = buyer_result.scalar_one_or_none()
    if not buyer:
        raise HTTPException(status_code=404, detail="User not found")

    # Get trade
    trade_result = await db.execute(
        select(P2PTrade)
        .options(
            joinedload(P2PTrade.inventory_item),
            joinedload(P2PTrade.seller),
        )
        .where(P2PTrade.id == trade_id)
    )
    trade = trade_result.scalar_one_or_none()

    if not trade:
        raise HTTPException(status_code=404, detail="Listing not found")

    if trade.status != TradeStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="Listing is not active")

    if trade.seller_id == buyer.id:
        raise HTTPException(status_code=400, detail="Cannot buy own listing")

    # Check buyer balance
    if buyer.balance_ton < trade.price_ton:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient balance (have: {buyer.balance_ton}, need: {trade.price_ton})"
        )

    # Execute trade
    # 1. Deduct from buyer
    buyer.balance_ton -= trade.price_ton

    # 2. Add to seller (minus platform fee if any)
    platform_fee_percent = Decimal("0.02")  # 2% platform fee
    platform_fee = trade.price_ton * platform_fee_percent
    seller_receives = trade.price_ton - platform_fee

    trade.seller.balance_ton += seller_receives

    # 3. Transfer inventory
    trade.inventory_item.user_id = buyer.id
    trade.inventory_item.is_locked = False
    trade.inventory_item.locked_reason = None
    trade.inventory_item.locked_at = None

    # 4. Update trade
    trade.status = TradeStatus.SOLD
    trade.buyer_id = buyer.id
    trade.sold_at = datetime.utcnow()

    await db.commit()

    return PurchaseResponse(
        success=True,
        trade_id=trade.id,
        gift_transferred=True,
        message=f"Successfully purchased {trade.inventory_item.gift.name} for {trade.price_ton} TON",
    )

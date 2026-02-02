"""
Gift (NFT) API endpoints.

Provides REST API for:
- Listing gifts with filters
- Getting gift details
- Searching gifts
- Getting gift price history
"""
import logging
from datetime import datetime
from decimal import Decimal
from typing import Optional, List

from fastapi import APIRouter, Depends, Query, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload

from app.core.database import get_db_session, AsyncSession
from app.models.collection import Collection
from app.models.nft import NFT
from app.models.listing import Listing
from app.models.market import Market

logger = logging.getLogger(__name__)
router = APIRouter()


# ============================================================
# SCHEMAS
# ============================================================

class MarketListingSchema(BaseModel):
    """Active listing on a market."""
    market_slug: str
    market_name: str
    price_ton: Decimal
    price_raw: Decimal
    currency: str
    listing_url: Optional[str]
    seller_address: Optional[str]
    listed_at: Optional[datetime]

    class Config:
        from_attributes = True


class GiftSchema(BaseModel):
    """Gift (NFT) response schema."""
    id: int
    address: str
    name: str
    description: Optional[str]
    collection_id: int
    collection_name: str
    collection_slug: str

    # Media
    image_url: Optional[str]
    animation_url: Optional[str]

    # Attributes
    rarity: Optional[str]
    backdrop: Optional[str]
    model: Optional[str]
    symbol: Optional[str]
    attributes: List[dict]

    # Sale info
    is_on_sale: bool
    lowest_price_ton: Optional[Decimal]
    lowest_price_market: Optional[str]

    # Active listings (if requested)
    listings: Optional[List[MarketListingSchema]] = None

    class Config:
        from_attributes = True


class GiftListResponse(BaseModel):
    """Paginated gift list response."""
    total: int
    page: int
    page_size: int
    total_pages: int
    items: List[GiftSchema]


class GiftFilters(BaseModel):
    """Gift search filters."""
    collection_id: Optional[int] = None
    collection_slug: Optional[str] = None
    is_on_sale: Optional[bool] = None
    rarity: Optional[List[str]] = None
    backdrop: Optional[str] = None
    model: Optional[str] = None
    price_min: Optional[Decimal] = None
    price_max: Optional[Decimal] = None
    sort_by: str = "price_asc"  # price_asc, price_desc, recent, name


# ============================================================
# ENDPOINTS
# ============================================================

@router.get("/gifts", response_model=GiftListResponse)
async def list_gifts(
    # Pagination
    page: int = Query(0, ge=0, description="Page number (0-indexed)"),
    page_size: int = Query(50, ge=1, le=200, description="Items per page"),

    # Filters
    collection_id: Optional[int] = Query(None, description="Filter by collection ID"),
    collection_slug: Optional[str] = Query(None, description="Filter by collection slug"),
    is_on_sale: Optional[bool] = Query(None, description="Filter by sale status"),
    rarity: Optional[str] = Query(None, description="Filter by rarity (comma-separated)"),
    backdrop: Optional[str] = Query(None, description="Filter by backdrop"),
    model: Optional[str] = Query(None, description="Filter by model"),
    price_min: Optional[Decimal] = Query(None, ge=0, description="Minimum price in TON"),
    price_max: Optional[Decimal] = Query(None, ge=0, description="Maximum price in TON"),
    search: Optional[str] = Query(None, description="Search by name"),

    # Sorting
    sort_by: str = Query("price_asc", description="Sort order"),

    session: AsyncSession = Depends(get_db_session),
):
    """
    List gifts with filters and pagination.

    Supports filtering by collection, sale status, rarity, price range.
    """
    # Build base query with collection join
    query = (
        select(NFT, Collection.name.label("collection_name"), Collection.slug.label("collection_slug"))
        .join(Collection, NFT.collection_id == Collection.id)
    )

    # Apply filters
    conditions = []

    if collection_id:
        conditions.append(NFT.collection_id == collection_id)

    if collection_slug:
        conditions.append(Collection.slug == collection_slug)

    if is_on_sale is not None:
        conditions.append(NFT.is_on_sale == is_on_sale)

    if rarity:
        rarity_list = [r.strip() for r in rarity.split(",")]
        conditions.append(NFT.rarity.in_(rarity_list))

    if backdrop:
        conditions.append(NFT.backdrop == backdrop)

    if model:
        conditions.append(NFT.model == model)

    if price_min is not None:
        conditions.append(NFT.lowest_price_ton >= price_min)

    if price_max is not None:
        conditions.append(NFT.lowest_price_ton <= price_max)

    if search:
        # Simple search - for production use Meilisearch
        conditions.append(NFT.name.ilike(f"%{search}%"))

    if conditions:
        query = query.where(and_(*conditions))

    # Count total
    count_query = select(func.count(NFT.id)).select_from(NFT)
    if conditions:
        count_query = count_query.where(and_(*conditions))
    count_result = await session.execute(count_query)
    total = count_result.scalar() or 0

    # Apply sorting
    if sort_by == "price_asc":
        query = query.order_by(NFT.lowest_price_ton.asc().nullslast())
    elif sort_by == "price_desc":
        query = query.order_by(NFT.lowest_price_ton.desc().nullsfirst())
    elif sort_by == "recent":
        query = query.order_by(NFT.updated_at.desc())
    elif sort_by == "name":
        query = query.order_by(NFT.name.asc())
    else:
        query = query.order_by(NFT.id.asc())

    # Apply pagination
    offset = page * page_size
    query = query.offset(offset).limit(page_size)

    # Execute query
    result = await session.execute(query)
    rows = result.all()

    # Build response
    items = []
    for row in rows:
        nft = row[0]
        items.append(GiftSchema(
            id=nft.id,
            address=nft.address,
            name=nft.name,
            description=nft.description,
            collection_id=nft.collection_id,
            collection_name=row.collection_name,
            collection_slug=row.collection_slug,
            image_url=nft.image_cdn_url or nft.image_url,
            animation_url=nft.animation_cdn_url or nft.animation_url,
            rarity=nft.rarity,
            backdrop=nft.backdrop,
            model=nft.model,
            symbol=nft.symbol,
            attributes=nft.attributes or [],
            is_on_sale=nft.is_on_sale,
            lowest_price_ton=nft.lowest_price_ton,
            lowest_price_market=nft.lowest_price_market,
            listings=None,
        ))

    total_pages = (total + page_size - 1) // page_size

    return GiftListResponse(
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        items=items,
    )


@router.get("/gifts/{gift_id}", response_model=GiftSchema)
async def get_gift(
    gift_id: int,
    include_listings: bool = Query(True, description="Include active listings"),
    session: AsyncSession = Depends(get_db_session),
):
    """
    Get gift details by ID.

    Optionally includes all active listings across markets.
    """
    # Get NFT with collection
    result = await session.execute(
        select(NFT, Collection.name.label("collection_name"), Collection.slug.label("collection_slug"))
        .join(Collection, NFT.collection_id == Collection.id)
        .where(NFT.id == gift_id)
    )
    row = result.first()

    if not row:
        raise HTTPException(status_code=404, detail="Gift not found")

    nft = row[0]

    # Get active listings if requested
    listings = None
    if include_listings:
        listings_result = await session.execute(
            select(Listing, Market)
            .join(Market, Listing.market_id == Market.id)
            .where(
                and_(
                    Listing.nft_id == gift_id,
                    Listing.is_active == True,
                )
            )
            .order_by(Listing.price_ton.asc())
        )
        listings_rows = listings_result.all()

        listings = [
            MarketListingSchema(
                market_slug=market.slug,
                market_name=market.name,
                price_ton=listing.price_ton,
                price_raw=listing.price_raw,
                currency=listing.currency,
                listing_url=listing.listing_url,
                seller_address=listing.seller_address,
                listed_at=listing.listed_at,
            )
            for listing, market in listings_rows
        ]

    return GiftSchema(
        id=nft.id,
        address=nft.address,
        name=nft.name,
        description=nft.description,
        collection_id=nft.collection_id,
        collection_name=row.collection_name,
        collection_slug=row.collection_slug,
        image_url=nft.image_cdn_url or nft.image_url,
        animation_url=nft.animation_cdn_url or nft.animation_url,
        rarity=nft.rarity,
        backdrop=nft.backdrop,
        model=nft.model,
        symbol=nft.symbol,
        attributes=nft.attributes or [],
        is_on_sale=nft.is_on_sale,
        lowest_price_ton=nft.lowest_price_ton,
        lowest_price_market=nft.lowest_price_market,
        listings=listings,
    )


@router.get("/gifts/address/{nft_address}", response_model=GiftSchema)
async def get_gift_by_address(
    nft_address: str,
    include_listings: bool = Query(True, description="Include active listings"),
    session: AsyncSession = Depends(get_db_session),
):
    """
    Get gift details by TON address.
    """
    # Get NFT by address
    result = await session.execute(
        select(NFT).where(NFT.address == nft_address)
    )
    nft = result.scalar_one_or_none()

    if not nft:
        raise HTTPException(status_code=404, detail="Gift not found")

    # Reuse get_gift logic
    return await get_gift(nft.id, include_listings, session)


@router.get("/gifts/{gift_id}/listings", response_model=List[MarketListingSchema])
async def get_gift_listings(
    gift_id: int,
    session: AsyncSession = Depends(get_db_session),
):
    """
    Get all active listings for a gift across all markets.
    """
    result = await session.execute(
        select(Listing, Market)
        .join(Market, Listing.market_id == Market.id)
        .where(
            and_(
                Listing.nft_id == gift_id,
                Listing.is_active == True,
            )
        )
        .order_by(Listing.price_ton.asc())
    )
    rows = result.all()

    return [
        MarketListingSchema(
            market_slug=market.slug,
            market_name=market.name,
            price_ton=listing.price_ton,
            price_raw=listing.price_raw,
            currency=listing.currency,
            listing_url=listing.listing_url,
            seller_address=listing.seller_address,
            listed_at=listing.listed_at,
        )
        for listing, market in rows
    ]


@router.get("/collections")
async def list_collections(
    telegram_gifts_only: bool = Query(False, description="Only Telegram Gift collections"),
    session: AsyncSession = Depends(get_db_session),
):
    """
    List all indexed collections.
    """
    query = select(Collection).order_by(Collection.name)

    if telegram_gifts_only:
        query = query.where(Collection.is_telegram_gift == True)

    result = await session.execute(query)
    collections = result.scalars().all()

    return {
        "total": len(collections),
        "collections": [
            {
                "id": c.id,
                "address": c.address,
                "name": c.name,
                "slug": c.slug,
                "description": c.description,
                "image_url": c.image_url,
                "total_items": c.total_items,
                "owners_count": c.owners_count,
                "floor_price_ton": c.floor_price_ton,
                "volume_24h_ton": c.volume_24h_ton,
                "is_verified": c.is_verified,
                "is_telegram_gift": c.is_telegram_gift,
            }
            for c in collections
        ],
    }


@router.get("/collections/{collection_id}")
async def get_collection(
    collection_id: int,
    session: AsyncSession = Depends(get_db_session),
):
    """
    Get collection details.
    """
    result = await session.execute(
        select(Collection).where(Collection.id == collection_id)
    )
    collection = result.scalar_one_or_none()

    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")

    return {
        "id": collection.id,
        "address": collection.address,
        "name": collection.name,
        "slug": collection.slug,
        "description": collection.description,
        "image_url": collection.image_url,
        "cover_url": collection.cover_url,
        "external_url": collection.external_url,
        "total_items": collection.total_items,
        "owners_count": collection.owners_count,
        "floor_price_ton": collection.floor_price_ton,
        "total_volume_ton": collection.total_volume_ton,
        "volume_24h_ton": collection.volume_24h_ton,
        "is_verified": collection.is_verified,
        "is_telegram_gift": collection.is_telegram_gift,
        "indexing_status": collection.indexing_status,
        "last_indexed_at": collection.last_indexed_at,
    }

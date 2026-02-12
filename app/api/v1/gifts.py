"""
Gift (NFT) API endpoints.

Provides REST API for:
- Listing gifts with filters
- Getting gift details
- Searching gifts
- Getting gift price history
- Getting filter options (distinct values)
"""
import logging
from datetime import datetime
from decimal import Decimal
from typing import Optional, List

from fastapi import APIRouter, Depends, Query, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select, func, and_, or_, distinct, case
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
    gift_type: Optional[str] = None
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
    pattern: Optional[str]
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


class FilterOption(BaseModel):
    """Single filter option with count and floor price."""
    value: str
    count: int
    floor_price: Optional[float] = None
    image_url: Optional[str] = None


class FiltersResponse(BaseModel):
    """Available filter options."""
    gift_types: List[FilterOption]
    models: List[FilterOption]
    backdrops: List[FilterOption]
    symbols: List[FilterOption]
    patterns: List[FilterOption]
    rarities: List[FilterOption]
    price_range: dict  # {min, max}


# ============================================================
# HELPERS
# ============================================================

def _normalize_sort(sort_value: str) -> str:
    """
    Normalize sort parameter to internal format.
    Accepts: 'price asc', 'price_asc', 'price desc', 'rarity asc', etc.
    Returns: 'price_asc', 'price_desc', 'recent', 'name', etc.
    """
    s = sort_value.strip().lower()
    # Replace space with underscore
    s = s.replace(' ', '_')
    # Map common aliases
    aliases = {
        'price_asc': 'price_asc',
        'price_desc': 'price_desc',
        'id_asc': 'id_asc',
        'id_desc': 'id_desc',
        'rarity_asc': 'rarity_asc',
        'rarity_desc': 'rarity_desc',
        'listed_at_desc': 'recent',
        'newest': 'recent',
        'recent': 'recent',
        'name': 'name',
        'name_asc': 'name',
    }
    return aliases.get(s, s)


def _split_multi(value: Optional[str]) -> Optional[list[str]]:
    """Split comma-separated filter value into list."""
    if not value:
        return None
    return [v.strip() for v in value.split(',') if v.strip()]


# ============================================================
# ENDPOINTS
# ============================================================

@router.get("/gifts/filters", response_model=FiltersResponse)
async def get_filter_options(
    gift_type: Optional[str] = Query(None, description="Filter by gift type to narrow down options"),
    is_on_sale: Optional[bool] = Query(True, description="Only show options for items on sale"),
    session: AsyncSession = Depends(get_db_session),
):
    """
    Get all available filter options with counts and floor prices.
    Used by frontend to populate filter dropdowns.
    """
    # Base condition
    conditions = []
    if is_on_sale is not None:
        conditions.append(NFT.is_on_sale == is_on_sale)
    if gift_type:
        gift_types = _split_multi(gift_type)
        if gift_types:
            conditions.append(NFT.gift_type.in_(gift_types))

    base_where = and_(*conditions) if conditions else True

    # Gift types
    gift_type_query = (
        select(
            NFT.gift_type,
            func.count(NFT.id).label('cnt'),
            func.min(NFT.lowest_price_ton).label('floor'),
            func.min(NFT.image_url).label('img'),
        )
        .where(base_where)
        .where(NFT.gift_type.isnot(None))
        .group_by(NFT.gift_type)
        .order_by(func.count(NFT.id).desc())
    )
    gt_result = await session.execute(gift_type_query)
    gift_types = [
        FilterOption(
            value=row.gift_type,
            count=row.cnt,
            floor_price=float(row.floor) if row.floor else None,
            image_url=row.img,
        )
        for row in gt_result.all()
    ]

    # Models
    model_query = (
        select(
            NFT.model,
            func.count(NFT.id).label('cnt'),
            func.min(NFT.lowest_price_ton).label('floor'),
        )
        .where(base_where)
        .where(NFT.model.isnot(None))
        .group_by(NFT.model)
        .order_by(func.count(NFT.id).desc())
    )
    m_result = await session.execute(model_query)
    models = [
        FilterOption(value=row.model, count=row.cnt, floor_price=float(row.floor) if row.floor else None)
        for row in m_result.all()
    ]

    # Backdrops
    backdrop_query = (
        select(
            NFT.backdrop,
            func.count(NFT.id).label('cnt'),
            func.min(NFT.lowest_price_ton).label('floor'),
        )
        .where(base_where)
        .where(NFT.backdrop.isnot(None))
        .group_by(NFT.backdrop)
        .order_by(func.count(NFT.id).desc())
    )
    b_result = await session.execute(backdrop_query)
    backdrops = [
        FilterOption(value=row.backdrop, count=row.cnt, floor_price=float(row.floor) if row.floor else None)
        for row in b_result.all()
    ]

    # Symbols
    symbol_query = (
        select(
            NFT.symbol,
            func.count(NFT.id).label('cnt'),
            func.min(NFT.lowest_price_ton).label('floor'),
        )
        .where(base_where)
        .where(NFT.symbol.isnot(None))
        .group_by(NFT.symbol)
        .order_by(func.count(NFT.id).desc())
    )
    s_result = await session.execute(symbol_query)
    symbols = [
        FilterOption(value=row.symbol, count=row.cnt, floor_price=float(row.floor) if row.floor else None)
        for row in s_result.all()
    ]

    # Patterns
    pattern_query = (
        select(
            NFT.pattern,
            func.count(NFT.id).label('cnt'),
            func.min(NFT.lowest_price_ton).label('floor'),
        )
        .where(base_where)
        .where(NFT.pattern.isnot(None))
        .group_by(NFT.pattern)
        .order_by(func.count(NFT.id).desc())
    )
    p_result = await session.execute(pattern_query)
    patterns = [
        FilterOption(value=row.pattern, count=row.cnt, floor_price=float(row.floor) if row.floor else None)
        for row in p_result.all()
    ]

    # Rarities
    rarity_query = (
        select(
            NFT.rarity,
            func.count(NFT.id).label('cnt'),
            func.min(NFT.lowest_price_ton).label('floor'),
        )
        .where(base_where)
        .where(NFT.rarity.isnot(None))
        .group_by(NFT.rarity)
        .order_by(func.count(NFT.id).desc())
    )
    r_result = await session.execute(rarity_query)
    rarities = [
        FilterOption(value=row.rarity, count=row.cnt, floor_price=float(row.floor) if row.floor else None)
        for row in r_result.all()
    ]

    # Price range
    price_query = (
        select(
            func.min(NFT.lowest_price_ton).label('min_price'),
            func.max(NFT.lowest_price_ton).label('max_price'),
        )
        .where(base_where)
        .where(NFT.lowest_price_ton.isnot(None))
        .where(NFT.lowest_price_ton > 0)
    )
    pr_result = await session.execute(price_query)
    pr_row = pr_result.first()

    return FiltersResponse(
        gift_types=gift_types,
        models=models,
        backdrops=backdrops,
        symbols=symbols,
        patterns=patterns,
        rarities=rarities,
        price_range={
            "min": float(pr_row.min_price) if pr_row and pr_row.min_price else 0,
            "max": float(pr_row.max_price) if pr_row and pr_row.max_price else 0,
        },
    )


@router.get("/gifts", response_model=GiftListResponse)
async def list_gifts(
    # Pagination
    page: int = Query(0, ge=0, description="Page number (0-indexed)"),
    page_size: int = Query(50, ge=1, le=200, description="Items per page"),
    limit: Optional[int] = Query(None, ge=1, le=200, description="Alias for page_size"),
    offset: Optional[int] = Query(None, ge=0, description="Offset (overrides page)"),

    # Filters
    collection_id: Optional[int] = Query(None, description="Filter by collection ID"),
    collection_slug: Optional[str] = Query(None, description="Filter by collection slug"),
    gift_type: Optional[str] = Query(None, description="Filter by gift type (comma-separated)"),
    is_on_sale: Optional[bool] = Query(None, description="Filter by sale status"),
    rarity: Optional[str] = Query(None, description="Filter by rarity (comma-separated)"),
    backdrop: Optional[str] = Query(None, description="Filter by backdrop (comma-separated)"),
    model: Optional[str] = Query(None, description="Filter by model (comma-separated)"),
    pattern: Optional[str] = Query(None, description="Filter by pattern (comma-separated)"),
    symbol: Optional[str] = Query(None, description="Filter by symbol (comma-separated)"),
    # Price: accept both naming conventions
    price_min: Optional[Decimal] = Query(None, ge=0, description="Minimum price in TON"),
    price_max: Optional[Decimal] = Query(None, ge=0, description="Maximum price in TON"),
    min_price: Optional[Decimal] = Query(None, ge=0, description="Alias for price_min"),
    max_price: Optional[Decimal] = Query(None, ge=0, description="Alias for price_max"),
    search: Optional[str] = Query(None, description="Search by name"),

    # Sorting: accept both naming conventions
    sort_by: Optional[str] = Query(None, description="Sort order"),
    sort: Optional[str] = Query(None, description="Alias for sort_by"),

    session: AsyncSession = Depends(get_db_session),
):
    """
    List gifts with filters and pagination.
    Supports multi-value filters (comma-separated).
    """
    # Resolve aliases
    effective_limit = limit or page_size
    effective_sort = _normalize_sort(sort_by or sort or "price_asc")
    effective_price_min = price_min or min_price
    effective_price_max = price_max or max_price

    # Calculate offset
    if offset is not None:
        effective_offset = offset
        effective_page = offset // effective_limit
    else:
        effective_page = page
        effective_offset = page * effective_limit

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

    # Gift type: multi-value
    gift_types = _split_multi(gift_type)
    if gift_types:
        conditions.append(NFT.gift_type.in_(gift_types))

    if is_on_sale is not None:
        conditions.append(NFT.is_on_sale == is_on_sale)

    # Rarity: multi-value
    rarities = _split_multi(rarity)
    if rarities:
        conditions.append(NFT.rarity.in_(rarities))

    # Backdrop: multi-value
    backdrops = _split_multi(backdrop)
    if backdrops:
        conditions.append(NFT.backdrop.in_(backdrops))

    # Model: multi-value
    models = _split_multi(model)
    if models:
        conditions.append(NFT.model.in_(models))

    # Pattern: multi-value
    patterns = _split_multi(pattern)
    if patterns:
        conditions.append(NFT.pattern.in_(patterns))

    # Symbol: multi-value
    symbols = _split_multi(symbol)
    if symbols:
        conditions.append(NFT.symbol.in_(symbols))

    if effective_price_min is not None:
        conditions.append(NFT.lowest_price_ton >= effective_price_min)

    if effective_price_max is not None:
        conditions.append(NFT.lowest_price_ton <= effective_price_max)

    if search:
        conditions.append(
            or_(
                NFT.name.ilike(f"%{search}%"),
                NFT.gift_type.ilike(f"%{search}%"),
            )
        )

    if conditions:
        query = query.where(and_(*conditions))

    # Count total
    count_query = (
        select(func.count(NFT.id))
        .select_from(NFT)
        .join(Collection, NFT.collection_id == Collection.id)
    )
    if conditions:
        count_query = count_query.where(and_(*conditions))
    count_result = await session.execute(count_query)
    total = count_result.scalar() or 0

    # Apply sorting
    if effective_sort == "price_asc":
        query = query.order_by(NFT.lowest_price_ton.asc().nullslast())
    elif effective_sort == "price_desc":
        query = query.order_by(NFT.lowest_price_ton.desc().nullsfirst())
    elif effective_sort == "recent":
        query = query.order_by(NFT.updated_at.desc().nullslast())
    elif effective_sort == "name":
        query = query.order_by(NFT.name.asc())
    elif effective_sort == "id_asc":
        query = query.order_by(NFT.index.asc().nullslast())
    elif effective_sort == "id_desc":
        query = query.order_by(NFT.index.desc().nullsfirst())
    elif effective_sort == "rarity_asc":
        # Rarity order: Common < Uncommon < Rare < Epic < Legendary
        rarity_order = case(
            (NFT.rarity == 'Common', 1),
            (NFT.rarity == 'Uncommon', 2),
            (NFT.rarity == 'Rare', 3),
            (NFT.rarity == 'Epic', 4),
            (NFT.rarity == 'Legendary', 5),
            else_=0,
        )
        query = query.order_by(rarity_order.asc())
    elif effective_sort == "rarity_desc":
        rarity_order = case(
            (NFT.rarity == 'Common', 1),
            (NFT.rarity == 'Uncommon', 2),
            (NFT.rarity == 'Rare', 3),
            (NFT.rarity == 'Epic', 4),
            (NFT.rarity == 'Legendary', 5),
            else_=0,
        )
        query = query.order_by(rarity_order.desc())
    else:
        query = query.order_by(NFT.id.asc())

    # Apply pagination
    query = query.offset(effective_offset).limit(effective_limit)

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
            gift_type=nft.gift_type,
            description=nft.description,
            collection_id=nft.collection_id,
            collection_name=row.collection_name,
            collection_slug=row.collection_slug,
            image_url=nft.image_cdn_url or nft.image_url,
            animation_url=nft.animation_cdn_url or nft.animation_url,
            rarity=nft.rarity,
            backdrop=nft.backdrop,
            model=nft.model,
            pattern=nft.pattern,
            symbol=nft.symbol,
            attributes=nft.attributes or [],
            is_on_sale=nft.is_on_sale,
            lowest_price_ton=nft.lowest_price_ton,
            lowest_price_market=nft.lowest_price_market,
            listings=None,
        ))

    total_pages = (total + effective_limit - 1) // effective_limit

    return GiftListResponse(
        total=total,
        page=effective_page,
        page_size=effective_limit,
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
        gift_type=nft.gift_type,
        description=nft.description,
        collection_id=nft.collection_id,
        collection_name=row.collection_name,
        collection_slug=row.collection_slug,
        image_url=nft.image_cdn_url or nft.image_url,
        animation_url=nft.animation_cdn_url or nft.animation_url,
        rarity=nft.rarity,
        backdrop=nft.backdrop,
        model=nft.model,
        pattern=nft.pattern,
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
    """Get gift details by TON address."""
    result = await session.execute(
        select(NFT).where(NFT.address == nft_address)
    )
    nft = result.scalar_one_or_none()

    if not nft:
        raise HTTPException(status_code=404, detail="Gift not found")

    return await get_gift(nft.id, include_listings, session)


@router.get("/gifts/{gift_id}/listings", response_model=List[MarketListingSchema])
async def get_gift_listings(
    gift_id: int,
    session: AsyncSession = Depends(get_db_session),
):
    """Get all active listings for a gift across all markets."""
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
    """List all indexed collections."""
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
    """Get collection details."""
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

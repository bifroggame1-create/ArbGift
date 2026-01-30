"""
Search API endpoints.

Provides full-text search for gifts with filters, sorting,
pagination, and autocomplete functionality.
"""
import logging
from decimal import Decimal
from typing import Optional, List, Any

from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel, Field

from app.services.search_service import get_search_service
from app.core.search import get_search_client

logger = logging.getLogger(__name__)
router = APIRouter()


# ============================================================
# SCHEMAS
# ============================================================

class SearchHit(BaseModel):
    """Individual search result."""

    id: int
    address: str
    name: str
    description: Optional[str] = None
    collection_id: int
    collection_name: str
    rarity: Optional[str] = None
    backdrop: Optional[str] = None
    model: Optional[str] = None
    is_on_sale: bool
    price_ton: Optional[float] = None
    image_url: Optional[str] = None
    updated_at: Optional[int] = None

    # Highlighted fields (from search)
    _formatted: Optional[dict] = Field(default=None, alias="_formatted")

    class Config:
        populate_by_name = True


class FacetDistribution(BaseModel):
    """Facet counts for a specific attribute."""

    rarity: Optional[dict[str, int]] = None
    collection_id: Optional[dict[str, int]] = None
    backdrop: Optional[dict[str, int]] = None
    model: Optional[dict[str, int]] = None
    is_on_sale: Optional[dict[str, int]] = None


class SearchResponse(BaseModel):
    """Search response with results and metadata."""

    hits: List[dict]
    total: int
    page: int
    page_size: int
    total_pages: int
    processing_time_ms: int
    facet_distribution: Optional[dict] = None
    facet_stats: Optional[dict] = None


class AutocompleteItem(BaseModel):
    """Autocomplete suggestion item."""

    id: int
    name: str
    collection_name: str
    rarity: Optional[str] = None
    image_url: Optional[str] = None
    price_ton: Optional[float] = None
    is_on_sale: bool = False
    _formatted: Optional[dict] = Field(default=None, alias="_formatted")

    class Config:
        populate_by_name = True


class AutocompleteResponse(BaseModel):
    """Autocomplete response."""

    suggestions: List[dict]
    query: str


class FacetsResponse(BaseModel):
    """Facets response for filter UI."""

    facet_distribution: dict
    facet_stats: Optional[dict] = None


class SearchHealthResponse(BaseModel):
    """Search health check response."""

    status: str
    index_stats: Optional[dict] = None


# ============================================================
# ENDPOINTS
# ============================================================

@router.get("/search", response_model=SearchResponse)
async def search_gifts(
    q: str = Query("", description="Search query"),

    # Filters
    rarity: Optional[str] = Query(
        None,
        description="Filter by rarity (comma-separated for multiple)",
    ),
    collection_id: Optional[int] = Query(
        None,
        description="Filter by collection ID",
    ),
    is_on_sale: Optional[bool] = Query(
        None,
        description="Filter by sale status",
    ),
    price_min: Optional[float] = Query(
        None,
        ge=0,
        description="Minimum price in TON",
    ),
    price_max: Optional[float] = Query(
        None,
        ge=0,
        description="Maximum price in TON",
    ),
    backdrop: Optional[str] = Query(
        None,
        description="Filter by backdrop",
    ),
    model: Optional[str] = Query(
        None,
        description="Filter by model",
    ),

    # Sorting
    sort: Optional[str] = Query(
        None,
        description="Sort order: price_asc, price_desc, name_asc, name_desc, recent",
    ),

    # Pagination
    page: int = Query(0, ge=0, description="Page number (0-indexed)"),
    page_size: int = Query(20, ge=1, le=100, description="Results per page"),

    # Facets
    include_facets: bool = Query(
        False,
        description="Include facet counts in response",
    ),
):
    """
    Search gifts with full-text search, filters, and pagination.

    **Search Features:**
    - Full-text search across name, description, collection_name
    - Typo tolerance for misspellings
    - Highlighted matches in results

    **Filter Examples:**
    - `?q=star&rarity=rare` - Search for "star" with rare rarity
    - `?is_on_sale=true&price_max=10` - On sale items under 10 TON
    - `?rarity=rare,legendary` - Multiple rarities

    **Sorting Options:**
    - `price_asc` / `price_desc` - Sort by price
    - `name_asc` / `name_desc` - Sort alphabetically
    - `recent` - Sort by update time

    **Response includes:**
    - `hits`: Array of matching gifts
    - `total`: Total number of matches
    - `facet_distribution`: Count of items per filter value (if requested)
    """
    search_service = get_search_service()

    # Build filters dict
    filters = {}

    if collection_id is not None:
        filters["collection_id"] = collection_id

    if rarity:
        rarity_list = [r.strip() for r in rarity.split(",")]
        filters["rarity"] = rarity_list if len(rarity_list) > 1 else rarity_list[0]

    if is_on_sale is not None:
        filters["is_on_sale"] = is_on_sale

    if price_min is not None:
        filters["price_min"] = price_min

    if price_max is not None:
        filters["price_max"] = price_max

    if backdrop:
        filters["backdrop"] = backdrop

    if model:
        filters["model"] = model

    # Build sort list
    sort_list = None
    if sort:
        sort_mapping = {
            "price_asc": ["price_ton:asc"],
            "price_desc": ["price_ton:desc"],
            "name_asc": ["name:asc"],
            "name_desc": ["name:desc"],
            "recent": ["updated_at:desc"],
        }
        sort_list = sort_mapping.get(sort)

    # Determine facets
    facets = None
    if include_facets:
        facets = ["rarity", "collection_id", "backdrop", "model", "is_on_sale"]

    try:
        result = search_service.search_gifts(
            query=q,
            filters=filters if filters else None,
            sort=sort_list,
            page=page,
            page_size=page_size,
            facets=facets,
        )

        return SearchResponse(
            hits=result["hits"],
            total=result["total"],
            page=result["page"],
            page_size=result["page_size"],
            total_pages=result["total_pages"],
            processing_time_ms=result["processing_time_ms"],
            facet_distribution=result.get("facet_distribution"),
            facet_stats=result.get("facet_stats"),
        )

    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Search service temporarily unavailable",
        )


@router.get("/search/autocomplete", response_model=AutocompleteResponse)
async def autocomplete(
    q: str = Query(..., min_length=1, description="Search query for autocomplete"),
    limit: int = Query(10, ge=1, le=20, description="Maximum suggestions"),
):
    """
    Get autocomplete suggestions for a search query.

    Optimized for speed and real-time suggestions.
    Returns gift names with highlighted matching portions.

    **Example:**
    - `?q=blu` - Returns gifts starting with or containing "blu"

    **Response:**
    - `suggestions`: Array of matching gifts with id, name, collection
    - `query`: Original query string
    """
    search_service = get_search_service()

    try:
        suggestions = search_service.autocomplete(query=q, limit=limit)

        return AutocompleteResponse(
            suggestions=suggestions,
            query=q,
        )

    except Exception as e:
        logger.error(f"Autocomplete error: {e}")
        # Return empty results instead of error for autocomplete
        return AutocompleteResponse(
            suggestions=[],
            query=q,
        )


@router.get("/search/facets", response_model=FacetsResponse)
async def get_facets(
    q: str = Query("", description="Optional search query to scope facets"),

    # Current filters (to get facets within filter context)
    rarity: Optional[str] = Query(None, description="Current rarity filter"),
    collection_id: Optional[int] = Query(None, description="Current collection filter"),
    is_on_sale: Optional[bool] = Query(None, description="Current sale status filter"),
    price_min: Optional[float] = Query(None, ge=0, description="Current min price filter"),
    price_max: Optional[float] = Query(None, ge=0, description="Current max price filter"),
):
    """
    Get facet counts for building filter UI.

    Returns count of gifts for each filter option,
    optionally scoped by current search query and filters.

    **Use Case:**
    Show filter options with counts:
    - Rarity: Common (150), Uncommon (89), Rare (45)
    - On Sale: Yes (120), No (164)

    **Response:**
    - `facet_distribution`: Counts per filter value
    - `facet_stats`: Statistics for numeric fields (min/max price)
    """
    search_service = get_search_service()

    # Build current filters
    filters = {}
    if collection_id is not None:
        filters["collection_id"] = collection_id
    if rarity:
        filters["rarity"] = rarity
    if is_on_sale is not None:
        filters["is_on_sale"] = is_on_sale
    if price_min is not None:
        filters["price_min"] = price_min
    if price_max is not None:
        filters["price_max"] = price_max

    try:
        result = search_service.get_facets(
            query=q,
            filters=filters if filters else None,
        )

        return FacetsResponse(
            facet_distribution=result.get("facet_distribution", {}),
            facet_stats=result.get("facet_stats"),
        )

    except Exception as e:
        logger.error(f"Facets error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Search service temporarily unavailable",
        )


@router.get("/search/health", response_model=SearchHealthResponse)
async def search_health():
    """
    Check search service health and get index statistics.

    **Response:**
    - `status`: "healthy" or "unhealthy"
    - `index_stats`: Document count and indexing status
    """
    client = get_search_client()

    is_healthy = client.health_check()
    stats = None

    if is_healthy:
        stats = client.get_index_stats()

    return SearchHealthResponse(
        status="healthy" if is_healthy else "unhealthy",
        index_stats=stats,
    )

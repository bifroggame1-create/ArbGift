"""
Base adapter interface for marketplace integrations.

All market adapters must implement this interface to ensure
consistent data flow through the aggregator.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional, AsyncIterator


class ListingStatus(Enum):
    """Listing status enum."""
    ACTIVE = "active"
    SOLD = "sold"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


@dataclass
class NormalizedListing:
    """
    Normalized listing data from any marketplace.

    All prices are converted to TON for comparison.
    """
    # Identifiers
    market_slug: str
    market_listing_id: str
    nft_address: str

    # Pricing
    price_raw: Decimal  # Original price in source currency
    currency: str  # TON, STARS, USDT, etc.
    price_ton: Decimal  # Normalized price in TON

    # Seller
    seller_address: Optional[str] = None

    # URLs
    listing_url: Optional[str] = None

    # Timing
    listed_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None

    # Status
    status: ListingStatus = ListingStatus.ACTIVE

    # Extra data
    extra: dict = field(default_factory=dict)


@dataclass
class NormalizedSale:
    """Normalized sale event from any marketplace."""
    market_slug: str
    nft_address: str

    # Pricing
    price_raw: Decimal
    currency: str
    price_ton: Decimal

    # Parties
    buyer_address: str
    seller_address: str

    # Transaction
    tx_hash: Optional[str] = None
    sold_at: datetime = None

    # Extra
    extra: dict = field(default_factory=dict)


class BaseMarketAdapter(ABC):
    """
    Abstract base class for marketplace adapters.

    Each adapter must implement methods to:
    - Fetch active listings
    - Fetch sales history
    - Convert prices to TON
    """

    def __init__(self, market_slug: str, config: dict = None):
        """
        Initialize adapter.

        Args:
            market_slug: Unique market identifier
            config: Adapter-specific configuration
        """
        self.market_slug = market_slug
        self.config = config or {}

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable market name."""
        pass

    @property
    @abstractmethod
    def website_url(self) -> str:
        """Market website URL."""
        pass

    @property
    def fee_buy_percent(self) -> Decimal:
        """Buyer fee percentage (0-100)."""
        return Decimal("0")

    @property
    def fee_sell_percent(self) -> Decimal:
        """Seller fee percentage (0-100)."""
        return Decimal("0")

    @abstractmethod
    async def fetch_collection_listings(
        self,
        collection_address: str,
        limit: int = 1000,
    ) -> list[NormalizedListing]:
        """
        Fetch active listings for a collection.

        Args:
            collection_address: NFT collection contract address
            limit: Maximum listings to fetch

        Returns:
            List of normalized listings
        """
        pass

    async def iter_collection_listings(
        self,
        collection_address: str,
        batch_size: int = 100,
    ) -> AsyncIterator[NormalizedListing]:
        """
        Iterate over collection listings with pagination.

        Default implementation uses fetch_collection_listings.
        Override for markets with native pagination.

        Args:
            collection_address: Collection address
            batch_size: Items per page

        Yields:
            NormalizedListing for each active listing
        """
        listings = await self.fetch_collection_listings(collection_address, limit=10000)
        for listing in listings:
            yield listing

    @abstractmethod
    async def fetch_nft_listing(
        self,
        nft_address: str,
    ) -> Optional[NormalizedListing]:
        """
        Fetch listing for a specific NFT.

        Args:
            nft_address: NFT contract address

        Returns:
            NormalizedListing if on sale, None otherwise
        """
        pass

    async def fetch_sales_history(
        self,
        collection_address: str = None,
        nft_address: str = None,
        limit: int = 100,
    ) -> list[NormalizedSale]:
        """
        Fetch sales history.

        Args:
            collection_address: Filter by collection
            nft_address: Filter by specific NFT
            limit: Maximum sales to fetch

        Returns:
            List of normalized sales (empty if not supported)
        """
        return []

    def build_listing_url(self, nft_address: str) -> str:
        """
        Build URL to view listing on marketplace.

        Args:
            nft_address: NFT contract address

        Returns:
            URL string
        """
        return f"{self.website_url}/nft/{nft_address}"

    @abstractmethod
    async def close(self):
        """Clean up resources."""
        pass

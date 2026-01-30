"""
Fragment Marketplace Adapter

Fragment is a TON-based marketplace for Telegram gifts, usernames, and other digital assets.
Unlike GetGems which has its own API, Fragment uses the TON blockchain directly,
so we query NFT data via TON API (tonapi.io).

This adapter:
- Fetches NFT listings via TON API collection/item endpoints
- Extracts sale info embedded in NFT data
- Normalizes data to unified format for the aggregator
"""
import logging
from datetime import datetime
from decimal import Decimal
from typing import Optional, AsyncIterator

from app.adapters.base import (
    BaseMarketAdapter,
    NormalizedListing,
    NormalizedSale,
    ListingStatus,
)
from app.config import settings
from app.indexer.ton_client import TonAPIClient, get_ton_client, NFTItemData

logger = logging.getLogger(__name__)

# Nanoton to TON conversion factor
NANOTON_DIVISOR = Decimal("1000000000")  # 1e9


class FragmentAdapter(BaseMarketAdapter):
    """
    Adapter for Fragment NFT marketplace.

    Fragment is a Telegram-affiliated marketplace for TON-based assets.
    It stores sale data on-chain, accessible via TON API.

    Key characteristics:
    - Uses TON blockchain for listings (no separate API)
    - NFT sale info is embedded in item data from TON API
    - 5% seller fee on sales
    - Supports Telegram gift NFTs
    """

    # Default Fragment collection address (Telegram Gifts)
    DEFAULT_COLLECTION = settings.FRAGMENT_COLLECTION

    def __init__(
        self,
        ton_client: TonAPIClient = None,
        config: dict = None,
    ):
        """
        Initialize Fragment adapter.

        Args:
            ton_client: Optional TonAPIClient instance. If not provided,
                       uses the global singleton from get_ton_client().
            config: Optional adapter-specific configuration.
        """
        super().__init__(market_slug="fragment", config=config)
        self._ton_client = ton_client
        self._owns_client = False  # Track if we created the client

    @property
    def ton_client(self) -> TonAPIClient:
        """
        Get TON API client, creating if necessary.

        Uses lazy initialization to avoid creating client if adapter
        is never used.
        """
        if self._ton_client is None:
            self._ton_client = get_ton_client()
        return self._ton_client

    @property
    def name(self) -> str:
        return "Fragment"

    @property
    def website_url(self) -> str:
        return "https://fragment.com"

    @property
    def fee_buy_percent(self) -> Decimal:
        """Fragment does not charge buyer fees."""
        return Decimal("0")

    @property
    def fee_sell_percent(self) -> Decimal:
        """Fragment charges 5% on sales."""
        return Decimal("5.0")

    async def close(self):
        """
        Clean up resources.

        Note: We don't close the TON client if it was injected or
        obtained from the global singleton, as other code may still
        need it.
        """
        if self._owns_client and self._ton_client is not None:
            await self._ton_client.close()
            self._ton_client = None

    def build_listing_url(self, nft_address: str) -> str:
        """
        Build URL to view NFT listing on Fragment.

        Args:
            nft_address: NFT contract address

        Returns:
            Fragment gift page URL
        """
        return f"https://fragment.com/gift/{nft_address}"

    def _nanoton_to_ton(self, nanoton: Optional[int]) -> Decimal:
        """
        Convert nanotons to TON.

        Args:
            nanoton: Amount in nanotons (1 TON = 1e9 nanotons)

        Returns:
            Amount in TON as Decimal
        """
        if nanoton is None or nanoton <= 0:
            return Decimal("0")
        return Decimal(str(nanoton)) / NANOTON_DIVISOR

    def _parse_nft_to_listing(self, nft: NFTItemData) -> Optional[NormalizedListing]:
        """
        Parse NFTItemData into NormalizedListing.

        Only returns a listing if the NFT is currently on sale.

        Args:
            nft: Parsed NFT item data from TON API

        Returns:
            NormalizedListing if on sale, None otherwise
        """
        try:
            # Only process NFTs that are on sale
            if not nft.is_on_sale:
                return None

            # Must have a valid sale price
            if not nft.sale_price_nanoton or nft.sale_price_nanoton <= 0:
                logger.debug(f"NFT {nft.address} on sale but no valid price")
                return None

            # Convert price to TON
            price_ton = self._nanoton_to_ton(nft.sale_price_nanoton)

            # Build listing
            return NormalizedListing(
                market_slug=self.market_slug,
                market_listing_id=nft.address,  # Use NFT address as unique listing ID
                nft_address=nft.address,
                price_raw=price_ton,
                currency="TON",
                price_ton=price_ton,
                seller_address=nft.owner_address,
                listing_url=self.build_listing_url(nft.address),
                listed_at=None,  # TON API doesn't provide listing timestamp directly
                expires_at=None,
                status=ListingStatus.ACTIVE,
                extra={
                    "name": nft.name,
                    "index": nft.index,
                    "collection_address": nft.collection_address,
                    "sale_market_address": nft.sale_market_address,
                    "marketplace_name": nft.sale_marketplace_name or "Fragment",
                    "description": nft.description,
                    "image_url": nft.image_url,
                    "attributes": nft.attributes,
                },
            )

        except Exception as e:
            logger.error(f"Failed to parse Fragment listing from NFT {nft.address}: {e}")
            return None

    async def fetch_collection_listings(
        self,
        collection_address: str,
        limit: int = 1000,
    ) -> list[NormalizedListing]:
        """
        Fetch active listings for a collection from Fragment.

        Queries the TON API for all NFTs in the collection, then filters
        for those currently on sale.

        Args:
            collection_address: NFT collection contract address
            limit: Maximum listings to fetch

        Returns:
            List of normalized listings sorted by price
        """
        listings = []
        offset = 0
        batch_size = min(1000, limit)  # TON API max is 1000

        logger.info(f"Fetching Fragment listings for collection {collection_address}")

        try:
            while len(listings) < limit:
                # Fetch batch of NFT items
                items = await self.ton_client.get_collection_items(
                    collection_address=collection_address,
                    limit=batch_size,
                    offset=offset,
                )

                if not items:
                    logger.debug(f"No more items at offset {offset}")
                    break

                # Parse each item, keeping only those on sale
                for nft in items:
                    if len(listings) >= limit:
                        break

                    listing = self._parse_nft_to_listing(nft)
                    if listing:
                        listings.append(listing)

                # Check if we got a full batch (more items may exist)
                if len(items) < batch_size:
                    break

                offset += len(items)
                logger.debug(f"Processed {offset} NFTs, found {len(listings)} listings")

            # Sort by price ascending
            listings.sort(key=lambda x: x.price_ton)

            logger.info(
                f"Found {len(listings)} active Fragment listings "
                f"for collection {collection_address}"
            )
            return listings

        except Exception as e:
            logger.error(f"Error fetching Fragment collection listings: {e}")
            raise

    async def iter_collection_listings(
        self,
        collection_address: str,
        batch_size: int = 100,
    ) -> AsyncIterator[NormalizedListing]:
        """
        Iterate over collection listings with pagination.

        Memory-efficient alternative to fetch_collection_listings for
        large collections.

        Args:
            collection_address: Collection address
            batch_size: Items per API request

        Yields:
            NormalizedListing for each active listing
        """
        try:
            async for nft in self.ton_client.iter_collection_items(
                collection_address=collection_address,
                batch_size=batch_size,
            ):
                listing = self._parse_nft_to_listing(nft)
                if listing:
                    yield listing

        except Exception as e:
            logger.error(f"Error iterating Fragment listings: {e}")
            raise

    async def fetch_nft_listing(
        self,
        nft_address: str,
    ) -> Optional[NormalizedListing]:
        """
        Fetch listing for a specific NFT.

        Args:
            nft_address: NFT contract address

        Returns:
            NormalizedListing if the NFT is on sale on Fragment, None otherwise
        """
        try:
            logger.debug(f"Fetching Fragment listing for NFT {nft_address}")

            # Get NFT details from TON API
            nft = await self.ton_client.get_nft_item(nft_address)

            if not nft:
                logger.debug(f"NFT {nft_address} not found")
                return None

            # Parse and return listing (None if not on sale)
            listing = self._parse_nft_to_listing(nft)

            if listing:
                logger.debug(f"NFT {nft_address} is on sale for {listing.price_ton} TON")
            else:
                logger.debug(f"NFT {nft_address} is not on sale")

            return listing

        except Exception as e:
            logger.error(f"Error fetching Fragment NFT listing for {nft_address}: {e}")
            return None

    async def fetch_sales_history(
        self,
        collection_address: str = None,
        nft_address: str = None,
        limit: int = 100,
    ) -> list[NormalizedSale]:
        """
        Fetch sales history from NFT transaction history.

        For Fragment, we query the TON API's NFT history endpoint which
        returns transfer events. We identify sales by looking for
        transfers that include TON payment.

        Args:
            collection_address: Filter by collection (not used for Fragment,
                              as we query individual NFT history)
            nft_address: Specific NFT address to get history for
            limit: Maximum sales to fetch

        Returns:
            List of normalized sales, newest first
        """
        if not nft_address:
            logger.warning("Fragment fetch_sales_history requires nft_address")
            return []

        try:
            logger.debug(f"Fetching Fragment sales history for NFT {nft_address}")

            # Get NFT history from TON API
            sale_events = await self.ton_client.get_nft_history(
                address=nft_address,
                limit=limit,
            )

            sales = []
            for event in sale_events:
                try:
                    # Convert price from nanotons
                    price_ton = self._nanoton_to_ton(event.price_nanoton)

                    if price_ton <= 0:
                        continue

                    sale = NormalizedSale(
                        market_slug=self.market_slug,
                        nft_address=event.nft_address,
                        price_raw=price_ton,
                        currency="TON",
                        price_ton=price_ton,
                        buyer_address=event.buyer_address,
                        seller_address=event.seller_address,
                        tx_hash=event.tx_hash,
                        sold_at=event.timestamp,
                        extra={
                            "marketplace": event.marketplace or "Fragment",
                            "tx_lt": event.tx_lt,
                        },
                    )
                    sales.append(sale)

                except Exception as e:
                    logger.warning(f"Failed to parse sale event: {e}")
                    continue

            logger.info(f"Found {len(sales)} sales for NFT {nft_address}")
            return sales

        except Exception as e:
            logger.error(f"Error fetching Fragment sales history: {e}")
            return []

    async def fetch_collection_sales_history(
        self,
        collection_address: str,
        limit: int = 100,
    ) -> list[NormalizedSale]:
        """
        Fetch recent sales for an entire collection.

        Note: This is expensive as we need to query each NFT individually.
        For bulk sales data, consider using an indexer or caching layer.

        Args:
            collection_address: Collection contract address
            limit: Maximum total sales to return

        Returns:
            List of sales across all NFTs in collection, newest first
        """
        logger.info(
            f"Fetching collection-wide sales history for {collection_address} "
            "(this may be slow)"
        )

        all_sales = []

        try:
            # Get a sample of NFTs from the collection
            items = await self.ton_client.get_collection_items(
                collection_address=collection_address,
                limit=min(limit, 100),  # Limit NFTs to query
                offset=0,
            )

            # Fetch history for each NFT
            for nft in items:
                if len(all_sales) >= limit:
                    break

                nft_sales = await self.fetch_sales_history(
                    nft_address=nft.address,
                    limit=10,  # Few sales per NFT
                )
                all_sales.extend(nft_sales)

            # Sort by timestamp descending and limit
            all_sales.sort(key=lambda s: s.sold_at or datetime.min, reverse=True)
            return all_sales[:limit]

        except Exception as e:
            logger.error(f"Error fetching Fragment collection sales: {e}")
            return []

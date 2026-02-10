"""
GetGems Marketplace Adapter

GetGems uses a GraphQL API for querying NFT listings and sales.
API Endpoint: https://api.getgems.io/graphql

This adapter:
- Queries active NFT sales via GraphQL
- Fetches sales history
- Normalizes data to unified format
"""
import asyncio
import logging
from datetime import datetime
from decimal import Decimal
from typing import Optional, AsyncIterator

import httpx

from app.adapters.base import (
    BaseMarketAdapter,
    NormalizedListing,
    NormalizedSale,
    ListingStatus,
)
from app.config import settings

logger = logging.getLogger(__name__)


# ============================================================
# GRAPHQL QUERIES
# ============================================================

# Query to get NFTs on sale in a collection
COLLECTION_SALES_QUERY = """
query CollectionSales($collectionAddress: String!, $first: Int!, $after: String) {
  nftItemsOnSale(
    filter: {
      collectionAddress: $collectionAddress
      saleType: fix_price
    }
    first: $first
    after: $after
    sort: PRICE_ASC
  ) {
    edges {
      cursor
      node {
        address
        index
        name
        collection {
          address
          name
        }
        content {
          image {
            originalUrl
          }
          video {
            originalUrl
          }
        }
        sale {
          ... on NftSaleFixPrice {
            fullPrice
            owner {
              address
            }
            marketplace {
              name
            }
            createdAt
          }
        }
      }
    }
    pageInfo {
      hasNextPage
      endCursor
    }
  }
}
"""

# Query to get single NFT sale info
NFT_SALE_QUERY = """
query NftSale($address: String!) {
  nftItemByAddress(address: $address) {
    address
    index
    name
    collection {
      address
      name
    }
    content {
      image {
        originalUrl
      }
    }
    sale {
      ... on NftSaleFixPrice {
        fullPrice
        owner {
          address
        }
        marketplace {
          name
        }
        createdAt
      }
    }
    owner {
      address
    }
  }
}
"""

# Query for sales history
SALES_HISTORY_QUERY = """
query SalesHistory($collectionAddress: String!, $first: Int!, $after: String) {
  nftSaleEvents(
    filter: {
      collectionAddress: $collectionAddress
      eventTypes: [sold]
    }
    first: $first
    after: $after
    sort: DATE_DESC
  ) {
    edges {
      cursor
      node {
        nftItem {
          address
          name
          collection {
            address
          }
        }
        eventType
        price
        buyer {
          address
        }
        seller {
          address
        }
        createdAt
        txHash
      }
    }
    pageInfo {
      hasNextPage
      endCursor
    }
  }
}
"""


class GetGemsAdapter(BaseMarketAdapter):
    """
    Adapter for GetGems NFT marketplace.

    GetGems is one of the largest TON NFT marketplaces.
    Uses GraphQL API for data fetching.
    """

    GRAPHQL_URL = "https://api.getgems.io/graphql"

    def __init__(self, config: dict = None):
        super().__init__(market_slug="getgems", config=config)
        self._client: Optional[httpx.AsyncClient] = None
        self._rate_limit = settings.GETGEMS_RATE_LIMIT
        self._last_request_time = 0.0

    @property
    def name(self) -> str:
        return "GetGems"

    @property
    def website_url(self) -> str:
        return "https://getgems.io"

    @property
    def fee_buy_percent(self) -> Decimal:
        # GetGems charges ~5% marketplace fee
        return Decimal("5.0")

    @property
    def fee_sell_percent(self) -> Decimal:
        return Decimal("0")

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(30.0),
                headers={
                    "Content-Type": "application/json",
                    "User-Agent": f"TONGiftAggregator/{settings.APP_VERSION}",
                },
            )
        return self._client

    async def close(self):
        """Close HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    async def _rate_limit_wait(self):
        """Wait to respect rate limit."""
        now = asyncio.get_event_loop().time()
        interval = 1.0 / self._rate_limit
        elapsed = now - self._last_request_time
        if elapsed < interval:
            await asyncio.sleep(interval - elapsed)
        self._last_request_time = asyncio.get_event_loop().time()

    async def _graphql_request(
        self,
        query: str,
        variables: dict,
        retries: int = 3,
    ) -> dict:
        """
        Execute GraphQL request.

        Args:
            query: GraphQL query string
            variables: Query variables
            retries: Number of retries

        Returns:
            Response data

        Raises:
            Exception on failure after all retries
        """
        client = await self._get_client()
        last_error = None

        for attempt in range(retries):
            try:
                await self._rate_limit_wait()

                response = await client.post(
                    self.GRAPHQL_URL,
                    json={"query": query, "variables": variables},
                )
                response.raise_for_status()

                data = response.json()

                if "errors" in data:
                    errors = data["errors"]
                    logger.error(f"GraphQL errors: {errors}")
                    raise Exception(f"GraphQL errors: {errors}")

                return data.get("data", {})

            except httpx.HTTPStatusError as e:
                last_error = e
                if e.response.status_code == 429:
                    wait_time = 2 ** attempt
                    logger.warning(f"Rate limited, waiting {wait_time}s")
                    await asyncio.sleep(wait_time)
                    continue
                raise

            except httpx.RequestError as e:
                last_error = e
                wait_time = 2 ** attempt
                logger.warning(f"Request error, retry {attempt + 1}/{retries} in {wait_time}s")
                await asyncio.sleep(wait_time)

        raise last_error or Exception("GraphQL request failed")

    def _parse_listing(self, node: dict) -> Optional[NormalizedListing]:
        """Parse GraphQL node into NormalizedListing."""
        try:
            sale = node.get("sale")
            if not sale:
                return None

            # Price is in nanotons
            price_nanoton = int(sale.get("fullPrice", 0))
            if price_nanoton <= 0:
                return None

            price_ton = Decimal(str(price_nanoton)) / Decimal("1000000000")
            nft_address = node.get("address")

            # Parse created timestamp
            created_at = sale.get("createdAt")
            listed_at = None
            if created_at:
                try:
                    listed_at = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                except Exception:
                    pass

            return NormalizedListing(
                market_slug=self.market_slug,
                market_listing_id=nft_address,  # Use NFT address as listing ID
                nft_address=nft_address,
                price_raw=price_ton,
                currency="TON",
                price_ton=price_ton,
                seller_address=sale.get("owner", {}).get("address"),
                listing_url=self.build_listing_url(nft_address),
                listed_at=listed_at,
                status=ListingStatus.ACTIVE,
                extra={
                    "name": node.get("name"),
                    "index": node.get("index"),
                    "collection": node.get("collection", {}).get("address"),
                    "marketplace": sale.get("marketplace", {}).get("name"),
                    "image_url": (node.get("content") or {}).get("image", {}).get("originalUrl"),
                },
            )

        except Exception as e:
            logger.error(f"Failed to parse GetGems listing: {e}")
            return None

    async def fetch_collection_listings(
        self,
        collection_address: str,
        limit: int = 1000,
    ) -> list[NormalizedListing]:
        """
        Fetch active listings for a collection.

        Args:
            collection_address: Collection contract address
            limit: Maximum listings to fetch

        Returns:
            List of normalized listings
        """
        listings = []
        cursor = None
        batch_size = min(100, limit)  # GetGems max is ~100 per request

        while len(listings) < limit:
            variables = {
                "collectionAddress": collection_address,
                "first": batch_size,
                "after": cursor,
            }

            try:
                data = await self._graphql_request(COLLECTION_SALES_QUERY, variables)
                sales_data = data.get("nftItemsOnSale", {})
                edges = sales_data.get("edges", [])

                if not edges:
                    break

                for edge in edges:
                    listing = self._parse_listing(edge.get("node", {}))
                    if listing:
                        listings.append(listing)

                # Check pagination
                page_info = sales_data.get("pageInfo", {})
                if not page_info.get("hasNextPage"):
                    break

                cursor = page_info.get("endCursor")

            except Exception as e:
                logger.error(f"Error fetching GetGems listings: {e}")
                break

        logger.info(f"Fetched {len(listings)} listings from GetGems for {collection_address}")
        return listings[:limit]

    async def iter_collection_listings(
        self,
        collection_address: str,
        batch_size: int = 100,
    ) -> AsyncIterator[NormalizedListing]:
        """Iterate over collection listings with pagination."""
        cursor = None

        while True:
            variables = {
                "collectionAddress": collection_address,
                "first": batch_size,
                "after": cursor,
            }

            try:
                data = await self._graphql_request(COLLECTION_SALES_QUERY, variables)
                sales_data = data.get("nftItemsOnSale", {})
                edges = sales_data.get("edges", [])

                if not edges:
                    break

                for edge in edges:
                    listing = self._parse_listing(edge.get("node", {}))
                    if listing:
                        yield listing

                # Check pagination
                page_info = sales_data.get("pageInfo", {})
                if not page_info.get("hasNextPage"):
                    break

                cursor = page_info.get("endCursor")

            except Exception as e:
                logger.error(f"Error iterating GetGems listings: {e}")
                break

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
        try:
            variables = {"address": nft_address}
            data = await self._graphql_request(NFT_SALE_QUERY, variables)

            nft_data = data.get("nftItemByAddress")
            if not nft_data:
                return None

            return self._parse_listing(nft_data)

        except Exception as e:
            logger.error(f"Error fetching GetGems NFT listing: {e}")
            return None

    async def fetch_sales_history(
        self,
        collection_address: str = None,
        nft_address: str = None,
        limit: int = 100,
    ) -> list[NormalizedSale]:
        """
        Fetch sales history for a collection.

        Args:
            collection_address: Collection address
            nft_address: Specific NFT (not supported, ignored)
            limit: Maximum sales

        Returns:
            List of normalized sales
        """
        if not collection_address:
            return []

        sales = []
        cursor = None
        batch_size = min(100, limit)

        while len(sales) < limit:
            variables = {
                "collectionAddress": collection_address,
                "first": batch_size,
                "after": cursor,
            }

            try:
                data = await self._graphql_request(SALES_HISTORY_QUERY, variables)
                events_data = data.get("nftSaleEvents", {})
                edges = events_data.get("edges", [])

                if not edges:
                    break

                for edge in edges:
                    sale = self._parse_sale_event(edge.get("node", {}))
                    if sale:
                        sales.append(sale)

                # Check pagination
                page_info = events_data.get("pageInfo", {})
                if not page_info.get("hasNextPage"):
                    break

                cursor = page_info.get("endCursor")

            except Exception as e:
                logger.error(f"Error fetching GetGems sales history: {e}")
                break

        logger.info(f"Fetched {len(sales)} sales from GetGems for {collection_address}")
        return sales[:limit]

    def _parse_sale_event(self, node: dict) -> Optional[NormalizedSale]:
        """Parse GraphQL sale event node."""
        try:
            nft_item = node.get("nftItem", {})
            nft_address = nft_item.get("address")

            if not nft_address:
                return None

            # Price in nanotons
            price_nanoton = int(node.get("price", 0))
            if price_nanoton <= 0:
                return None

            price_ton = Decimal(str(price_nanoton)) / Decimal("1000000000")

            # Parse timestamp
            created_at = node.get("createdAt")
            sold_at = datetime.now()
            if created_at:
                try:
                    sold_at = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                except Exception:
                    pass

            return NormalizedSale(
                market_slug=self.market_slug,
                nft_address=nft_address,
                price_raw=price_ton,
                currency="TON",
                price_ton=price_ton,
                buyer_address=node.get("buyer", {}).get("address", ""),
                seller_address=node.get("seller", {}).get("address", ""),
                tx_hash=node.get("txHash"),
                sold_at=sold_at,
                extra={
                    "name": nft_item.get("name"),
                    "event_type": node.get("eventType"),
                },
            )

        except Exception as e:
            logger.error(f"Failed to parse GetGems sale event: {e}")
            return None

    def build_listing_url(self, nft_address: str) -> str:
        """Build URL to NFT page on GetGems."""
        return f"https://getgems.io/nft/{nft_address}"

"""
Tonnel Marketplace Adapter.

Tonnel is a TON NFT marketplace. This adapter provides integration
for fetching listings and sales data.

NOTE: Tonnel API documentation is limited. This adapter uses common
REST API patterns and should be updated when official API docs are available.
"""
import logging
from datetime import datetime
from decimal import Decimal
from typing import Optional, AsyncIterator, Dict, Any

import httpx

from app.adapters.base import (
    BaseMarketAdapter,
    NormalizedListing,
    NormalizedSale,
    ListingStatus,
)

logger = logging.getLogger(__name__)

NANOTON_DIVISOR = Decimal("1000000000")


class TonnelAdapter(BaseMarketAdapter):
    """
    Adapter for Tonnel NFT marketplace.

    Tonnel is a community-driven TON marketplace. This adapter attempts
    to integrate with their API using common REST patterns.

    To be updated when official API documentation is available.
    """

    def __init__(self):
        super().__init__(
            slug="tonnel",
            name="Tonnel",
            base_url="https://api.tonnel.network",  # Assumed API endpoint
            fee_buy_percent=Decimal("2.5"),
            fee_sell_percent=Decimal("2.5"),
        )

    async def fetch_collection_listings(
        self, collection_address: str, limit: int = 100
    ) -> AsyncIterator[NormalizedListing]:
        """
        Fetch active listings for a collection.

        Expected API endpoint: GET /api/v1/nfts/on-sale
        Query params: collection={address}, limit={limit}
        """
        await self._ensure_rate_limit()

        endpoint = f"{self.base_url}/api/v1/nfts/on-sale"
        params = {
            "collection": collection_address,
            "limit": limit,
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(endpoint, params=params)
                response.raise_for_status()
                data = response.json()

            # Parse response - adjust based on actual API response format
            items = data.get("items", data.get("nfts", []))

            for item in items:
                yield self._parse_listing(item)

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.warning(f"Tonnel API endpoint not found: {endpoint}")
                return
            logger.error(f"HTTP error fetching Tonnel listings: {e}")
            raise
        except Exception as e:
            logger.error(f"Error fetching Tonnel collection listings: {e}")
            raise

    async def fetch_nft_listing(
        self, nft_address: str
    ) -> Optional[NormalizedListing]:
        """
        Fetch single NFT listing.

        Expected endpoint: GET /api/v1/nfts/{address}
        """
        await self._ensure_rate_limit()

        endpoint = f"{self.base_url}/api/v1/nfts/{nft_address}"

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(endpoint)
                response.raise_for_status()
                data = response.json()

            # Check if item is on sale
            if not data.get("on_sale", False):
                return None

            return self._parse_listing(data)

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return None
            logger.error(f"HTTP error fetching Tonnel NFT: {e}")
            raise
        except Exception as e:
            logger.error(f"Error fetching Tonnel NFT listing: {e}")
            raise

    async def fetch_sales_history(
        self, nft_address: str, limit: int = 10
    ) -> AsyncIterator[NormalizedSale]:
        """
        Fetch sales history for an NFT.

        Expected endpoint: GET /api/v1/nfts/{address}/history
        """
        await self._ensure_rate_limit()

        endpoint = f"{self.base_url}/api/v1/nfts/{nft_address}/history"
        params = {"limit": limit}

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(endpoint, params=params)
                response.raise_for_status()
                data = response.json()

            sales = data.get("sales", data.get("history", []))

            for sale in sales:
                yield self._parse_sale(sale, nft_address)

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.info(f"No history found for {nft_address}")
                return
            logger.error(f"HTTP error fetching Tonnel sales: {e}")
            raise
        except Exception as e:
            logger.error(f"Error fetching Tonnel sales history: {e}")
            raise

    def _parse_listing(self, data: Dict[str, Any]) -> NormalizedListing:
        """
        Parse API response into NormalizedListing.

        Adjust field names based on actual Tonnel API response.
        """
        nft_address = data.get("address", data.get("nft_address"))
        price_nanoton = data.get("price", data.get("sale_price", 0))

        # Convert price
        price_ton = Decimal(price_nanoton) / NANOTON_DIVISOR

        return NormalizedListing(
            nft_address=nft_address,
            price_ton=price_ton,
            seller_address=data.get("owner", {}).get("address")
            if isinstance(data.get("owner"), dict)
            else data.get("owner"),
            market_slug=self.slug,
            listing_url=f"https://tonnel.network/nft/{nft_address}",
            status=ListingStatus.ACTIVE,
            listed_at=self._parse_timestamp(data.get("listed_at")),
        )

    def _parse_sale(self, data: Dict[str, Any], nft_address: str) -> NormalizedSale:
        """Parse sale data from API response."""
        price_nanoton = data.get("price", 0)
        price_ton = Decimal(price_nanoton) / NANOTON_DIVISOR

        return NormalizedSale(
            nft_address=nft_address,
            price_ton=price_ton,
            buyer_address=data.get("buyer", {}).get("address")
            if isinstance(data.get("buyer"), dict)
            else data.get("buyer"),
            seller_address=data.get("seller", {}).get("address")
            if isinstance(data.get("seller"), dict)
            else data.get("seller"),
            sale_date=self._parse_timestamp(data.get("sale_date", data.get("timestamp"))),
            tx_hash=data.get("tx_hash", data.get("transaction_hash")),
            market_slug=self.slug,
        )

    def _parse_timestamp(self, ts: Optional[Any]) -> datetime:
        """Parse timestamp from various formats."""
        if not ts:
            return datetime.utcnow()

        if isinstance(ts, int):
            return datetime.fromtimestamp(ts)

        if isinstance(ts, str):
            try:
                return datetime.fromisoformat(ts.replace("Z", "+00:00"))
            except Exception:
                return datetime.utcnow()

        return datetime.utcnow()

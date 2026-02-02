"""
NFT Pricing — median цена гифта по рыночным данным.
"""
import logging
import statistics
from decimal import Decimal
from typing import Optional, Dict
from datetime import datetime, timedelta

import httpx

logger = logging.getLogger(__name__)


class PricingService:
    """Calculate NFT prices from market data."""

    def __init__(self, tonapi_key: Optional[str] = None):
        headers = {}
        if tonapi_key:
            headers["Authorization"] = f"Bearer {tonapi_key}"
        self.client = httpx.AsyncClient(
            base_url="https://tonapi.io/v2",
            headers=headers,
            timeout=15.0,
        )
        # Simple cache: nft_address -> (price, timestamp)
        self._cache: Dict[str, tuple[Decimal, datetime]] = {}
        self._cache_ttl = timedelta(minutes=5)

    async def get_nft_price(self, nft_address: str) -> Optional[Decimal]:
        """
        Get estimated price for NFT.

        Uses cached value if available and fresh.
        Falls back to collection floor price if no direct listing.
        """
        # Check cache
        if nft_address in self._cache:
            price, cached_at = self._cache[nft_address]
            if datetime.utcnow() - cached_at < self._cache_ttl:
                return price

        try:
            # Try to get NFT sale info
            resp = await self.client.get(f"/nfts/{nft_address}")
            resp.raise_for_status()
            data = resp.json()

            # Check if on sale
            sale = data.get("sale")
            if sale and sale.get("price", {}).get("value"):
                price_nano = int(sale["price"]["value"])
                price_ton = Decimal(price_nano) / Decimal(10**9)
                self._cache[nft_address] = (price_ton, datetime.utcnow())
                return price_ton

            # Fall back to collection floor
            collection = data.get("collection", {}).get("address")
            if collection:
                floor = await self.get_collection_floor(collection)
                if floor:
                    self._cache[nft_address] = (floor, datetime.utcnow())
                    return floor

            return None

        except Exception as e:
            logger.error(f"Price fetch failed for {nft_address}: {e}")
            return None

    async def get_collection_floor(
        self,
        collection_address: str,
    ) -> Optional[Decimal]:
        """Get floor price for collection."""
        try:
            resp = await self.client.get(
                f"/nfts/collections/{collection_address}",
            )
            resp.raise_for_status()
            data = resp.json()

            # Try to extract floor from metadata
            # tonapi sometimes includes floor_price
            if "floor_price" in data:
                return Decimal(str(data["floor_price"]))

            return None

        except Exception as e:
            logger.error(f"Floor price fetch failed: {e}")
            return None

    async def close(self):
        await self.client.aclose()

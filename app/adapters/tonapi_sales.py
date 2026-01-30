"""
TON API Sales Adapter - Fallback adapter for marketplaces without APIs.

This adapter monitors NFT transfer events on TON blockchain to detect sales.
Works as a universal fallback when marketplace-specific APIs are unavailable.
"""
import logging
from datetime import datetime
from decimal import Decimal
from typing import Optional, AsyncIterator, List

from app.adapters.base import (
    BaseMarketAdapter,
    NormalizedListing,
    NormalizedSale,
    ListingStatus,
)
from app.indexer.ton_client import TonAPIClient, get_ton_client

logger = logging.getLogger(__name__)

NANOTON_DIVISOR = Decimal("1000000000")


class TONAPISalesAdapter(BaseMarketAdapter):
    """
    Universal adapter for detecting sales via TON blockchain events.

    Works by monitoring NFT transfers and analyzing transaction comments
    to identify marketplace sales. Can detect sales from any marketplace.
    """

    def __init__(self):
        super().__init__(
            slug="tonapi-sales",
            name="TON Blockchain Sales",
            base_url="https://tonapi.io",
            fee_buy_percent=Decimal("0"),
            fee_sell_percent=Decimal("0"),
        )
        self.ton_client: Optional[TonAPIClient] = None

    async def initialize(self):
        """Initialize TON API client."""
        if not self.ton_client:
            self.ton_client = await get_ton_client()
        await super().initialize()

    async def fetch_collection_listings(
        self, collection_address: str, limit: int = 100
    ) -> AsyncIterator[NormalizedListing]:
        """
        Cannot fetch active listings via blockchain - only historical sales.
        This method is not implemented for this adapter.
        """
        logger.warning("TONAPISalesAdapter cannot fetch active listings")
        return
        yield  # Make this a generator

    async def fetch_nft_listing(
        self, nft_address: str
    ) -> Optional[NormalizedListing]:
        """Cannot fetch single listing via blockchain."""
        return None

    async def fetch_sales_history(
        self, nft_address: str, limit: int = 10
    ) -> AsyncIterator[NormalizedSale]:
        """
        Fetch NFT sales history from TON blockchain events.

        Analyzes NFT transfer events to detect sales (transfers with payment).
        """
        if not self.ton_client:
            await self.initialize()

        try:
            history = await self.ton_client.get_nft_history(nft_address)

            for event in history.get("events", [])[:limit]:
                # Check if this is a sale (NFT transfer with payment)
                actions = event.get("actions", [])
                for action in actions:
                    if action.get("type") != "NftItemTransfer":
                        continue

                    # Look for payment in the same transaction
                    payment = None
                    for other_action in actions:
                        if other_action.get("type") == "TonTransfer":
                            payment = other_action.get("TonTransfer", {}).get("amount")
                            break

                    if not payment:
                        continue  # Not a sale, just a transfer

                    nft_info = action.get("NftItemTransfer", {})

                    yield NormalizedSale(
                        nft_address=nft_address,
                        price_ton=Decimal(payment) / NANOTON_DIVISOR,
                        buyer_address=nft_info.get("recipient", {}).get("address"),
                        seller_address=nft_info.get("sender", {}).get("address"),
                        sale_date=datetime.fromtimestamp(event.get("timestamp", 0)),
                        tx_hash=event.get("event_id"),
                        market_slug=self.slug,
                    )

        except Exception as e:
            logger.error(f"Error fetching sales history for {nft_address}: {e}")
            raise

    async def fetch_collection_sales(
        self, collection_address: str, limit: int = 100
    ) -> List[NormalizedSale]:
        """
        Fetch recent sales for entire collection.

        Useful for monitoring new sales across all collection NFTs.
        """
        if not self.ton_client:
            await self.initialize()

        sales = []
        try:
            # Get collection items
            items = await self.ton_client.get_collection_items(
                collection_address, limit=1000
            )

            # Check recent sales for each item (expensive!)
            for item in items[:50]:  # Limit to 50 items to avoid timeouts
                nft_address = item.get("address")
                if not nft_address:
                    continue

                async for sale in self.fetch_sales_history(nft_address, limit=1):
                    sales.append(sale)
                    if len(sales) >= limit:
                        return sales

        except Exception as e:
            logger.error(f"Error fetching collection sales for {collection_address}: {e}")
            raise

        return sales

"""
TON API Client for NFT indexing.

Uses tonapi.io v2 API for:
- Fetching NFT collections
- Fetching NFT items
- Getting sale information
- Tracking ownership changes

API Documentation: https://docs.tonconsole.com/tonapi/api-v2
"""
import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional, AsyncIterator
from urllib.parse import urljoin

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


@dataclass
class NFTCollectionData:
    """Parsed NFT collection data."""
    address: str
    name: str
    description: Optional[str]
    image_url: Optional[str]
    cover_url: Optional[str]
    external_url: Optional[str]
    owner_address: Optional[str]
    items_count: int
    raw_metadata: dict


@dataclass
class NFTItemData:
    """Parsed NFT item data."""
    address: str
    collection_address: str
    index: int
    owner_address: str
    name: str
    description: Optional[str]
    image_url: Optional[str]
    animation_url: Optional[str]
    attributes: list[dict]
    metadata_url: Optional[str]
    raw_metadata: dict
    # Sale info (if on sale)
    is_on_sale: bool
    sale_price_nanoton: Optional[int]
    sale_market_address: Optional[str]
    sale_marketplace_name: Optional[str]


@dataclass
class NFTSaleEvent:
    """Parsed NFT sale event."""
    nft_address: str
    buyer_address: str
    seller_address: str
    price_nanoton: int
    marketplace: Optional[str]
    tx_hash: str
    tx_lt: int
    timestamp: datetime


class TonAPIClient:
    """
    Async client for TON API (tonapi.io).

    Handles:
    - Rate limiting
    - Retries with exponential backoff
    - Response parsing
    - Pagination
    """

    def __init__(
        self,
        base_url: str = None,
        api_key: str = None,
        rate_limit: float = None,
        timeout: int = None,
    ):
        self.base_url = base_url or settings.TONAPI_BASE_URL
        self.api_key = api_key or settings.TONAPI_KEY
        self.rate_limit = rate_limit or settings.TONAPI_RATE_LIMIT
        self.timeout = timeout or settings.TONAPI_TIMEOUT

        # Rate limiting state
        self._last_request_time = 0.0
        self._request_interval = 1.0 / self.rate_limit

        # HTTP client (created on first use)
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None or self._client.is_closed:
            headers = {
                "Accept": "application/json",
                "User-Agent": f"TONGiftAggregator/{settings.APP_VERSION}",
            }
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"

            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                headers=headers,
                timeout=httpx.Timeout(self.timeout),
            )
        return self._client

    async def close(self):
        """Close HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    async def _rate_limit_wait(self):
        """Wait to respect rate limit."""
        now = asyncio.get_event_loop().time()
        elapsed = now - self._last_request_time
        if elapsed < self._request_interval:
            await asyncio.sleep(self._request_interval - elapsed)
        self._last_request_time = asyncio.get_event_loop().time()

    async def _request(
        self,
        method: str,
        endpoint: str,
        params: dict = None,
        retries: int = 3,
    ) -> dict:
        """
        Make API request with rate limiting and retries.

        Args:
            method: HTTP method
            endpoint: API endpoint
            params: Query parameters
            retries: Number of retries on failure

        Returns:
            Parsed JSON response

        Raises:
            httpx.HTTPStatusError: On HTTP errors after all retries
        """
        client = await self._get_client()
        last_error = None

        for attempt in range(retries):
            try:
                await self._rate_limit_wait()

                response = await client.request(
                    method=method,
                    url=endpoint,
                    params=params,
                )
                response.raise_for_status()
                return response.json()

            except httpx.HTTPStatusError as e:
                last_error = e
                status = e.response.status_code

                # Don't retry on 4xx errors (except 429)
                if 400 <= status < 500 and status != 429:
                    logger.error(f"Client error {status} for {endpoint}: {e.response.text}")
                    raise

                # Rate limited - wait and retry
                if status == 429:
                    wait_time = 2 ** attempt
                    logger.warning(f"Rate limited, waiting {wait_time}s before retry")
                    await asyncio.sleep(wait_time)
                    continue

                # Server error - retry with backoff
                wait_time = 2 ** attempt
                logger.warning(f"Server error {status}, retry {attempt + 1}/{retries} in {wait_time}s")
                await asyncio.sleep(wait_time)

            except httpx.RequestError as e:
                last_error = e
                wait_time = 2 ** attempt
                logger.warning(f"Request error: {e}, retry {attempt + 1}/{retries} in {wait_time}s")
                await asyncio.sleep(wait_time)

        raise last_error

    # ================================================================
    # COLLECTION METHODS
    # ================================================================

    async def get_collection(self, address: str) -> NFTCollectionData:
        """
        Get NFT collection metadata.

        API: GET /v2/nft/collections/{address}

        Args:
            address: Collection contract address

        Returns:
            Parsed collection data
        """
        data = await self._request("GET", f"/v2/nft/collections/{address}")

        metadata = data.get("metadata", {})
        previews = data.get("previews", [])

        # Find best preview image
        image_url = None
        for preview in previews:
            if preview.get("resolution") in ["500x500", "1500x1500"]:
                image_url = preview.get("url")
                break
        if not image_url and previews:
            image_url = previews[0].get("url")

        return NFTCollectionData(
            address=data.get("address"),
            name=metadata.get("name", "Unknown Collection"),
            description=metadata.get("description"),
            image_url=metadata.get("image") or image_url,
            cover_url=metadata.get("cover_image"),
            external_url=metadata.get("external_url") or metadata.get("external_link"),
            owner_address=data.get("owner", {}).get("address"),
            items_count=data.get("next_item_index", 0),
            raw_metadata=data,
        )

    async def get_collection_items(
        self,
        collection_address: str,
        limit: int = 1000,
        offset: int = 0,
    ) -> list[NFTItemData]:
        """
        Get NFT items in a collection.

        API: GET /v2/nft/collections/{address}/items

        Args:
            collection_address: Collection contract address
            limit: Max items to fetch (max 1000)
            offset: Pagination offset

        Returns:
            List of parsed NFT items
        """
        data = await self._request(
            "GET",
            f"/v2/nft/collections/{collection_address}/items",
            params={"limit": min(limit, 1000), "offset": offset},
        )

        items = []
        for raw_item in data.get("nft_items", []):
            item = self._parse_nft_item(raw_item, collection_address)
            if item:
                items.append(item)

        return items

    async def iter_collection_items(
        self,
        collection_address: str,
        batch_size: int = 1000,
    ) -> AsyncIterator[NFTItemData]:
        """
        Iterate over all items in a collection with pagination.

        Args:
            collection_address: Collection contract address
            batch_size: Items per request

        Yields:
            NFTItemData for each item
        """
        offset = 0
        while True:
            items = await self.get_collection_items(
                collection_address,
                limit=batch_size,
                offset=offset,
            )

            if not items:
                break

            for item in items:
                yield item

            if len(items) < batch_size:
                break

            offset += len(items)
            logger.info(f"Fetched {offset} items from collection {collection_address}")

    # ================================================================
    # NFT ITEM METHODS
    # ================================================================

    async def get_nft_item(self, address: str) -> NFTItemData:
        """
        Get single NFT item details.

        API: GET /v2/nft/items/{address}

        Args:
            address: NFT item contract address

        Returns:
            Parsed NFT item data
        """
        data = await self._request("GET", f"/v2/nft/items/{address}")
        collection_address = data.get("collection", {}).get("address", "")
        return self._parse_nft_item(data, collection_address)

    async def get_nft_history(
        self,
        address: str,
        limit: int = 50,
    ) -> list[NFTSaleEvent]:
        """
        Get NFT transaction history (sales).

        API: GET /v2/nft/items/{address}/history

        Args:
            address: NFT item address
            limit: Max events to fetch

        Returns:
            List of sale events
        """
        data = await self._request(
            "GET",
            f"/v2/nft/items/{address}/history",
            params={"limit": limit},
        )

        sales = []
        for event in data.get("events", []):
            sale = self._parse_sale_event(event, address)
            if sale:
                sales.append(sale)

        return sales

    # ================================================================
    # ACCOUNT METHODS
    # ================================================================

    async def get_account_nfts(
        self,
        address: str,
        collection: str = None,
        limit: int = 1000,
        offset: int = 0,
    ) -> list[NFTItemData]:
        """
        Get NFTs owned by an account.

        API: GET /v2/accounts/{address}/nfts

        Args:
            address: Account address
            collection: Optional collection filter
            limit: Max items
            offset: Pagination offset

        Returns:
            List of NFT items
        """
        params = {"limit": limit, "offset": offset}
        if collection:
            params["collection"] = collection

        data = await self._request(
            "GET",
            f"/v2/accounts/{address}/nfts",
            params=params,
        )

        items = []
        for raw_item in data.get("nft_items", []):
            collection_address = raw_item.get("collection", {}).get("address", "")
            item = self._parse_nft_item(raw_item, collection_address)
            if item:
                items.append(item)

        return items

    # ================================================================
    # PARSING HELPERS
    # ================================================================

    def _parse_nft_item(self, raw: dict, collection_address: str) -> Optional[NFTItemData]:
        """Parse raw NFT item data from API response."""
        try:
            metadata = raw.get("metadata", {})
            sale = raw.get("sale")

            # Extract attributes
            attributes = []
            for attr in metadata.get("attributes", []):
                attributes.append({
                    "trait_type": attr.get("trait_type", ""),
                    "value": attr.get("value", ""),
                })

            # Get image URL from previews or metadata
            previews = raw.get("previews", [])
            image_url = metadata.get("image")
            for preview in previews:
                if preview.get("resolution") in ["500x500", "1500x1500"]:
                    image_url = preview.get("url")
                    break

            # Parse sale info
            is_on_sale = sale is not None
            sale_price = None
            sale_market = None
            sale_marketplace = None

            if sale:
                price_data = sale.get("price", {})
                sale_price = int(price_data.get("value", 0))
                sale_market = sale.get("address")
                market_info = sale.get("market", {})
                sale_marketplace = market_info.get("name")

            return NFTItemData(
                address=raw.get("address"),
                collection_address=collection_address,
                index=raw.get("index", 0),
                owner_address=raw.get("owner", {}).get("address"),
                name=metadata.get("name", f"#{raw.get('index', 0)}"),
                description=metadata.get("description"),
                image_url=image_url,
                animation_url=metadata.get("animation_url") or metadata.get("lottie"),
                attributes=attributes,
                metadata_url=raw.get("metadata", {}).get("uri"),
                raw_metadata=raw,
                is_on_sale=is_on_sale,
                sale_price_nanoton=sale_price,
                sale_market_address=sale_market,
                sale_marketplace_name=sale_marketplace,
            )

        except Exception as e:
            logger.error(f"Failed to parse NFT item: {e}")
            return None

    def _parse_sale_event(self, event: dict, nft_address: str) -> Optional[NFTSaleEvent]:
        """Parse sale event from NFT history."""
        try:
            actions = event.get("actions", [])

            # Find NFT transfer and TON transfer in actions
            nft_transfer = None
            ton_transfer = None

            for action in actions:
                action_type = action.get("type")
                if action_type == "NftItemTransfer":
                    nft_transfer = action.get("NftItemTransfer") or action.get("nft_item_transfer", {})
                elif action_type == "TonTransfer":
                    ton_transfer = action.get("TonTransfer") or action.get("ton_transfer", {})

            # Must have both to be a sale
            if not nft_transfer or not ton_transfer:
                return None

            # Extract sale details
            buyer = nft_transfer.get("recipient", {}).get("address")
            seller = nft_transfer.get("sender", {}).get("address")
            amount = int(ton_transfer.get("amount", 0))

            if not buyer or not seller or amount <= 0:
                return None

            timestamp = event.get("timestamp")
            if isinstance(timestamp, int):
                dt = datetime.fromtimestamp(timestamp)
            else:
                dt = datetime.now()

            return NFTSaleEvent(
                nft_address=nft_address,
                buyer_address=buyer,
                seller_address=seller,
                price_nanoton=amount,
                marketplace=event.get("description"),  # Usually contains marketplace name
                tx_hash=event.get("event_id", ""),
                tx_lt=event.get("lt", 0),
                timestamp=dt,
            )

        except Exception as e:
            logger.error(f"Failed to parse sale event: {e}")
            return None


# Global client instance
_client: Optional[TonAPIClient] = None


def get_ton_client() -> TonAPIClient:
    """Get global TON API client instance."""
    global _client
    if _client is None:
        _client = TonAPIClient()
    return _client

"""
MRKT Marketplace Adapter

MRKT is a Telegram-based gift marketplace with TON payments.
API Endpoint: https://api.tgmrkt.io/api/v1

This adapter:
- Authenticates using Telegram initData
- Fetches active gift listings
- Normalizes data to unified format
"""
import asyncio
import logging
import time
from datetime import datetime
from decimal import Decimal
from typing import Optional

import httpx

from app.adapters.base import (
    BaseMarketAdapter,
    NormalizedListing,
    ListingStatus,
)
from app.config import settings

logger = logging.getLogger(__name__)


class MRKTAuthError(Exception):
    """Raised when MRKT authentication fails."""
    pass


class MRKTAPIError(Exception):
    """Raised when MRKT API request fails."""
    pass


class MRKTAdapter(BaseMarketAdapter):
    """
    Adapter for MRKT gift marketplace.

    MRKT is a Telegram-based marketplace for TON gifts.
    Requires Telegram initData for authentication.
    """

    BASE_URL = "https://api.tgmrkt.io/api/v1"
    WEBSITE_URL = "https://tgmrkt.io"

    # Token refresh threshold (refresh if expires in less than this many seconds)
    TOKEN_REFRESH_THRESHOLD = 300  # 5 minutes

    def __init__(self, config: dict = None):
        super().__init__(market_slug="mrkt", config=config)
        self._client: Optional[httpx.AsyncClient] = None

        # Rate limiting - use config, then settings, then default
        self._rate_limit = self.config.get("rate_limit", settings.MRKT_RATE_LIMIT)
        self._last_request_time = 0.0

        # Authentication state
        self._access_token: Optional[str] = None
        self._token_expires_at: float = 0.0
        self._auth_lock = asyncio.Lock()

        # Get initData from config or environment
        self._init_data = self.config.get("init_data") or settings.MRKT_INIT_DATA

    @property
    def name(self) -> str:
        return "MRKT"

    @property
    def website_url(self) -> str:
        return self.WEBSITE_URL

    @property
    def fee_buy_percent(self) -> Decimal:
        return Decimal("2.0")

    @property
    def fee_sell_percent(self) -> Decimal:
        return Decimal("2.0")

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(30.0),
                headers={
                    "Content-Type": "application/json",
                    "User-Agent": f"TONGiftAggregator/{settings.APP_VERSION}",
                    "Accept": "application/json",
                },
            )
        return self._client

    async def close(self):
        """Close HTTP client and clear auth state."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
        self._access_token = None
        self._token_expires_at = 0.0

    async def _rate_limit_wait(self):
        """Wait to respect rate limit."""
        now = asyncio.get_event_loop().time()
        interval = 1.0 / self._rate_limit
        elapsed = now - self._last_request_time
        if elapsed < interval:
            await asyncio.sleep(interval - elapsed)
        self._last_request_time = asyncio.get_event_loop().time()

    def _is_token_valid(self) -> bool:
        """Check if current access token is valid and not expiring soon."""
        if not self._access_token:
            return False
        return time.time() < (self._token_expires_at - self.TOKEN_REFRESH_THRESHOLD)

    async def _authenticate(self, force: bool = False) -> str:
        """
        Authenticate with MRKT API using Telegram initData.

        Args:
            force: Force re-authentication even if token is valid

        Returns:
            Access token

        Raises:
            MRKTAuthError: If authentication fails
        """
        async with self._auth_lock:
            # Double-check after acquiring lock
            if not force and self._is_token_valid():
                return self._access_token

            if not self._init_data:
                raise MRKTAuthError(
                    "MRKT_INIT_DATA not configured. "
                    "Set the MRKT_INIT_DATA environment variable with Telegram initData."
                )

            client = await self._get_client()

            try:
                logger.debug("Authenticating with MRKT API")

                response = await client.post(
                    f"{self.BASE_URL}/auth",
                    json={"data": self._init_data},
                )

                if response.status_code == 401:
                    raise MRKTAuthError("Invalid or expired Telegram initData")

                response.raise_for_status()
                data = response.json()

                # Extract access token from response
                # API may return token in different formats
                access_token = data.get("access_token") or data.get("token") or data.get("accessToken")

                if not access_token:
                    logger.error(f"MRKT auth response missing token: {data}")
                    raise MRKTAuthError("Authentication response missing access_token")

                # Extract expiration if provided, otherwise default to 1 hour
                expires_in = data.get("expires_in", 3600)

                self._access_token = access_token
                self._token_expires_at = time.time() + expires_in

                logger.info("Successfully authenticated with MRKT API")
                return self._access_token

            except httpx.HTTPStatusError as e:
                logger.error(f"MRKT auth HTTP error: {e.response.status_code} - {e.response.text}")
                raise MRKTAuthError(f"Authentication failed: HTTP {e.response.status_code}")
            except httpx.RequestError as e:
                logger.error(f"MRKT auth request error: {e}")
                raise MRKTAuthError(f"Authentication request failed: {e}")

    async def _ensure_authenticated(self) -> str:
        """Ensure we have a valid access token, refreshing if needed."""
        if self._is_token_valid():
            return self._access_token
        return await self._authenticate()

    async def _api_request(
        self,
        method: str,
        endpoint: str,
        params: dict = None,
        json_data: dict = None,
        retries: int = 3,
    ) -> dict:
        """
        Make authenticated API request with retry logic.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            params: Query parameters
            json_data: JSON body data
            retries: Number of retries

        Returns:
            Response JSON data

        Raises:
            MRKTAPIError: On API failure after all retries
        """
        client = await self._get_client()
        last_error = None
        url = f"{self.BASE_URL}{endpoint}"

        for attempt in range(retries):
            try:
                await self._rate_limit_wait()

                # Get fresh token if needed
                token = await self._ensure_authenticated()

                headers = {"Authorization": f"Bearer {token}"}

                response = await client.request(
                    method=method,
                    url=url,
                    params=params,
                    json=json_data,
                    headers=headers,
                )

                # Handle auth errors - refresh token and retry
                if response.status_code == 401:
                    logger.warning("MRKT token expired, refreshing...")
                    await self._authenticate(force=True)
                    continue

                # Handle rate limiting
                if response.status_code == 429:
                    retry_after = int(response.headers.get("Retry-After", 2 ** attempt))
                    logger.warning(f"MRKT rate limited, waiting {retry_after}s")
                    await asyncio.sleep(retry_after)
                    continue

                response.raise_for_status()
                return response.json()

            except httpx.HTTPStatusError as e:
                last_error = e
                if e.response.status_code >= 500:
                    # Server error, retry with backoff
                    wait_time = 2 ** attempt
                    logger.warning(f"MRKT server error {e.response.status_code}, retry {attempt + 1}/{retries} in {wait_time}s")
                    await asyncio.sleep(wait_time)
                    continue
                raise MRKTAPIError(f"API error: HTTP {e.response.status_code} - {e.response.text}")

            except httpx.RequestError as e:
                last_error = e
                wait_time = 2 ** attempt
                logger.warning(f"MRKT request error, retry {attempt + 1}/{retries} in {wait_time}s: {e}")
                await asyncio.sleep(wait_time)

        raise MRKTAPIError(f"API request failed after {retries} retries: {last_error}")

    def _parse_listing(self, item: dict) -> Optional[NormalizedListing]:
        """
        Parse MRKT listing item into NormalizedListing.

        Expected format:
        {
            "id": "...",
            "gift": {"name": "...", "collection": "..."},
            "price": 10.5,
            "currency": "TON",
            "seller": {"address": "..."}
        }
        """
        try:
            listing_id = item.get("id")
            if not listing_id:
                return None

            # Extract price
            price_raw = item.get("price")
            if price_raw is None:
                return None

            price = Decimal(str(price_raw))
            if price <= 0:
                return None

            # Get currency (default to TON)
            currency = item.get("currency", "TON").upper()

            # Convert price to TON if needed
            price_ton = price
            if currency == "STARS":
                price_ton = price * Decimal(str(settings.STARS_TO_TON_RATE))
            elif currency != "TON":
                # Unknown currency, use raw price
                logger.warning(f"Unknown currency {currency} for listing {listing_id}")

            # Extract gift/NFT info
            gift_data = item.get("gift", {})
            gift_name = gift_data.get("name", "")
            collection = gift_data.get("collection", "")

            # NFT address - try multiple possible fields
            nft_address = (
                item.get("nft_address") or
                item.get("nftAddress") or
                gift_data.get("address") or
                gift_data.get("nft_address") or
                listing_id  # Fallback to listing ID
            )

            # Seller info
            seller_data = item.get("seller", {})
            seller_address = seller_data.get("address") or seller_data.get("wallet")

            # Parse timestamps if available
            listed_at = None
            created_at = item.get("created_at") or item.get("createdAt")
            if created_at:
                try:
                    if isinstance(created_at, (int, float)):
                        listed_at = datetime.fromtimestamp(created_at)
                    else:
                        listed_at = datetime.fromisoformat(str(created_at).replace("Z", "+00:00"))
                except Exception:
                    pass

            return NormalizedListing(
                market_slug=self.market_slug,
                market_listing_id=str(listing_id),
                nft_address=nft_address,
                price_raw=price,
                currency=currency,
                price_ton=price_ton,
                seller_address=seller_address,
                listing_url=self.build_listing_url(listing_id),
                listed_at=listed_at,
                status=ListingStatus.ACTIVE,
                extra={
                    "name": gift_name,
                    "collection": collection,
                    "seller_id": seller_data.get("id"),
                    "raw_data": item,
                },
            )

        except Exception as e:
            logger.error(f"Failed to parse MRKT listing: {e}", exc_info=True)
            return None

    async def fetch_collection_listings(
        self,
        collection_address: str,
        limit: int = 1000,
    ) -> list[NormalizedListing]:
        """
        Fetch active listings for a collection.

        Args:
            collection_address: NFT collection contract address or collection name
            limit: Maximum listings to fetch

        Returns:
            List of normalized listings
        """
        listings = []
        offset = 0
        batch_size = min(100, limit)  # Use reasonable batch size

        while len(listings) < limit:
            try:
                params = {
                    "limit": batch_size,
                    "offset": offset,
                }

                # Try to filter by collection if API supports it
                if collection_address:
                    params["collection"] = collection_address

                data = await self._api_request("GET", "/gifts/saling", params=params)

                # Handle response format
                items = data.get("gifts", [])
                if not items:
                    # Try alternative response formats
                    items = data.get("data", []) or data.get("items", []) or data.get("listings", [])

                if not items:
                    break

                for item in items:
                    listing = self._parse_listing(item)
                    if listing:
                        # Filter by collection if API doesn't support it natively
                        if collection_address:
                            item_collection = listing.extra.get("collection", "")
                            if item_collection and collection_address.lower() not in item_collection.lower():
                                continue
                        listings.append(listing)

                    if len(listings) >= limit:
                        break

                # Check for pagination
                total = data.get("total", 0)
                if offset + batch_size >= total or len(items) < batch_size:
                    break

                offset += batch_size

            except MRKTAuthError:
                # Re-raise auth errors
                raise
            except Exception as e:
                logger.error(f"Error fetching MRKT listings: {e}")
                break

        logger.info(f"Fetched {len(listings)} listings from MRKT for collection {collection_address}")
        return listings[:limit]

    async def fetch_nft_listing(
        self,
        nft_address: str,
    ) -> Optional[NormalizedListing]:
        """
        Fetch listing for a specific NFT.

        Args:
            nft_address: NFT contract address or listing ID

        Returns:
            NormalizedListing if on sale, None otherwise
        """
        try:
            # First try to fetch all listings and find the matching one
            # MRKT API may not have a direct endpoint for single listing lookup
            params = {"limit": 500}
            data = await self._api_request("GET", "/gifts/saling", params=params)

            items = data.get("gifts", []) or data.get("data", []) or data.get("items", [])

            for item in items:
                listing = self._parse_listing(item)
                if listing:
                    # Match by NFT address or listing ID
                    if (listing.nft_address == nft_address or
                        listing.market_listing_id == nft_address):
                        return listing

            return None

        except MRKTAuthError:
            raise
        except Exception as e:
            logger.error(f"Error fetching MRKT NFT listing: {e}")
            return None

    def build_listing_url(self, listing_id: str) -> str:
        """Build URL to listing page on MRKT."""
        return f"{self.WEBSITE_URL}/gift/{listing_id}"


# Factory function for easy instantiation
def create_mrkt_adapter(config: dict = None) -> MRKTAdapter:
    """
    Create MRKT adapter instance.

    Args:
        config: Optional configuration dict with:
            - init_data: Telegram initData string (overrides env var)
            - rate_limit: Requests per second (default: 3.0)

    Returns:
        Configured MRKTAdapter instance
    """
    return MRKTAdapter(config=config)

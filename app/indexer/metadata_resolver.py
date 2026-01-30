"""
Metadata Resolver for NFT metadata and images.

Handles:
- IPFS URL resolution through multiple gateways
- HTTP/HTTPS URL fetching
- TON Storage URLs
- JSON metadata parsing
- Image URL extraction
"""
import asyncio
import hashlib
import logging
import re
from dataclasses import dataclass
from typing import Optional
from urllib.parse import urlparse, urljoin

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


@dataclass
class ResolvedMetadata:
    """Resolved and parsed NFT metadata."""
    name: str
    description: Optional[str]
    image_url: Optional[str]
    animation_url: Optional[str]
    attributes: list[dict]
    external_url: Optional[str]
    raw: dict
    source_url: str
    resolved_via: str  # 'direct', 'ipfs_gateway', 'ton_storage'


class MetadataResolver:
    """
    Resolves NFT metadata from various sources.

    Supports:
    - IPFS URLs (ipfs://...)
    - HTTP/HTTPS URLs
    - TON Storage URLs (ton://...)
    - Data URLs (data:application/json;...)
    """

    # IPFS URL patterns
    IPFS_PATTERNS = [
        re.compile(r'^ipfs://(.+)$'),
        re.compile(r'^/ipfs/(.+)$'),
        re.compile(r'ipfs/([a-zA-Z0-9]+.*)$'),
    ]

    # TON Storage pattern
    TON_STORAGE_PATTERN = re.compile(r'^ton://storage/(.+)$')

    def __init__(
        self,
        ipfs_gateways: list[str] = None,
        timeout: int = None,
        max_retries: int = 3,
    ):
        self.ipfs_gateways = ipfs_gateways or settings.IPFS_GATEWAYS
        self.timeout = timeout or settings.IPFS_TIMEOUT
        self.max_retries = max_retries
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(self.timeout),
                follow_redirects=True,
                headers={
                    "User-Agent": f"TONGiftAggregator/{settings.APP_VERSION}",
                    "Accept": "application/json, */*",
                },
            )
        return self._client

    async def close(self):
        """Close HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    def _extract_ipfs_hash(self, url: str) -> Optional[str]:
        """Extract IPFS hash/path from URL."""
        for pattern in self.IPFS_PATTERNS:
            match = pattern.search(url)
            if match:
                return match.group(1)
        return None

    def _build_ipfs_urls(self, ipfs_hash: str) -> list[str]:
        """Build gateway URLs for IPFS hash."""
        return [f"{gateway}{ipfs_hash}" for gateway in self.ipfs_gateways]

    def _is_ton_storage(self, url: str) -> bool:
        """Check if URL is TON Storage."""
        return url.startswith("ton://storage/")

    def _build_ton_storage_url(self, url: str) -> str:
        """Convert TON Storage URL to HTTP gateway URL."""
        match = self.TON_STORAGE_PATTERN.match(url)
        if match:
            bag_id = match.group(1)
            # TON Storage gateway (official)
            return f"https://storage.ton.org/{bag_id}"
        return url

    async def _fetch_json(self, url: str) -> Optional[dict]:
        """Fetch JSON from URL."""
        try:
            client = await self._get_client()
            response = await client.get(url)
            response.raise_for_status()

            # Handle different content types
            content_type = response.headers.get("content-type", "")
            if "application/json" in content_type or url.endswith(".json"):
                return response.json()

            # Try parsing as JSON anyway
            try:
                return response.json()
            except Exception:
                logger.warning(f"Non-JSON response from {url}")
                return None

        except httpx.HTTPStatusError as e:
            logger.warning(f"HTTP error fetching {url}: {e.response.status_code}")
            return None
        except httpx.RequestError as e:
            logger.warning(f"Request error fetching {url}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching {url}: {e}")
            return None

    async def _fetch_with_ipfs_fallback(self, ipfs_hash: str) -> tuple[Optional[dict], str]:
        """Try fetching from multiple IPFS gateways."""
        urls = self._build_ipfs_urls(ipfs_hash)

        for url in urls:
            data = await self._fetch_json(url)
            if data:
                return data, url

        return None, ""

    async def resolve(self, metadata_url: str) -> Optional[ResolvedMetadata]:
        """
        Resolve metadata from URL.

        Args:
            metadata_url: Original metadata URL (IPFS, HTTP, TON Storage)

        Returns:
            ResolvedMetadata with parsed content, or None on failure
        """
        if not metadata_url:
            return None

        resolved_via = "direct"
        source_url = metadata_url
        data = None

        try:
            # Handle data: URLs (inline JSON)
            if metadata_url.startswith("data:"):
                data = self._parse_data_url(metadata_url)
                resolved_via = "data_url"

            # Handle IPFS URLs
            elif ipfs_hash := self._extract_ipfs_hash(metadata_url):
                data, source_url = await self._fetch_with_ipfs_fallback(ipfs_hash)
                resolved_via = "ipfs_gateway"

            # Handle TON Storage URLs
            elif self._is_ton_storage(metadata_url):
                http_url = self._build_ton_storage_url(metadata_url)
                data = await self._fetch_json(http_url)
                source_url = http_url
                resolved_via = "ton_storage"

            # Handle HTTP/HTTPS URLs
            elif metadata_url.startswith(("http://", "https://")):
                data = await self._fetch_json(metadata_url)
                resolved_via = "direct"

            else:
                logger.warning(f"Unknown URL scheme: {metadata_url}")
                return None

            if not data:
                logger.warning(f"Failed to resolve metadata from {metadata_url}")
                return None

            # Parse the metadata
            return self._parse_metadata(data, source_url, resolved_via)

        except Exception as e:
            logger.error(f"Error resolving metadata {metadata_url}: {e}")
            return None

    def _parse_data_url(self, data_url: str) -> Optional[dict]:
        """Parse data: URL with inline JSON."""
        import base64
        import json

        try:
            # data:application/json;base64,{base64_data}
            # data:application/json,{json_data}
            if ",base64," in data_url or ";base64," in data_url:
                # Base64 encoded
                parts = data_url.split(",", 1)
                if len(parts) == 2:
                    decoded = base64.b64decode(parts[1])
                    return json.loads(decoded)
            elif "," in data_url:
                # URL encoded or plain JSON
                parts = data_url.split(",", 1)
                if len(parts) == 2:
                    from urllib.parse import unquote
                    return json.loads(unquote(parts[1]))
        except Exception as e:
            logger.error(f"Failed to parse data URL: {e}")

        return None

    def _parse_metadata(
        self,
        data: dict,
        source_url: str,
        resolved_via: str,
    ) -> ResolvedMetadata:
        """Parse raw metadata dict into structured format."""

        # Handle different attribute formats
        attributes = []
        raw_attrs = data.get("attributes", [])

        if isinstance(raw_attrs, list):
            for attr in raw_attrs:
                if isinstance(attr, dict):
                    attributes.append({
                        "trait_type": attr.get("trait_type", attr.get("traitType", "")),
                        "value": str(attr.get("value", "")),
                    })

        # Resolve image URL (might be IPFS)
        image_url = self._resolve_media_url(
            data.get("image") or data.get("image_url"),
            source_url,
        )

        # Resolve animation URL
        animation_url = self._resolve_media_url(
            data.get("animation_url") or data.get("lottie") or data.get("video"),
            source_url,
        )

        return ResolvedMetadata(
            name=data.get("name", "Unnamed"),
            description=data.get("description"),
            image_url=image_url,
            animation_url=animation_url,
            attributes=attributes,
            external_url=data.get("external_url") or data.get("external_link"),
            raw=data,
            source_url=source_url,
            resolved_via=resolved_via,
        )

    def _resolve_media_url(self, url: Optional[str], base_url: str) -> Optional[str]:
        """
        Resolve media URL, handling IPFS and relative paths.

        Args:
            url: Original URL (might be IPFS or relative)
            base_url: Base URL for resolving relative paths

        Returns:
            Resolved HTTP URL
        """
        if not url:
            return None

        # Already HTTP(S)
        if url.startswith(("http://", "https://")):
            return url

        # IPFS URL - use first gateway
        if ipfs_hash := self._extract_ipfs_hash(url):
            return f"{self.ipfs_gateways[0]}{ipfs_hash}"

        # TON Storage
        if self._is_ton_storage(url):
            return self._build_ton_storage_url(url)

        # Relative URL
        if base_url and not url.startswith("data:"):
            try:
                return urljoin(base_url, url)
            except Exception:
                pass

        return url


class ImageProcessor:
    """
    Processes and caches NFT images.

    Can:
    - Download images from resolved URLs
    - Upload to CDN (S3/R2/etc)
    - Generate thumbnails
    - Return CDN URLs
    """

    def __init__(self):
        self.enabled = settings.CDN_ENABLED
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(30.0),
                follow_redirects=True,
            )
        return self._client

    async def close(self):
        """Close HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    def _generate_cdn_key(self, url: str) -> str:
        """Generate unique CDN key from URL."""
        url_hash = hashlib.sha256(url.encode()).hexdigest()[:16]
        # Try to preserve extension
        parsed = urlparse(url)
        path = parsed.path.lower()
        ext = ".png"  # default
        for e in [".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg"]:
            if path.endswith(e):
                ext = e
                break
        return f"nft-images/{url_hash}{ext}"

    async def process_image(self, image_url: str) -> Optional[str]:
        """
        Download image and upload to CDN.

        Args:
            image_url: Source image URL

        Returns:
            CDN URL or original URL if CDN disabled
        """
        if not self.enabled:
            return image_url

        if not image_url:
            return None

        try:
            # Download image
            client = await self._get_client()
            response = await client.get(image_url)
            response.raise_for_status()

            image_data = response.content
            content_type = response.headers.get("content-type", "image/png")

            # Generate CDN key
            cdn_key = self._generate_cdn_key(image_url)

            # Upload to CDN (implement based on your CDN)
            cdn_url = await self._upload_to_cdn(cdn_key, image_data, content_type)

            return cdn_url or image_url

        except Exception as e:
            logger.warning(f"Failed to process image {image_url}: {e}")
            return image_url

    async def _upload_to_cdn(
        self,
        key: str,
        data: bytes,
        content_type: str,
    ) -> Optional[str]:
        """
        Upload to CDN storage.

        Override this method for your specific CDN (S3, R2, etc.)
        """
        # Example: Cloudflare R2 / S3 upload
        # import boto3
        # s3 = boto3.client('s3', ...)
        # s3.put_object(Bucket='bucket', Key=key, Body=data, ContentType=content_type)
        # return f"https://cdn.example.com/{key}"

        logger.warning("CDN upload not implemented, returning None")
        return None


# Global instances
_metadata_resolver: Optional[MetadataResolver] = None
_image_processor: Optional[ImageProcessor] = None


def get_metadata_resolver() -> MetadataResolver:
    """Get global metadata resolver."""
    global _metadata_resolver
    if _metadata_resolver is None:
        _metadata_resolver = MetadataResolver()
    return _metadata_resolver


def get_image_processor() -> ImageProcessor:
    """Get global image processor."""
    global _image_processor
    if _image_processor is None:
        _image_processor = ImageProcessor()
    return _image_processor

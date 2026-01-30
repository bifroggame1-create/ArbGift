"""
Redis Pub/Sub helper for broadcasting real-time updates.

This module provides a unified interface for publishing price updates
from Celery workers and subscribing to them from WebSocket connections.
"""
import asyncio
import json
import logging
from contextlib import asynccontextmanager
from dataclasses import dataclass, asdict
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import AsyncGenerator, Callable, Optional, Any

import redis.asyncio as aioredis

from app.config import settings

logger = logging.getLogger(__name__)


class MessageType(str, Enum):
    """Types of WebSocket messages."""
    PRICE_UPDATE = "price_update"
    NEW_LISTING = "new_listing"
    LISTING_REMOVED = "listing_removed"
    COLLECTION_UPDATE = "collection_update"
    HEARTBEAT = "heartbeat"
    ERROR = "error"


# Redis channel names
CHANNEL_ALL_PRICES = "ws:prices:all"
CHANNEL_COLLECTION_PREFIX = "ws:prices:collection:"
CHANNEL_GIFT_PREFIX = "ws:prices:gift:"


@dataclass
class PriceUpdateMessage:
    """Price update message structure."""
    type: MessageType
    gift_id: int
    collection_id: int
    price_ton: str
    price_raw: Optional[str] = None
    currency: str = "TON"
    market_slug: str = ""
    market_listing_id: Optional[str] = None
    seller_address: Optional[str] = None
    listing_url: Optional[str] = None
    nft_address: Optional[str] = None
    nft_name: Optional[str] = None
    timestamp: Optional[str] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow().isoformat() + "Z"
        if isinstance(self.type, MessageType):
            self.type = self.type.value

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "type": self.type,
            "data": {
                "gift_id": self.gift_id,
                "collection_id": self.collection_id,
                "price_ton": self.price_ton,
                "price_raw": self.price_raw,
                "currency": self.currency,
                "market_slug": self.market_slug,
                "market_listing_id": self.market_listing_id,
                "seller_address": self.seller_address,
                "listing_url": self.listing_url,
                "nft_address": self.nft_address,
                "nft_name": self.nft_name,
            },
            "timestamp": self.timestamp,
        }

    def to_json(self) -> str:
        """Serialize to JSON string."""
        return json.dumps(self.to_dict())


class DecimalEncoder(json.JSONEncoder):
    """JSON encoder that handles Decimal types."""
    def default(self, obj):
        if isinstance(obj, Decimal):
            return str(obj)
        return super().default(obj)


class RedisPubSub:
    """
    Redis Pub/Sub manager for real-time price updates.

    This class provides both publishing (for Celery workers) and
    subscribing (for WebSocket handlers) capabilities.
    """

    _instance: Optional["RedisPubSub"] = None
    _lock = asyncio.Lock()

    def __init__(self):
        self._redis: Optional[aioredis.Redis] = None
        self._pubsub: Optional[aioredis.client.PubSub] = None
        self._subscribers: dict[str, set[Callable]] = {}
        self._listener_task: Optional[asyncio.Task] = None
        self._running = False

    @classmethod
    async def get_instance(cls) -> "RedisPubSub":
        """Get or create singleton instance."""
        if cls._instance is None:
            async with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
                    await cls._instance.connect()
        return cls._instance

    async def connect(self) -> None:
        """Connect to Redis."""
        if self._redis is not None:
            return

        try:
            self._redis = aioredis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
                max_connections=20,
            )
            # Test connection
            await self._redis.ping()
            logger.info("Connected to Redis for pub/sub")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise

    async def close(self) -> None:
        """Close Redis connection and cleanup."""
        self._running = False

        if self._listener_task:
            self._listener_task.cancel()
            try:
                await self._listener_task
            except asyncio.CancelledError:
                pass
            self._listener_task = None

        if self._pubsub:
            await self._pubsub.unsubscribe()
            await self._pubsub.close()
            self._pubsub = None

        if self._redis:
            await self._redis.close()
            self._redis = None

        self._subscribers.clear()
        logger.info("Redis pub/sub connection closed")

    async def publish(
        self,
        message: PriceUpdateMessage,
    ) -> int:
        """
        Publish a price update message to relevant channels.

        Publishes to:
        - All prices channel
        - Collection-specific channel
        - Gift-specific channel

        Args:
            message: The price update message to publish

        Returns:
            Number of subscribers that received the message
        """
        if self._redis is None:
            await self.connect()

        json_message = message.to_json()
        total_receivers = 0

        try:
            # Publish to all channels
            channels = [
                CHANNEL_ALL_PRICES,
                f"{CHANNEL_COLLECTION_PREFIX}{message.collection_id}",
                f"{CHANNEL_GIFT_PREFIX}{message.gift_id}",
            ]

            for channel in channels:
                receivers = await self._redis.publish(channel, json_message)
                total_receivers += receivers

            logger.debug(
                f"Published {message.type} for gift {message.gift_id} "
                f"to {total_receivers} receivers"
            )

        except Exception as e:
            logger.error(f"Failed to publish message: {e}")
            raise

        return total_receivers

    async def subscribe(
        self,
        channels: list[str],
        callback: Callable[[str, dict], Any],
    ) -> None:
        """
        Subscribe to one or more channels.

        Args:
            channels: List of channel names to subscribe to
            callback: Async function called with (channel, message_dict)
        """
        if self._redis is None:
            await self.connect()

        if self._pubsub is None:
            self._pubsub = self._redis.pubsub()

        # Register callback for each channel
        for channel in channels:
            if channel not in self._subscribers:
                self._subscribers[channel] = set()
                await self._pubsub.subscribe(channel)
            self._subscribers[channel].add(callback)

        # Start listener if not running
        if not self._running:
            self._running = True
            self._listener_task = asyncio.create_task(self._listen())

        logger.debug(f"Subscribed to channels: {channels}")

    async def unsubscribe(
        self,
        channels: list[str],
        callback: Callable[[str, dict], Any],
    ) -> None:
        """
        Unsubscribe a callback from channels.

        Args:
            channels: List of channel names
            callback: The callback to remove
        """
        for channel in channels:
            if channel in self._subscribers:
                self._subscribers[channel].discard(callback)
                if not self._subscribers[channel]:
                    del self._subscribers[channel]
                    if self._pubsub:
                        await self._pubsub.unsubscribe(channel)

        logger.debug(f"Unsubscribed from channels: {channels}")

    async def _listen(self) -> None:
        """Background task that listens for messages and dispatches to callbacks."""
        try:
            while self._running and self._pubsub:
                try:
                    message = await asyncio.wait_for(
                        self._pubsub.get_message(ignore_subscribe_messages=True),
                        timeout=1.0,
                    )

                    if message is None:
                        continue

                    channel = message.get("channel")
                    data = message.get("data")

                    if channel and data and channel in self._subscribers:
                        try:
                            parsed_data = json.loads(data)
                        except json.JSONDecodeError:
                            logger.warning(f"Invalid JSON in message: {data}")
                            continue

                        # Dispatch to all callbacks for this channel
                        for callback in list(self._subscribers.get(channel, [])):
                            try:
                                if asyncio.iscoroutinefunction(callback):
                                    await callback(channel, parsed_data)
                                else:
                                    callback(channel, parsed_data)
                            except Exception as e:
                                logger.error(f"Error in subscriber callback: {e}")

                except asyncio.TimeoutError:
                    continue
                except Exception as e:
                    logger.error(f"Error in pub/sub listener: {e}")
                    await asyncio.sleep(1)

        except asyncio.CancelledError:
            logger.debug("Pub/sub listener cancelled")
            raise


# Synchronous publisher for Celery workers
class SyncRedisPubSub:
    """
    Synchronous Redis pub/sub client for use in Celery workers.

    Celery workers run synchronous code, so we need a sync client.
    """

    def __init__(self):
        import redis
        self._redis = redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
        )

    def publish(self, message: PriceUpdateMessage) -> int:
        """
        Publish a message synchronously.

        Args:
            message: The message to publish

        Returns:
            Number of subscribers that received the message
        """
        json_message = message.to_json()
        total_receivers = 0

        channels = [
            CHANNEL_ALL_PRICES,
            f"{CHANNEL_COLLECTION_PREFIX}{message.collection_id}",
            f"{CHANNEL_GIFT_PREFIX}{message.gift_id}",
        ]

        for channel in channels:
            receivers = self._redis.publish(channel, json_message)
            total_receivers += receivers

        return total_receivers

    def publish_price_update(
        self,
        gift_id: int,
        collection_id: int,
        price_ton: str,
        market_slug: str,
        **kwargs,
    ) -> int:
        """
        Convenience method to publish a price update.

        Args:
            gift_id: The NFT/gift ID
            collection_id: The collection ID
            price_ton: Price in TON as string
            market_slug: Market identifier
            **kwargs: Additional message fields

        Returns:
            Number of receivers
        """
        message = PriceUpdateMessage(
            type=MessageType.PRICE_UPDATE,
            gift_id=gift_id,
            collection_id=collection_id,
            price_ton=price_ton,
            market_slug=market_slug,
            **kwargs,
        )
        return self.publish(message)

    def publish_new_listing(
        self,
        gift_id: int,
        collection_id: int,
        price_ton: str,
        market_slug: str,
        **kwargs,
    ) -> int:
        """Publish a new listing notification."""
        message = PriceUpdateMessage(
            type=MessageType.NEW_LISTING,
            gift_id=gift_id,
            collection_id=collection_id,
            price_ton=price_ton,
            market_slug=market_slug,
            **kwargs,
        )
        return self.publish(message)

    def publish_listing_removed(
        self,
        gift_id: int,
        collection_id: int,
        market_slug: str,
        **kwargs,
    ) -> int:
        """Publish a listing removed notification."""
        message = PriceUpdateMessage(
            type=MessageType.LISTING_REMOVED,
            gift_id=gift_id,
            collection_id=collection_id,
            price_ton="0",
            market_slug=market_slug,
            **kwargs,
        )
        return self.publish(message)

    def close(self) -> None:
        """Close the Redis connection."""
        self._redis.close()


# Global sync publisher instance for Celery
_sync_pubsub: Optional[SyncRedisPubSub] = None


def get_sync_pubsub() -> SyncRedisPubSub:
    """Get or create the synchronous pub/sub client for Celery workers."""
    global _sync_pubsub
    if _sync_pubsub is None:
        _sync_pubsub = SyncRedisPubSub()
    return _sync_pubsub


# Helper functions for broadcasting from tasks
def broadcast_price_update(
    gift_id: int,
    collection_id: int,
    price_ton: str,
    market_slug: str,
    **kwargs,
) -> int:
    """
    Broadcast a price update from a Celery task.

    Usage in tasks:
        from app.core.pubsub import broadcast_price_update

        broadcast_price_update(
            gift_id=123,
            collection_id=1,
            price_ton="10.5",
            market_slug="getgems",
            nft_name="Cool Gift",
        )
    """
    return get_sync_pubsub().publish_price_update(
        gift_id=gift_id,
        collection_id=collection_id,
        price_ton=price_ton,
        market_slug=market_slug,
        **kwargs,
    )


def broadcast_new_listing(
    gift_id: int,
    collection_id: int,
    price_ton: str,
    market_slug: str,
    **kwargs,
) -> int:
    """Broadcast a new listing notification from a Celery task."""
    return get_sync_pubsub().publish_new_listing(
        gift_id=gift_id,
        collection_id=collection_id,
        price_ton=price_ton,
        market_slug=market_slug,
        **kwargs,
    )


def broadcast_listing_removed(
    gift_id: int,
    collection_id: int,
    market_slug: str,
    **kwargs,
) -> int:
    """Broadcast a listing removed notification from a Celery task."""
    return get_sync_pubsub().publish_listing_removed(
        gift_id=gift_id,
        collection_id=collection_id,
        market_slug=market_slug,
        **kwargs,
    )

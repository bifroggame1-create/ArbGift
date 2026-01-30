"""
WebSocket support for real-time price updates.

Provides WebSocket endpoints for:
- All price updates: ws://host/ws/prices
- Collection updates: ws://host/ws/collection/{collection_id}
- Single gift updates: ws://host/ws/gift/{gift_id}
"""
import asyncio
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, Set

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, status
from starlette.websockets import WebSocketState

from app.core.pubsub import (
    RedisPubSub,
    CHANNEL_ALL_PRICES,
    CHANNEL_COLLECTION_PREFIX,
    CHANNEL_GIFT_PREFIX,
    MessageType,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["WebSocket"])


class SubscriptionType(str, Enum):
    """Types of WebSocket subscriptions."""
    ALL_PRICES = "all_prices"
    COLLECTION = "collection"
    GIFT = "gift"


@dataclass
class WebSocketConnection:
    """Represents a WebSocket connection with its subscriptions."""
    websocket: WebSocket
    subscription_type: SubscriptionType
    subscription_id: Optional[int] = None
    connected_at: datetime = field(default_factory=datetime.utcnow)
    last_heartbeat: datetime = field(default_factory=datetime.utcnow)
    message_count: int = 0

    @property
    def channels(self) -> list[str]:
        """Get Redis channels for this subscription."""
        if self.subscription_type == SubscriptionType.ALL_PRICES:
            return [CHANNEL_ALL_PRICES]
        elif self.subscription_type == SubscriptionType.COLLECTION:
            return [f"{CHANNEL_COLLECTION_PREFIX}{self.subscription_id}"]
        elif self.subscription_type == SubscriptionType.GIFT:
            return [f"{CHANNEL_GIFT_PREFIX}{self.subscription_id}"]
        return []

    def __hash__(self):
        return id(self.websocket)


class ConnectionManager:
    """
    Manages WebSocket connections and message broadcasting.

    Thread-safe connection management with:
    - Connection tracking by subscription type
    - Redis pub/sub integration
    - Heartbeat/ping-pong support
    - Graceful disconnection handling
    """

    def __init__(self):
        self._connections: dict[SubscriptionType, Set[WebSocketConnection]] = {
            SubscriptionType.ALL_PRICES: set(),
            SubscriptionType.COLLECTION: set(),
            SubscriptionType.GIFT: set(),
        }
        self._lock = asyncio.Lock()
        self._pubsub: Optional[RedisPubSub] = None
        self._heartbeat_task: Optional[asyncio.Task] = None
        self._running = False

    @property
    def total_connections(self) -> int:
        """Get total number of active connections."""
        return sum(len(conns) for conns in self._connections.values())

    async def start(self) -> None:
        """Start the connection manager and background tasks."""
        if self._running:
            return

        self._running = True
        self._pubsub = await RedisPubSub.get_instance()
        self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())
        logger.info("WebSocket ConnectionManager started")

    async def stop(self) -> None:
        """Stop the connection manager and close all connections."""
        self._running = False

        if self._heartbeat_task:
            self._heartbeat_task.cancel()
            try:
                await self._heartbeat_task
            except asyncio.CancelledError:
                pass

        # Close all connections
        async with self._lock:
            for connections in self._connections.values():
                for conn in list(connections):
                    await self._close_connection(conn, code=1001, reason="Server shutdown")

        logger.info("WebSocket ConnectionManager stopped")

    async def connect(
        self,
        websocket: WebSocket,
        subscription_type: SubscriptionType,
        subscription_id: Optional[int] = None,
    ) -> WebSocketConnection:
        """
        Accept a new WebSocket connection and set up subscriptions.

        Args:
            websocket: The WebSocket connection
            subscription_type: Type of subscription
            subscription_id: Collection or gift ID (if applicable)

        Returns:
            WebSocketConnection instance
        """
        await websocket.accept()

        connection = WebSocketConnection(
            websocket=websocket,
            subscription_type=subscription_type,
            subscription_id=subscription_id,
        )

        async with self._lock:
            self._connections[subscription_type].add(connection)

        # Subscribe to Redis channels
        if self._pubsub:
            await self._pubsub.subscribe(
                connection.channels,
                lambda channel, message: self._on_redis_message(connection, channel, message),
            )

        logger.info(
            f"WebSocket connected: {subscription_type.value}"
            f"{f'/{subscription_id}' if subscription_id else ''} "
            f"(total: {self.total_connections})"
        )

        # Send welcome message
        await self._send_json(connection, {
            "type": "connected",
            "subscription": {
                "type": subscription_type.value,
                "id": subscription_id,
            },
            "timestamp": datetime.utcnow().isoformat() + "Z",
        })

        return connection

    async def disconnect(self, connection: WebSocketConnection) -> None:
        """
        Handle disconnection of a WebSocket.

        Args:
            connection: The connection to disconnect
        """
        async with self._lock:
            self._connections[connection.subscription_type].discard(connection)

        # Unsubscribe from Redis channels
        if self._pubsub:
            await self._pubsub.unsubscribe(
                connection.channels,
                lambda channel, message: self._on_redis_message(connection, channel, message),
            )

        logger.info(
            f"WebSocket disconnected: {connection.subscription_type.value}"
            f"{f'/{connection.subscription_id}' if connection.subscription_id else ''} "
            f"(total: {self.total_connections})"
        )

    async def broadcast_to_type(
        self,
        subscription_type: SubscriptionType,
        message: dict,
        subscription_id: Optional[int] = None,
    ) -> int:
        """
        Broadcast a message to all connections of a given type.

        Args:
            subscription_type: Type of subscriptions to broadcast to
            message: Message to send
            subscription_id: Optional ID filter for collection/gift types

        Returns:
            Number of connections that received the message
        """
        sent_count = 0
        async with self._lock:
            connections = list(self._connections[subscription_type])

        for connection in connections:
            # Filter by subscription_id if specified
            if subscription_id is not None and connection.subscription_id != subscription_id:
                continue

            try:
                await self._send_json(connection, message)
                sent_count += 1
            except Exception as e:
                logger.warning(f"Failed to send to connection: {e}")

        return sent_count

    async def _send_json(self, connection: WebSocketConnection, data: dict) -> None:
        """Send JSON data to a connection."""
        if connection.websocket.client_state != WebSocketState.CONNECTED:
            return

        try:
            await connection.websocket.send_json(data)
            connection.message_count += 1
        except Exception as e:
            logger.debug(f"Error sending to WebSocket: {e}")
            raise

    async def _close_connection(
        self,
        connection: WebSocketConnection,
        code: int = 1000,
        reason: str = "Normal closure",
    ) -> None:
        """Close a WebSocket connection gracefully."""
        try:
            if connection.websocket.client_state == WebSocketState.CONNECTED:
                await connection.websocket.close(code=code, reason=reason)
        except Exception as e:
            logger.debug(f"Error closing WebSocket: {e}")

    def _on_redis_message(
        self,
        connection: WebSocketConnection,
        channel: str,
        message: dict,
    ) -> None:
        """
        Handle incoming Redis pub/sub message.

        Schedules async send in the event loop.
        """
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.create_task(self._forward_message(connection, message))
        except Exception as e:
            logger.error(f"Error handling Redis message: {e}")

    async def _forward_message(
        self,
        connection: WebSocketConnection,
        message: dict,
    ) -> None:
        """Forward a message from Redis to the WebSocket client."""
        try:
            await self._send_json(connection, message)
        except Exception as e:
            logger.debug(f"Error forwarding message: {e}")
            await self.disconnect(connection)

    async def _heartbeat_loop(self) -> None:
        """
        Background task that sends periodic heartbeats.

        Also cleans up stale connections.
        """
        HEARTBEAT_INTERVAL = 30  # seconds
        STALE_THRESHOLD = 120  # seconds

        while self._running:
            try:
                await asyncio.sleep(HEARTBEAT_INTERVAL)

                heartbeat_message = {
                    "type": MessageType.HEARTBEAT.value,
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "connections": self.total_connections,
                }

                stale_connections = []
                now = datetime.utcnow()

                async with self._lock:
                    all_connections = [
                        conn
                        for connections in self._connections.values()
                        for conn in connections
                    ]

                for connection in all_connections:
                    try:
                        # Check if connection is stale
                        time_since_heartbeat = (now - connection.last_heartbeat).total_seconds()
                        if time_since_heartbeat > STALE_THRESHOLD:
                            stale_connections.append(connection)
                            continue

                        # Send heartbeat
                        await self._send_json(connection, heartbeat_message)
                        connection.last_heartbeat = now

                    except Exception as e:
                        logger.debug(f"Heartbeat failed for connection: {e}")
                        stale_connections.append(connection)

                # Clean up stale connections
                for connection in stale_connections:
                    await self.disconnect(connection)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in heartbeat loop: {e}")
                await asyncio.sleep(5)

    def get_stats(self) -> dict:
        """Get connection statistics."""
        return {
            "total_connections": self.total_connections,
            "by_type": {
                sub_type.value: len(conns)
                for sub_type, conns in self._connections.items()
            },
        }


# Global connection manager instance
manager = ConnectionManager()


async def get_manager() -> ConnectionManager:
    """Get the global connection manager, ensuring it's started."""
    if not manager._running:
        await manager.start()
    return manager


# WebSocket endpoints

@router.websocket("/ws/prices")
async def websocket_all_prices(websocket: WebSocket):
    """
    WebSocket endpoint for all price updates.

    Receives updates for all listings across all collections and markets.

    Message format:
    ```json
    {
      "type": "price_update" | "new_listing" | "listing_removed",
      "data": {
        "gift_id": 123,
        "collection_id": 1,
        "price_ton": "10.5",
        "market_slug": "getgems",
        ...
      },
      "timestamp": "2024-01-01T00:00:00Z"
    }
    ```
    """
    connection = await manager.connect(
        websocket=websocket,
        subscription_type=SubscriptionType.ALL_PRICES,
    )

    try:
        while True:
            # Wait for client messages (ping/pong or commands)
            try:
                data = await asyncio.wait_for(
                    websocket.receive_text(),
                    timeout=60.0,
                )
                await _handle_client_message(connection, data)
            except asyncio.TimeoutError:
                # No message received, continue (heartbeat handles keep-alive)
                continue

    except WebSocketDisconnect:
        await manager.disconnect(connection)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await manager.disconnect(connection)


@router.websocket("/ws/collection/{collection_id}")
async def websocket_collection(
    websocket: WebSocket,
    collection_id: int,
):
    """
    WebSocket endpoint for collection-specific price updates.

    Args:
        collection_id: The collection ID to subscribe to

    Receives updates only for listings in the specified collection.
    """
    connection = await manager.connect(
        websocket=websocket,
        subscription_type=SubscriptionType.COLLECTION,
        subscription_id=collection_id,
    )

    try:
        while True:
            try:
                data = await asyncio.wait_for(
                    websocket.receive_text(),
                    timeout=60.0,
                )
                await _handle_client_message(connection, data)
            except asyncio.TimeoutError:
                continue

    except WebSocketDisconnect:
        await manager.disconnect(connection)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await manager.disconnect(connection)


@router.websocket("/ws/gift/{gift_id}")
async def websocket_gift(
    websocket: WebSocket,
    gift_id: int,
):
    """
    WebSocket endpoint for single gift price updates.

    Args:
        gift_id: The gift/NFT ID to subscribe to

    Receives updates only for the specified gift's listings.
    """
    connection = await manager.connect(
        websocket=websocket,
        subscription_type=SubscriptionType.GIFT,
        subscription_id=gift_id,
    )

    try:
        while True:
            try:
                data = await asyncio.wait_for(
                    websocket.receive_text(),
                    timeout=60.0,
                )
                await _handle_client_message(connection, data)
            except asyncio.TimeoutError:
                continue

    except WebSocketDisconnect:
        await manager.disconnect(connection)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await manager.disconnect(connection)


async def _handle_client_message(
    connection: WebSocketConnection,
    raw_data: str,
) -> None:
    """
    Handle incoming messages from WebSocket clients.

    Supports:
    - ping: Responds with pong
    - subscribe: (future) Dynamic subscription changes
    """
    try:
        data = json.loads(raw_data)
    except json.JSONDecodeError:
        # Treat as ping if not valid JSON
        data = {"type": raw_data.strip()}

    message_type = data.get("type", "").lower()

    if message_type == "ping":
        await connection.websocket.send_json({
            "type": "pong",
            "timestamp": datetime.utcnow().isoformat() + "Z",
        })
        connection.last_heartbeat = datetime.utcnow()

    elif message_type == "pong":
        # Client responded to our ping
        connection.last_heartbeat = datetime.utcnow()

    elif message_type == "stats":
        # Return connection stats
        await connection.websocket.send_json({
            "type": "stats",
            "data": {
                "connected_at": connection.connected_at.isoformat() + "Z",
                "messages_received": connection.message_count,
                "subscription_type": connection.subscription_type.value,
                "subscription_id": connection.subscription_id,
            },
            "timestamp": datetime.utcnow().isoformat() + "Z",
        })

    else:
        # Unknown message type
        await connection.websocket.send_json({
            "type": "error",
            "message": f"Unknown message type: {message_type}",
            "timestamp": datetime.utcnow().isoformat() + "Z",
        })


# HTTP endpoints for WebSocket status

@router.get("/ws/status")
async def websocket_status():
    """
    Get WebSocket connection statistics.

    Returns current connection counts by subscription type.
    """
    mgr = await get_manager()
    return {
        "status": "running" if mgr._running else "stopped",
        **mgr.get_stats(),
    }


# Lifecycle hooks for FastAPI

async def startup_websocket_manager() -> None:
    """Start the WebSocket manager on application startup."""
    await manager.start()
    logger.info("WebSocket manager started")


async def shutdown_websocket_manager() -> None:
    """Stop the WebSocket manager on application shutdown."""
    await manager.stop()
    logger.info("WebSocket manager stopped")

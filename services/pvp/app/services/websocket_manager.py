"""
WebSocket manager — реалтайм обновления для PvP комнат.
"""
import asyncio
import logging
from typing import Dict, Set

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class WebSocketManager:
    """Manage WebSocket connections grouped by room_code."""

    def __init__(self):
        self.rooms: Dict[str, Set[WebSocket]] = {}
        self._lock = asyncio.Lock()

    async def connect(self, room_code: str, ws: WebSocket) -> None:
        await ws.accept()
        async with self._lock:
            if room_code not in self.rooms:
                self.rooms[room_code] = set()
            self.rooms[room_code].add(ws)
        logger.debug(f"WS connected to room {room_code}, total: {len(self.rooms.get(room_code, set()))}")

    async def disconnect(self, room_code: str, ws: WebSocket) -> None:
        async with self._lock:
            if room_code in self.rooms:
                self.rooms[room_code].discard(ws)
                if not self.rooms[room_code]:
                    del self.rooms[room_code]

    async def broadcast(self, room_code: str, message: dict) -> None:
        """Send message to all connections in room."""
        connections = self.rooms.get(room_code, set()).copy()
        if not connections:
            return

        dead = set()
        for ws in connections:
            try:
                await ws.send_json(message)
            except Exception:
                dead.add(ws)

        if dead:
            async with self._lock:
                if room_code in self.rooms:
                    self.rooms[room_code] -= dead
                    if not self.rooms[room_code]:
                        del self.rooms[room_code]

    def get_room_count(self, room_code: str) -> int:
        return len(self.rooms.get(room_code, set()))

    def get_total_connections(self) -> int:
        return sum(len(v) for v in self.rooms.values())


# Global singleton
ws_manager = WebSocketManager()

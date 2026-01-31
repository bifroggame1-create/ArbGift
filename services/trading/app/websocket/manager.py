from fastapi import WebSocket
from typing import List, Dict
import json
import asyncio
from datetime import datetime


class ConnectionManager:
    """Manage WebSocket connections for real-time trading game updates"""

    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.user_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, user_id: str = None):
        """Accept new WebSocket connection"""
        await websocket.accept()
        self.active_connections.append(websocket)
        if user_id:
            self.user_connections[user_id] = websocket

    def disconnect(self, websocket: WebSocket, user_id: str = None):
        """Remove WebSocket connection"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        if user_id and user_id in self.user_connections:
            del self.user_connections[user_id]

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send message to specific WebSocket"""
        await websocket.send_text(json.dumps(message))

    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients"""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message))
            except Exception as e:
                print(f"Error sending message: {e}")
                disconnected.append(connection)

        # Clean up disconnected clients
        for conn in disconnected:
            self.disconnect(conn)

    async def broadcast_game_state(self, game_number: int, status: str, multiplier: float, timestamp: str = None):
        """Broadcast current game state to all clients"""
        await self.broadcast({
            "type": "game_update",
            "game_number": game_number,
            "status": status,
            "multiplier": multiplier,
            "timestamp": timestamp or datetime.utcnow().isoformat()
        })

    async def broadcast_crash(self, game_number: int, crash_point: float, server_seed: str):
        """Broadcast game crash event"""
        await self.broadcast({
            "type": "game_crashed",
            "game_number": game_number,
            "crash_point": crash_point,
            "server_seed": server_seed,
            "timestamp": datetime.utcnow().isoformat()
        })

    async def broadcast_new_bet(self, user_id: str, bet_amount: float, game_number: int):
        """Broadcast new bet placed"""
        await self.broadcast({
            "type": "new_bet",
            "user_id": user_id,
            "bet_amount": bet_amount,
            "game_number": game_number,
            "timestamp": datetime.utcnow().isoformat()
        })

    async def broadcast_cash_out(self, user_id: str, multiplier: float, profit: float):
        """Broadcast cash out event"""
        await self.broadcast({
            "type": "cash_out",
            "user_id": user_id,
            "multiplier": multiplier,
            "profit": profit,
            "timestamp": datetime.utcnow().isoformat()
        })


# Global connection manager instance
manager = ConnectionManager()

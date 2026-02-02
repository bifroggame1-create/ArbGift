"""
WebSocket endpoint для реалтайм обновлений PvP.
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.services.websocket_manager import ws_manager

router = APIRouter(tags=["WebSocket"])


@router.websocket("/ws/pvp/{room_code}")
async def websocket_room(websocket: WebSocket, room_code: str):
    """
    WebSocket для получения обновлений комнаты.

    Events:
    - bet_placed — новая ставка
    - countdown_start — начало обратного отсчёта
    - countdown_update — обновление таймера
    - spin_start — рулетка крутится
    - spin_result — победитель определён
    - room_cancelled — комната отменена
    """
    await ws_manager.connect(room_code, websocket)

    try:
        while True:
            # Keep alive — клиент может слать ping
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_json({"type": "pong"})
    except WebSocketDisconnect:
        await ws_manager.disconnect(room_code, websocket)

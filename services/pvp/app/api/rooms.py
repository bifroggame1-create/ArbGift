"""
PvP Rooms API.

Endpoints по образцу Rolls.codes.
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional, List
import secrets

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field

from app.services import PvPGameEngine

router = APIRouter(prefix="/api/pvp", tags=["PvP"])

# Глобальный движок (в проде будет DI)
engine = PvPGameEngine()


# =============================================================================
# Pydantic Schemas
# =============================================================================

class CreateRoomRequest(BaseModel):
    """Запрос на создание комнаты."""
    room_type: str = "classic"  # classic, lucky, mono
    min_bet_ton: Decimal = Field(default=Decimal("1"), ge=0)
    max_bet_ton: Optional[Decimal] = None
    max_players: int = Field(default=10, ge=2, le=50)


class CreateRoomResponse(BaseModel):
    """Ответ создания комнаты."""
    room_code: str
    server_seed_hash: str
    status: str
    min_bet_ton: Decimal
    max_bet_ton: Optional[Decimal]
    max_players: int
    countdown_seconds: int


class PlaceBetRequest(BaseModel):
    """Запрос на ставку."""
    room_code: str
    user_id: int
    user_telegram_id: int
    user_name: str
    user_avatar: Optional[str] = None
    gift_address: str
    gift_name: str
    gift_image_url: Optional[str] = None
    gift_value_ton: Decimal


class BetInfo(BaseModel):
    """Информация о ставке."""
    bet_id: int
    user_id: int
    user_name: str
    user_avatar: Optional[str]
    gift_name: str
    gift_image_url: Optional[str]
    gift_value_ton: Decimal
    tickets_count: int
    win_chance_percent: Decimal


class RoomState(BaseModel):
    """Текущее состояние комнаты."""
    room_code: str
    status: str
    total_pool_ton: Decimal
    total_bets: int
    total_players: int
    bets: List[BetInfo]
    server_seed_hash: str
    countdown_seconds: Optional[int] = None


class SpinResultResponse(BaseModel):
    """Результат спина."""
    room_code: str
    winner_user_id: int
    winner_user_name: str
    winning_ticket: int
    total_tickets: int
    spin_degree: Decimal
    winnings_ton: Decimal
    house_fee_ton: Decimal
    server_seed: str  # Раскрываем для верификации


# =============================================================================
# In-memory storage (в проде будет PostgreSQL)
# =============================================================================

rooms_db: dict = {}
bets_db: dict = {}
bet_id_counter = 0


# =============================================================================
# API Endpoints
# =============================================================================

@router.post("/rooms", response_model=CreateRoomResponse)
async def create_room(req: CreateRoomRequest):
    """
    Создать новую PvP комнату.

    Генерирует server_seed и возвращает его хеш.
    """
    room_code = secrets.token_urlsafe(8)[:8].upper()

    room_params = engine.create_room(
        room_code=room_code,
        min_bet_ton=req.min_bet_ton,
        max_bet_ton=req.max_bet_ton,
        max_players=req.max_players,
    )

    rooms_db[room_code] = {
        **room_params,
        "bets": [],
        "total_pool_ton": Decimal("0"),
        "total_bets": 0,
        "total_players": 0,
        "created_at": datetime.utcnow(),
    }

    return CreateRoomResponse(
        room_code=room_code,
        server_seed_hash=room_params["server_seed_hash"],
        status="waiting",
        min_bet_ton=req.min_bet_ton,
        max_bet_ton=req.max_bet_ton,
        max_players=req.max_players,
        countdown_seconds=30,
    )


@router.post("/rooms/{room_code}/bet")
async def place_bet(room_code: str, req: PlaceBetRequest):
    """
    Поставить гифт в комнату.

    Проверяет:
    - Комната существует и в статусе waiting/countdown
    - Ставка в пределах min/max
    - Игрок не превысил лимит
    """
    global bet_id_counter

    room = rooms_db.get(room_code)
    if not room:
        raise HTTPException(404, "Room not found")

    if room["status"] not in ("waiting", "countdown"):
        raise HTTPException(400, "Room is not accepting bets")

    if req.gift_value_ton < room["min_bet_ton"]:
        raise HTTPException(400, f"Minimum bet is {room['min_bet_ton']} TON")

    if room["max_bet_ton"] and req.gift_value_ton > room["max_bet_ton"]:
        raise HTTPException(400, f"Maximum bet is {room['max_bet_ton']} TON")

    bet_id_counter += 1
    bet = {
        "id": bet_id_counter,
        "room_code": room_code,
        "user_id": req.user_id,
        "user_telegram_id": req.user_telegram_id,
        "user_name": req.user_name,
        "user_avatar": req.user_avatar,
        "gift_address": req.gift_address,
        "gift_name": req.gift_name,
        "gift_image_url": req.gift_image_url,
        "gift_value_ton": req.gift_value_ton,
        "tickets_start": 0,
        "tickets_end": 0,
        "tickets_count": 0,
        "win_chance_percent": Decimal("0"),
        "is_winner": False,
        "placed_at": datetime.utcnow(),
    }

    room["bets"].append(bet)
    room["total_pool_ton"] += req.gift_value_ton
    room["total_bets"] += 1

    # Подсчёт уникальных игроков
    unique_users = set(b["user_id"] for b in room["bets"])
    room["total_players"] = len(unique_users)

    # Если достигли 2+ игроков — начинаем countdown
    if room["total_players"] >= 2 and room["status"] == "waiting":
        room["status"] = "countdown"
        room["countdown_started_at"] = datetime.utcnow()

    return {
        "bet_id": bet["id"],
        "room_code": room_code,
        "status": room["status"],
        "total_pool_ton": str(room["total_pool_ton"]),
        "total_bets": room["total_bets"],
    }


@router.get("/rooms/{room_code}", response_model=RoomState)
async def get_room(room_code: str):
    """Получить состояние комнаты."""
    room = rooms_db.get(room_code)
    if not room:
        raise HTTPException(404, "Room not found")

    # Рассчитываем тикеты и шансы
    bets_info = []
    total_tickets = 0

    for bet in room["bets"]:
        tickets = engine.calculate_tickets(bet["gift_value_ton"])
        bet["tickets_count"] = tickets
        total_tickets += tickets

    for bet in room["bets"]:
        if total_tickets > 0:
            chance = (Decimal(bet["tickets_count"]) / Decimal(total_tickets)) * 100
        else:
            chance = Decimal("0")

        bets_info.append(BetInfo(
            bet_id=bet["id"],
            user_id=bet["user_id"],
            user_name=bet["user_name"],
            user_avatar=bet["user_avatar"],
            gift_name=bet["gift_name"],
            gift_image_url=bet["gift_image_url"],
            gift_value_ton=bet["gift_value_ton"],
            tickets_count=bet["tickets_count"],
            win_chance_percent=round(chance, 2),
        ))

    return RoomState(
        room_code=room_code,
        status=room["status"],
        total_pool_ton=room["total_pool_ton"],
        total_bets=room["total_bets"],
        total_players=room["total_players"],
        bets=bets_info,
        server_seed_hash=room["server_seed_hash"],
    )


@router.post("/rooms/{room_code}/spin", response_model=SpinResultResponse)
async def spin_wheel(room_code: str, client_seed: Optional[str] = None):
    """
    Крутить рулетку и определить победителя.

    Требует минимум 2 игроков.
    После спина раскрывается server_seed для верификации.
    """
    room = rooms_db.get(room_code)
    if not room:
        raise HTTPException(404, "Room not found")

    if room["status"] == "finished":
        raise HTTPException(400, "Room already finished")

    if room["total_players"] < 2:
        raise HTTPException(400, "Need at least 2 players")

    room["status"] = "spinning"

    # Конвертируем dict в объекты для движка
    class BetObj:
        def __init__(self, d):
            for k, v in d.items():
                setattr(self, k, v)

    bet_objs = [BetObj(b) for b in room["bets"]]

    class RoomObj:
        server_seed = room["server_seed"]
        nonce = 0

    # Спиним
    result = engine.spin_wheel(RoomObj(), bet_objs, client_seed)

    # Находим победителя
    winner_bet = None
    for bet in room["bets"]:
        if bet["id"] == result.winning_bet_id:
            bet["is_winner"] = True
            winner_bet = bet
            break

    # Рассчитываем выигрыш
    winnings, fee = engine.calculate_winnings(
        room["total_pool_ton"],
        Decimal("5"),  # 5% комиссия
    )

    room["status"] = "finished"
    room["winner_user_id"] = result.winner_user_id
    room["finished_at"] = datetime.utcnow()

    return SpinResultResponse(
        room_code=room_code,
        winner_user_id=result.winner_user_id,
        winner_user_name=winner_bet["user_name"] if winner_bet else "Unknown",
        winning_ticket=result.winning_ticket,
        total_tickets=sum(b["tickets_count"] for b in room["bets"]),
        spin_degree=result.spin_degree,
        winnings_ton=winnings,
        house_fee_ton=fee,
        server_seed=room["server_seed"],  # Раскрываем для проверки!
    )


@router.get("/rooms")
async def list_rooms(status: Optional[str] = None, limit: int = 20):
    """Список комнат."""
    rooms = list(rooms_db.values())

    if status:
        rooms = [r for r in rooms if r["status"] == status]

    rooms = sorted(rooms, key=lambda x: x["created_at"], reverse=True)[:limit]

    return {
        "total": len(rooms),
        "rooms": [
            {
                "room_code": r["room_code"],
                "status": r["status"],
                "total_pool_ton": str(r["total_pool_ton"]),
                "total_players": r["total_players"],
                "server_seed_hash": r["server_seed_hash"],
            }
            for r in rooms
        ],
    }


@router.post("/rooms/{room_code}/verify")
async def verify_result(
    room_code: str,
    server_seed: str,
    client_seed: str,
    nonce: int = 0,
):
    """
    Проверить честность результата.

    Клиент может независимо проверить что результат был честным.
    """
    from app.services import ProvablyFairEngine

    room = rooms_db.get(room_code)
    if not room:
        raise HTTPException(404, "Room not found")

    if room["status"] != "finished":
        raise HTTPException(400, "Room not finished yet")

    # Проверяем что server_seed соответствует хешу
    actual_hash = ProvablyFairEngine.hash_server_seed(server_seed)
    if actual_hash != room["server_seed_hash"]:
        return {"valid": False, "reason": "Server seed does not match hash"}

    # Вычисляем результат
    result = ProvablyFairEngine.generate_result(server_seed, client_seed, nonce)

    return {
        "valid": True,
        "computed_result": result,
        "server_seed_hash": actual_hash,
    }

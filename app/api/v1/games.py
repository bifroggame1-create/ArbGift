"""
Games Orchestration API.

Централизованный endpoint для всех игр с:
- Проверкой Telegram initData
- Управлением балансом
- Проксированием к микросервисам
- Audit logging
"""
import logging
import os
import json
import hashlib
import secrets
import uuid
from urllib.parse import parse_qs
from typing import Optional
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Header
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import httpx

from app.core.database import get_db_session
from app.models.user import User
from app.models.ledger import BalanceOperation, OperationStatus, OperationType
from app.models.game_round import GameRound
from app.config import settings
from app.core.gateway import internal_headers
from app.core.auth import get_verified_telegram_id, verify_telegram_init_data
from app.core.ratelimit import limiter
from app.core.ledger import get_or_create_op, ensure_idempotent, lock_user, hash_payload

logger = logging.getLogger(__name__)
router = APIRouter()

# Microservice URLs
PLINKO_SERVICE_URL = settings.PLINKO_SERVICE_URL
TRADING_SERVICE_URL = settings.TRADING_SERVICE_URL
PVP_SERVICE_URL = settings.PVP_SERVICE_URL
SOLO_GAMES_SERVICE_URL = settings.SOLO_GAMES_SERVICE_URL
PVP_INTERNAL_HEADERS = internal_headers


def _hash_payload(payload: dict) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()


async def _commit_round(session: AsyncSession, game_type: str, round_id: str, server_seed: str, server_seed_hash: str):
    existing = await session.execute(select(GameRound).where(GameRound.round_id == round_id))
    if existing.scalar_one_or_none():
        return
    session.add(GameRound(
        game_type=game_type,
        round_id=round_id,
        server_seed=server_seed,
        server_seed_hash=server_seed_hash,
    ))


async def _get_or_create_operation(
    session: AsyncSession,
    user_id: int,
    operation_id: Optional[str],
    op_type: OperationType,
    request_payload: dict,
) -> Optional[BalanceOperation]:
    if not operation_id:
        return None
    existing = await session.execute(
        select(BalanceOperation).where(BalanceOperation.operation_id == operation_id)
    )
    op = existing.scalar_one_or_none()
    if op:
        return op
    op = BalanceOperation(
        operation_id=operation_id,
        user_id=user_id,
        op_type=op_type,
        status=OperationStatus.PENDING,
        request_hash=_hash_payload(request_payload),
    )
    session.add(op)
    await session.flush()
    return op


async def get_current_user(
    init_data: str = Header(..., alias="X-Telegram-Init-Data"),
    session: AsyncSession = Depends(get_db_session),
) -> User:
    """
    Получить текущего пользователя из Telegram initData.

    ВАЖНО: Проверяет подпись Telegram!
    """
    bot_token = settings.TELEGRAM_BOT_TOKEN or os.getenv("TELEGRAM_BOT_TOKEN")
    if settings.DEBUG and not bot_token:
        try:
            parsed_user = json.loads(parse_qs(init_data).get("user", ["{}"])[0])
            telegram_id = parsed_user.get("id")
        except Exception:
            raise HTTPException(status_code=401, detail="Invalid initData format")
    else:
        if not bot_token:
            logger.error("TELEGRAM_BOT_TOKEN is not configured")
            raise HTTPException(status_code=500, detail="Server auth not configured")
        user_data = verify_telegram_init_data(init_data, bot_token)
        telegram_id = user_data.get("id")

    if not telegram_id:
        raise HTTPException(status_code=401, detail="No user ID in initData")

    # Get user from database
    result = await session.execute(
        select(User).where(User.telegram_id == telegram_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found. Please register first.")

    return user


# ============================================================
# PLINKO GAME
# ============================================================

class PlinkoPlayRequest(BaseModel):
    """Plinko play request."""
    bet_amount_stars: int = Field(..., gt=0, description="Bet amount in Stars")
    risk_level: str = Field("medium", pattern="^(low|medium|high)$")
    row_count: int = Field(12, ge=8, le=16)
    ball_count: int = Field(1, ge=1, le=10)
    client_seed: Optional[str] = None
    round_id: Optional[str] = Field(
        None,
        description="Optional pre-committed round id; if omitted server will create commit"
    )


class PlinkoCommitResponse(BaseModel):
    round_id: str
    server_seed_hash: str


@router.get("/games/plinko/config")
async def get_plinko_config():
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            resp = await client.get(f"{PLINKO_SERVICE_URL}/api/v1/config")
            resp.raise_for_status()
            return resp.json()
        except httpx.HTTPError as e:
            logger.error(f"Plinko config error: {e}")
            raise HTTPException(status_code=503, detail="Game service unavailable")


@router.post("/games/plinko/commit", response_model=PlinkoCommitResponse)
@limiter.limit("30/minute")
async def commit_plinko_round(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    """Pre-commit server seed for a Plinko round and return hash."""
    server_seed = secrets.token_hex(32)
    server_seed_hash = hashlib.sha256(server_seed.encode()).hexdigest()
    round_id = f"plinko-{uuid.uuid4()}"

    await _commit_round(
        session,
        "plinko",
        round_id,
        server_seed,
        server_seed_hash,
    )
    await session.commit()
    return PlinkoCommitResponse(round_id=round_id, server_seed_hash=server_seed_hash)


@router.post("/games/plinko/play")
@limiter.limit("10/minute")
async def play_plinko(
    request: PlinkoPlayRequest,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key"),
):
    """
    Играть в Plinko.

    1. Проверяет баланс
    2. Списывает ставку
    3. Вызывает Plinko service
    4. Начисляет выигрыш
    5. Возвращает результат
    """
    total_cost = request.bet_amount_stars * request.ball_count

    request_payload = {
        "bet_amount_stars": request.bet_amount_stars,
        "risk_level": request.risk_level,
        "row_count": request.row_count,
        "ball_count": request.ball_count,
        "client_seed": request.client_seed,
    }

    # Ensure commit exists or create one
    round_id = request.round_id or f"plinko-{uuid.uuid4()}"
    commit_seed = None
    commit_hash = None
    existing_commit = await session.execute(select(GameRound).where(GameRound.round_id == round_id))
    commit_row = existing_commit.scalar_one_or_none()
    if commit_row:
        commit_seed = commit_row.server_seed
        commit_hash = commit_row.server_seed_hash
    else:
        commit_seed = secrets.token_hex(32)
        commit_hash = hashlib.sha256(commit_seed.encode()).hexdigest()
        await _commit_round(session, "plinko", round_id, commit_seed, commit_hash)

    # Lock user row for balance update
    user = await lock_user(session, user)

    op = await get_or_create_op(
        session, user.id, idempotency_key, OperationType.BET, request_payload
    )
    ensure_idempotent(op, request_payload)

    # Check balance
    if user.balance_stars < total_cost:
        if op:
            op.status = OperationStatus.FAILED
        await session.commit()
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient balance. Need {total_cost} Stars, have {user.balance_stars}"
        )

    # Deduct bet
    user.balance_stars -= total_cost
    user.total_wagered_ton += Decimal(total_cost) * Decimal(settings.STARS_TO_TON_RATE)
    user.games_played += request.ball_count

    # Call Plinko service
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(
                f"{PLINKO_SERVICE_URL}/api/v1/play",
                params={"user_id": str(user.telegram_id)},
                json={
                    "bet_amount_stars": request.bet_amount_stars,
                    "risk_level": request.risk_level,
                    "row_count": request.row_count,
                    "ball_count": request.ball_count,
                    "client_seed": request.client_seed,
                    "server_seed": commit_seed,
                    "round_id": round_id,
                }
            )
            response.raise_for_status()
            result = response.json()
        except httpx.HTTPError as e:
            # Refund on service error
            user.balance_stars += total_cost
            if op:
                op.status = OperationStatus.FAILED
            await session.commit()
            logger.error(f"Plinko service error: {e}")
            raise HTTPException(status_code=503, detail="Game service unavailable")

    # Add winnings
    total_payout = int(result["total_payout"])
    total_profit = int(result["total_profit"])

    user.balance_stars += total_payout

    if total_profit > 0:
        user.total_won_ton += Decimal(total_profit) * Decimal(settings.STARS_TO_TON_RATE)
        user.games_won += sum(1 for d in result["drops"] if d["profit"] > 0)
    else:
        user.total_lost_ton += Decimal(abs(total_profit)) * Decimal(settings.STARS_TO_TON_RATE)

    # Update stats
    biggest_win = max((d["payout"] for d in result["drops"]), default=0)
    if biggest_win > float(user.biggest_win_ton):
        user.biggest_win_ton = Decimal(biggest_win) * Decimal(settings.STARS_TO_TON_RATE)

    # Apply ledger op
    if op:
        op.amount_stars = -total_cost
        op.status = OperationStatus.APPLIED
        result["new_balance_stars"] = user.balance_stars
        op.response_json = result

    await session.commit()
    await session.refresh(user)

    # Return result with updated balance
    result["new_balance_stars"] = user.balance_stars
    result["round_id"] = round_id
    result["server_seed_hash"] = commit_hash
    result.pop("server_seed", None)

    logger.info(
        f"Plinko play: user={user.telegram_id}, "
        f"bet={total_cost}, payout={total_payout}, profit={total_profit}"
    )

    return result


# ============================================================
# SOLO GAMES (Plinko/Gonka/Escape)
# ============================================================

class SoloPlayRequest(BaseModel):
    amount: Decimal
    client_seed: Optional[str] = ""
    nonce: int = 0
    mode: Optional[str] = None  # used by gonka
    round_id: Optional[str] = None


@router.post("/games/solo/plinko/play")
@limiter.limit("10/minute")
async def solo_plinko_play(
    request: SoloPlayRequest,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key"),
):
    payload = request.model_dump()
    user = await lock_user(session, user)
    op = await get_or_create_op(session, user.id, idempotency_key, OperationType.BET, payload)
    ensure_idempotent(op, payload)

    if user.balance_ton < request.amount:
        if op:
            op.status = OperationStatus.FAILED
        await session.commit()
        raise HTTPException(status_code=400, detail="Insufficient TON balance")

    user.balance_ton -= request.amount

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            resp = await client.post(
                f"{SOLO_GAMES_SERVICE_URL}/api/solo-plinko-game/buy/ton",
                headers=internal_headers(),
                json={
                    "amount": float(request.amount),
                    "client_seed": request.client_seed or "",
                    "nonce": request.nonce,
                    "user_id": str(user.id),
                },
            )
            resp.raise_for_status()
            result = resp.json()
            await _commit_round(session, "solo_plinko", result.get("round_id", f"solo-plinko-{user.id}-{request.nonce}"), result.get("server_seed", ""), result.get("server_seed_hash", ""))
        except httpx.HTTPError as e:
            user.balance_ton += request.amount
            if op:
                op.status = OperationStatus.FAILED
            await session.commit()
            raise HTTPException(status_code=503, detail="Solo service unavailable") from e

    payout = Decimal(str(result.get("payout", 0)))
    user.balance_ton += payout

    if op:
        op.status = OperationStatus.APPLIED
        op.amount_ton = request.amount * -1 + payout
        op.response_json = result

    await session.commit()
    return result


@router.post("/games/solo/gonka/play")
@limiter.limit("10/minute")
async def solo_gonka_play(
    request: SoloPlayRequest,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key"),
):
    payload = request.model_dump()
    user = await lock_user(session, user)
    op = await get_or_create_op(session, user.id, idempotency_key, OperationType.BET, payload)
    ensure_idempotent(op, payload)

    if user.balance_ton < request.amount:
        if op:
            op.status = OperationStatus.FAILED
        await session.commit()
        raise HTTPException(status_code=400, detail="Insufficient TON balance")

    user.balance_ton -= request.amount

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            resp = await client.post(
                f"{SOLO_GAMES_SERVICE_URL}/api/solo-race-game/buy/ton",
                headers=internal_headers(),
                json={
                    "amount": float(request.amount),
                    "mode": request.mode or "lite",
                    "client_seed": request.client_seed or "",
                    "nonce": request.nonce,
                    "user_id": str(user.id),
                },
            )
            resp.raise_for_status()
            result = resp.json()
            await _commit_round(session, "solo_gonka", result.get("round_id", f"solo-gonka-{user.id}-{request.nonce}"), result.get("server_seed", ""), result.get("server_seed_hash", ""))
        except httpx.HTTPError as e:
            user.balance_ton += request.amount
            if op:
                op.status = OperationStatus.FAILED
            await session.commit()
            raise HTTPException(status_code=503, detail="Solo service unavailable") from e

    payout = Decimal(str(result.get("payout", 0)))
    user.balance_ton += payout

    if op:
        op.status = OperationStatus.APPLIED
        op.amount_ton = request.amount * -1 + payout
        op.response_json = result

    await session.commit()
    return result


@router.post("/games/solo/escape/play")
@limiter.limit("10/minute")
async def solo_escape_play(
    request: SoloPlayRequest,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key"),
):
    payload = request.model_dump()
    user = await lock_user(session, user)
    op = await get_or_create_op(session, user.id, idempotency_key, OperationType.BET, payload)
    ensure_idempotent(op, payload)

    if user.balance_ton < request.amount:
        if op:
            op.status = OperationStatus.FAILED
        await session.commit()
        raise HTTPException(status_code=400, detail="Insufficient TON balance")

    user.balance_ton -= request.amount

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            resp = await client.post(
                f"{SOLO_GAMES_SERVICE_URL}/api/solo-escape-game/buy/ton",
                headers=internal_headers(),
                json={
                    "amount": float(request.amount),
                    "client_seed": request.client_seed or "",
                    "nonce": request.nonce,
                    "user_id": str(user.id),
                },
            )
            resp.raise_for_status()
            result = resp.json()
            await _commit_round(session, "solo_escape", result.get("round_id", f"solo-escape-{user.id}-{request.nonce}"), result.get("server_seed", ""), result.get("server_seed_hash", ""))
        except httpx.HTTPError as e:
            user.balance_ton += request.amount
            if op:
                op.status = OperationStatus.FAILED
            await session.commit()
            raise HTTPException(status_code=503, detail="Solo service unavailable") from e

    payout = Decimal(str(result.get("payout", 0)))
    user.balance_ton += payout

    if op:
        op.status = OperationStatus.APPLIED
        op.amount_ton = request.amount * -1 + payout
        op.response_json = result

    await session.commit()
    return result


# ============================================================
# TRADING GAME (Crash)
# ============================================================

class TradingBuyRequest(BaseModel):
    """Trading game buy request."""
    bet_amount: Decimal = Field(..., gt=0)
    currency: str = Field("stars", pattern="^(ton|stars)$")


class TradingSellRequest(BaseModel):
    """Trading game sell request."""
    game_id: str


@router.post("/games/trading/buy")
@limiter.limit("10/minute")
async def trading_buy(
    request: TradingBuyRequest,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key"),
):
    """
    Купить в Trading game (войти в раунд).

    ВАЖНО: Игра должна быть на сервере, не на клиенте!
    """
    request_payload = {
        "bet_amount": str(request.bet_amount),
        "currency": request.currency,
    }

    # Lock user row
    result = await session.execute(
        select(User).where(User.id == user.id).with_for_update()
    )
    user = result.scalar_one()

    op = await _get_or_create_operation(
        session, user.id, idempotency_key, OperationType.BET, request_payload
    )
    if op and op.status == OperationStatus.APPLIED and op.response_json:
        return op.response_json
    if op and op.status == OperationStatus.PENDING and op.response_json is None and op.request_hash != _hash_payload(request_payload):
        raise HTTPException(status_code=409, detail="Idempotency key reused with different payload")

    # Check balance and deduct
    if request.currency == "stars":
        bet_stars = int(request.bet_amount)
        if user.balance_stars < bet_stars:
            if op:
                op.status = OperationStatus.FAILED
            await session.commit()
            raise HTTPException(status_code=400, detail="Insufficient Stars balance")
        user.balance_stars -= bet_stars
    else:
        if user.balance_ton < request.bet_amount:
            if op:
                op.status = OperationStatus.FAILED
            await session.commit()
            raise HTTPException(status_code=400, detail="Insufficient TON balance")
        user.balance_ton -= request.bet_amount

    # Get current game and place bet in trading service
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            game_resp = await client.get(f"{TRADING_SERVICE_URL}/api/trading/game/current")
            game_resp.raise_for_status()
            game = game_resp.json()
            bet_resp = await client.post(
                f"{TRADING_SERVICE_URL}/api/trading/bet",
                headers=internal_headers(),
                json={
                    "game_number": game["game_number"],
                    "user_id": user.id,
                    "user_telegram_id": user.telegram_id,
                    "user_name": user.display_name,
                    "bet_amount_ton": str(request.bet_amount if request.currency == "ton" else Decimal(request.bet_amount) * Decimal(settings.STARS_TO_TON_RATE)),
                },
            )
            bet_resp.raise_for_status()
            bet = bet_resp.json()
        except httpx.HTTPError as e:
            # Refund on service error
            if request.currency == "stars":
                user.balance_stars += int(request.bet_amount)
            else:
                user.balance_ton += request.bet_amount
            if op:
                op.status = OperationStatus.FAILED
            await session.commit()
            raise HTTPException(status_code=503, detail="Trading service unavailable") from e

    response = {
        "game_id": game["id"],
        "status": game["status"],
        "entry_multiplier": game["current_multiplier"],
        "bet_id": bet["id"],
        "new_balance_stars": user.balance_stars,
        "new_balance_ton": float(user.balance_ton),
    }

    if op:
        op.status = OperationStatus.APPLIED
        op.response_json = response
        op.amount_ton = request.bet_amount if request.currency == "ton" else Decimal("0")
        op.amount_stars = int(request.bet_amount) if request.currency == "stars" else 0

    await session.commit()
    return response


# ============================================================
# PVP
# ============================================================

class PvpCreateRoomRequest(BaseModel):
    room_type: str = "classic"
    min_bet_ton: Decimal = Field(default=Decimal("1"), ge=0)
    max_bet_ton: Optional[Decimal] = None
    max_players: int = Field(default=10, ge=2, le=50)


@router.post("/games/pvp/rooms")
async def pvp_create_room(
    req: PvpCreateRoomRequest,
):
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(
            f"{PVP_SERVICE_URL}/api/pvp/rooms",
            headers=internal_headers(),
            json=req.model_dump(),
        )
        resp.raise_for_status()
        return resp.json()


@router.get("/games/pvp/rooms/{room_code}")
async def pvp_get_room(room_code: str):
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.get(
            f"{PVP_SERVICE_URL}/api/pvp/rooms/{room_code}",
            headers=internal_headers(),
        )
        resp.raise_for_status()
        return resp.json()


@router.get("/games/pvp/inventory")
async def pvp_inventory(wallet_address: str):
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.get(
            f"{PVP_SERVICE_URL}/api/pvp/inventory/user/{wallet_address}",
            headers=internal_headers(),
        )
        resp.raise_for_status()
        return resp.json()


class PvpBetRequest(BaseModel):
    user_id: int
    user_telegram_id: int
    user_name: str
    user_avatar: Optional[str] = None
    gift_address: str
    gift_name: str
    gift_image_url: Optional[str] = None
    gift_value_ton: Decimal


@router.post("/games/pvp/rooms/{room_code}/bet")
@limiter.limit("10/minute")
async def pvp_place_bet(
    room_code: str,
    req: PvpBetRequest,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
    wallet_address: Optional[str] = Header(None, alias="X-Wallet-Address"),
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key"),
):
    # Use current authenticated user, ignore spoofed ids
    req_payload = req.model_dump()
    bet_amount = req.gift_value_ton

    user = await lock_user(session, user)
    op = await get_or_create_op(session, user.id, idempotency_key, OperationType.BET, req_payload)
    ensure_idempotent(op, req_payload)

    if user.balance_ton < bet_amount:
        if op:
            op.status = OperationStatus.FAILED
        await session.commit()
        raise HTTPException(status_code=400, detail="Insufficient TON balance")

    user.balance_ton -= bet_amount

    headers = internal_headers()
    if wallet_address:
        headers["X-Wallet-Address"] = wallet_address

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            resp = await client.post(
                f"{PVP_SERVICE_URL}/api/pvp/rooms/{room_code}/bet",
                headers=headers,
                json={
                    **req_payload,
                    "user_id": user.id,
                    "user_telegram_id": user.telegram_id,
                    "user_name": user.display_name,
                },
            )
            resp.raise_for_status()
            result = resp.json()
        except httpx.HTTPError as e:
            user.balance_ton += bet_amount
            if op:
                op.status = OperationStatus.FAILED
            await session.commit()
            raise HTTPException(status_code=503, detail="PvP service unavailable") from e

    if op:
        op.status = OperationStatus.APPLIED
        op.amount_ton = -bet_amount
        op.response_json = result

    await session.commit()
    return result


@router.post("/games/pvp/rooms/{room_code}/spin")
@limiter.limit("10/minute")
async def pvp_spin(
    room_code: str,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key"),
):
    payload = {"room_code": room_code}
    op = await get_or_create_op(session, user.id, idempotency_key, OperationType.PAYOUT, payload)
    ensure_idempotent(op, payload)

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            resp = await client.post(
                f"{PVP_SERVICE_URL}/api/pvp/rooms/{room_code}/spin",
                headers=internal_headers(),
            )
            resp.raise_for_status()
            result = resp.json()
        except httpx.HTTPError as e:
            if op:
                op.status = OperationStatus.FAILED
            await session.commit()
            raise HTTPException(status_code=503, detail="PvP service unavailable") from e

    # Credit winner
    winner_id = result.get("winner_user_id")
    winnings = Decimal(str(result.get("winnings_ton", "0")))
    if winnings > 0:
        winner = await session.execute(select(User).where(User.id == winner_id).with_for_update())
        winner_user = winner.scalar_one_or_none()
        if winner_user:
            winner_user.balance_ton += winnings
            if op:
                op.amount_ton = winnings
                op.status = OperationStatus.APPLIED
                op.response_json = result

    await session.commit()
    return result


@router.get("/games/reveal/{round_id}")
@limiter.limit("60/minute")
async def reveal_round(round_id: str, session: AsyncSession = Depends(get_db_session)):
    """Reveal server seed for a committed round."""
    res = await session.execute(select(GameRound).where(GameRound.round_id == round_id))
    row = res.scalar_one_or_none()
    if not row:
        raise HTTPException(status_code=404, detail="Round not found")
    return {
        "round_id": row.round_id,
        "server_seed_hash": row.server_seed_hash,
        "server_seed": row.server_seed,
    }


@router.post("/games/trading/sell")
@limiter.limit("10/minute")
async def trading_sell(
    request: TradingSellRequest,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key"),
):
    """
    Продать в Trading game (выйти из раунда).
    """
    request_payload = {"game_id": request.game_id}
    op = await get_or_create_op(
        session, user.id, idempotency_key, OperationType.PAYOUT, request_payload
    )
    ensure_idempotent(op, request_payload)

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            cash_resp = await client.post(
                f"{TRADING_SERVICE_URL}/api/trading/cashout",
                headers=internal_headers(),
                params={"user_id": user.id},
                json={"bet_id": request.game_id},
            )
            cash_resp.raise_for_status()
            cash = cash_resp.json()
        except httpx.HTTPError as e:
            if op:
                op.status = OperationStatus.FAILED
            await session.commit()
            raise HTTPException(status_code=503, detail="Trading service unavailable") from e

    # Credit winnings (assume TON payout)
    profit_ton = Decimal(cash.get("profit_ton", "0"))
    user.balance_ton += profit_ton
    response = {
        "game_id": request.game_id,
        "exit_multiplier": cash.get("cash_out_multiplier"),
        "payout": cash.get("profit_ton"),
        "profit": cash.get("profit_ton"),
        "new_balance_stars": user.balance_stars,
        "new_balance_ton": float(user.balance_ton),
    }
    if op:
        op.status = OperationStatus.APPLIED
        op.amount_ton = profit_ton
        op.response_json = response
    await session.commit()
    return response


# ============================================================
# BALANCE ENDPOINTS
# ============================================================

@router.get("/user/balance")
async def get_user_balance(
    user: User = Depends(get_current_user),
):
    """Получить баланс пользователя."""
    return {
        "balance_ton": float(user.balance_ton),
        "balance_stars": user.balance_stars,
    }


@router.post("/user/balance/add")
async def add_balance(
    amount_ton: Optional[Decimal] = None,
    amount_stars: Optional[int] = None,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    """
    Пополнить баланс (для тестирования).

    TODO: В продакшене заменить на реальную оплату.
    """
    if not settings.DEBUG:
        raise HTTPException(status_code=403, detail="Only available in debug mode")

    if amount_ton:
        user.balance_ton += amount_ton
    if amount_stars:
        user.balance_stars += amount_stars

    await session.commit()
    await session.refresh(user)

    return {
        "balance_ton": float(user.balance_ton),
        "balance_stars": user.balance_stars,
    }

"""
Staking API Endpoints.

API для стейкинга NFT гифтов.
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.models.stake import StakePeriod, StakeStatus
from app.services import StakingEngine

router = APIRouter(prefix="/api/staking", tags=["Staking"])

# In-memory storage (в проде PostgreSQL)
stakes_db: dict = {}
user_stats_db: dict = {}


# =============================================================================
# Pydantic Schemas
# =============================================================================

class StakePreviewRequest(BaseModel):
    """Запрос превью стейка."""
    gift_value_ton: Decimal
    period: StakePeriod


class CreateStakeRequest(BaseModel):
    """Запрос на создание стейка."""
    user_id: int
    user_telegram_id: int
    user_name: str
    gift_address: str
    gift_name: str
    gift_image_url: Optional[str] = None
    gift_value_ton: Decimal
    period: StakePeriod


class StakeResponse(BaseModel):
    """Ответ со стейком."""
    id: str
    user_id: int
    gift_address: str
    gift_name: str
    gift_image_url: Optional[str]
    gift_value_ton: str
    period: str
    period_days: int
    apy_percent: str
    expected_reward_ton: str
    status: str
    created_at: str
    unlocks_at: str
    days_remaining: int
    is_unlockable: bool


class UnstakeRequest(BaseModel):
    """Запрос на вывод стейка."""
    force_early: bool = False  # Досрочный вывод со штрафом


class StatsResponse(BaseModel):
    """Статистика стейкинга пользователя."""
    total_stakes: int
    active_stakes: int
    completed_stakes: int
    total_staked_ton: str
    currently_staked_ton: str
    total_rewards_earned_ton: str
    total_penalties_paid_ton: str
    net_profit_ton: str


# =============================================================================
# API Endpoints
# =============================================================================

@router.get("/periods")
async def get_staking_periods():
    """Получить доступные периоды стейкинга."""
    return {
        "periods": StakingEngine.get_available_periods(),
        "min_stake_ton": str(StakingEngine.MIN_STAKE_VALUE_TON),
        "early_withdrawal_penalty_percent": str(StakingEngine.EARLY_WITHDRAWAL_PENALTY),
    }


@router.post("/preview")
async def preview_stake(req: StakePreviewRequest):
    """
    Предпросмотр стейка.

    Показывает расчет награды перед подтверждением.
    """
    preview = StakingEngine.get_stake_preview(req.gift_value_ton, req.period)

    if not preview["valid"]:
        raise HTTPException(400, preview["error"])

    return preview


@router.post("/stake", response_model=StakeResponse)
async def create_stake(req: CreateStakeRequest):
    """
    Создать стейк.

    Блокирует NFT гифт на указанный период.
    """
    # Валидация
    is_valid, error = StakingEngine.validate_stake(req.gift_value_ton, req.period)
    if not is_valid:
        raise HTTPException(400, error)

    # Проверка что гифт не застейкан
    for stake in stakes_db.values():
        if stake["gift_address"] == req.gift_address and stake["status"] == "active":
            raise HTTPException(400, "Gift is already staked")

    # Создаем стейк
    stake_id = str(uuid4())
    now = datetime.utcnow()
    unlock_date = StakingEngine.get_unlock_date(req.period, now)
    expected_reward = StakingEngine.calculate_reward(req.gift_value_ton, req.period)
    apy = StakingEngine.get_apy(req.period)
    period_days = StakingEngine.PERIOD_DAYS[req.period]

    stake = {
        "id": stake_id,
        "user_id": req.user_id,
        "user_telegram_id": req.user_telegram_id,
        "user_name": req.user_name,
        "gift_address": req.gift_address,
        "gift_name": req.gift_name,
        "gift_image_url": req.gift_image_url,
        "gift_value_ton": req.gift_value_ton,
        "period": req.period,
        "period_days": period_days,
        "apy_percent": apy,
        "expected_reward_ton": expected_reward,
        "actual_reward_ton": None,
        "penalty_paid_ton": None,
        "status": StakeStatus.ACTIVE.value,
        "created_at": now,
        "unlocks_at": unlock_date,
        "completed_at": None,
    }

    stakes_db[stake_id] = stake

    # Обновляем статистику
    _update_user_stats(req.user_id, req.user_telegram_id, stake, "create")

    return _format_stake_response(stake)


@router.get("/stakes", response_model=List[StakeResponse])
async def get_user_stakes(
    user_id: int,
    status: Optional[str] = None,
    limit: int = 20,
):
    """Получить стейки пользователя."""
    user_stakes = [
        s for s in stakes_db.values()
        if s["user_id"] == user_id
    ]

    if status:
        user_stakes = [s for s in user_stakes if s["status"] == status]

    # Сортировка по дате создания
    user_stakes = sorted(user_stakes, key=lambda x: x["created_at"], reverse=True)[:limit]

    return [_format_stake_response(s) for s in user_stakes]


@router.get("/stakes/{stake_id}", response_model=StakeResponse)
async def get_stake(stake_id: str):
    """Получить информацию о стейке."""
    stake = stakes_db.get(stake_id)
    if not stake:
        raise HTTPException(404, "Stake not found")

    return _format_stake_response(stake)


@router.post("/stakes/{stake_id}/unstake")
async def unstake(stake_id: str, req: UnstakeRequest):
    """
    Вывести стейк.

    Если досрочный вывод — взимается штраф.
    """
    stake = stakes_db.get(stake_id)
    if not stake:
        raise HTTPException(404, "Stake not found")

    if stake["status"] != StakeStatus.ACTIVE.value:
        raise HTTPException(400, "Stake is not active")

    now = datetime.utcnow()
    is_unlockable = now >= stake["unlocks_at"]

    if not is_unlockable and not req.force_early:
        raise HTTPException(
            400,
            f"Stake is locked until {stake['unlocks_at'].isoformat()}. "
            "Use force_early=true for early withdrawal with penalty."
        )

    # Расчет выплаты
    if is_unlockable:
        # Полная награда
        stake["status"] = StakeStatus.COMPLETED.value
        stake["actual_reward_ton"] = stake["expected_reward_ton"]
        stake["penalty_paid_ton"] = Decimal("0")
        total_payout = stake["gift_value_ton"] + stake["expected_reward_ton"]
    else:
        # Досрочный вывод со штрафом
        stake["status"] = StakeStatus.WITHDRAWN.value
        penalty = StakingEngine.calculate_early_withdrawal_penalty(stake["gift_value_ton"])
        stake["actual_reward_ton"] = Decimal("0")
        stake["penalty_paid_ton"] = penalty
        total_payout = stake["gift_value_ton"] - penalty

    stake["completed_at"] = now

    # Обновляем статистику
    _update_user_stats(stake["user_id"], stake["user_telegram_id"], stake, "unstake")

    return {
        "stake_id": stake_id,
        "status": stake["status"],
        "gift_value_ton": str(stake["gift_value_ton"]),
        "reward_ton": str(stake["actual_reward_ton"]),
        "penalty_ton": str(stake["penalty_paid_ton"]),
        "total_payout_ton": str(total_payout),
        "early_withdrawal": not is_unlockable,
    }


@router.get("/stats/{user_id}", response_model=StatsResponse)
async def get_user_stats(user_id: int):
    """Статистика стейкинга пользователя."""
    stats = user_stats_db.get(user_id)

    if not stats:
        return StatsResponse(
            total_stakes=0,
            active_stakes=0,
            completed_stakes=0,
            total_staked_ton="0",
            currently_staked_ton="0",
            total_rewards_earned_ton="0",
            total_penalties_paid_ton="0",
            net_profit_ton="0",
        )

    return StatsResponse(
        total_stakes=stats["total_stakes"],
        active_stakes=stats["active_stakes"],
        completed_stakes=stats["completed_stakes"],
        total_staked_ton=str(stats["total_staked_ton"]),
        currently_staked_ton=str(stats["currently_staked_ton"]),
        total_rewards_earned_ton=str(stats["total_rewards_earned_ton"]),
        total_penalties_paid_ton=str(stats["total_penalties_paid_ton"]),
        net_profit_ton=str(stats["total_rewards_earned_ton"] - stats["total_penalties_paid_ton"]),
    )


@router.get("/leaderboard")
async def get_staking_leaderboard(limit: int = 10):
    """Лидерборд по общей сумме стейка."""
    # Сортируем по total_staked_ton
    sorted_users = sorted(
        user_stats_db.values(),
        key=lambda x: x["total_staked_ton"],
        reverse=True,
    )[:limit]

    return {
        "leaderboard": [
            {
                "rank": i + 1,
                "user_id": u["user_id"],
                "user_name": u.get("user_name", "Unknown"),
                "total_staked_ton": str(u["total_staked_ton"]),
                "total_rewards_ton": str(u["total_rewards_earned_ton"]),
                "active_stakes": u["active_stakes"],
            }
            for i, u in enumerate(sorted_users)
        ]
    }


# =============================================================================
# Helper Functions
# =============================================================================

def _format_stake_response(stake: dict) -> StakeResponse:
    """Форматировать стейк для ответа."""
    now = datetime.utcnow()
    is_unlockable = now >= stake["unlocks_at"]
    days_remaining = max(0, (stake["unlocks_at"] - now).days) if not is_unlockable else 0

    return StakeResponse(
        id=stake["id"],
        user_id=stake["user_id"],
        gift_address=stake["gift_address"],
        gift_name=stake["gift_name"],
        gift_image_url=stake["gift_image_url"],
        gift_value_ton=str(stake["gift_value_ton"]),
        period=stake["period"].value if isinstance(stake["period"], StakePeriod) else stake["period"],
        period_days=stake["period_days"],
        apy_percent=str(stake["apy_percent"]),
        expected_reward_ton=str(stake["expected_reward_ton"]),
        status=stake["status"],
        created_at=stake["created_at"].isoformat(),
        unlocks_at=stake["unlocks_at"].isoformat(),
        days_remaining=days_remaining,
        is_unlockable=is_unlockable,
    )


def _update_user_stats(user_id: int, telegram_id: int, stake: dict, action: str):
    """Обновить статистику пользователя."""
    if user_id not in user_stats_db:
        user_stats_db[user_id] = {
            "user_id": user_id,
            "telegram_id": telegram_id,
            "user_name": stake.get("user_name", "Unknown"),
            "total_stakes": 0,
            "active_stakes": 0,
            "completed_stakes": 0,
            "total_staked_ton": Decimal("0"),
            "currently_staked_ton": Decimal("0"),
            "total_rewards_earned_ton": Decimal("0"),
            "total_penalties_paid_ton": Decimal("0"),
        }

    stats = user_stats_db[user_id]

    if action == "create":
        stats["total_stakes"] += 1
        stats["active_stakes"] += 1
        stats["total_staked_ton"] += stake["gift_value_ton"]
        stats["currently_staked_ton"] += stake["gift_value_ton"]

    elif action == "unstake":
        stats["active_stakes"] -= 1
        stats["currently_staked_ton"] -= stake["gift_value_ton"]

        if stake["status"] == StakeStatus.COMPLETED.value:
            stats["completed_stakes"] += 1
            stats["total_rewards_earned_ton"] += stake["actual_reward_ton"]
        elif stake["status"] == StakeStatus.WITHDRAWN.value:
            stats["total_penalties_paid_ton"] += stake["penalty_paid_ton"]

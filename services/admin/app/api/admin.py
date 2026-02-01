"""
Admin API endpoints - полный контроль над gambling

Эндпоинты:
- /admin/settings - CRUD настроек игр (RTP, house edge, лимиты)
- /admin/targets - таргетирование пользователей (win/lose)
- /admin/rounds - ручное управление раундами
- /admin/stats - статистика и аналитика
- /admin/audit - лог действий
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

from ..database import get_session
from ..services.admin_service import AdminService
from ..models.settings import GameType, TargetMode

router = APIRouter(prefix="/admin", tags=["Admin Panel"])


# ==========================================
# Pydantic Schemas
# ==========================================

class GameSettingsUpdate(BaseModel):
    rtp_percent: Optional[float] = Field(None, ge=50.0, le=99.0)
    house_edge_percent: Optional[float] = Field(None, ge=1.0, le=50.0)
    min_multiplier: Optional[float] = None
    max_multiplier: Optional[float] = None
    min_bet: Optional[float] = Field(None, ge=0.01)
    max_bet: Optional[float] = None
    is_enabled: Optional[bool] = None
    rigged_mode: Optional[bool] = None
    rigged_win_rate: Optional[float] = Field(None, ge=0.0, le=1.0)
    big_win_threshold: Optional[float] = None
    big_win_frequency: Optional[float] = Field(None, ge=0.0, le=1.0)
    custom_settings: Optional[Dict[str, Any]] = None


class UserTargetCreate(BaseModel):
    user_id: str
    username: Optional[str] = None
    game_type: Optional[GameType] = None
    target_mode: TargetMode
    forced_multiplier: Optional[float] = None
    forced_result: Optional[Dict] = None
    custom_rtp: Optional[float] = Field(None, ge=50.0, le=99.0)
    uses: int = Field(1, ge=-1)  # -1 = бесконечно
    active_hours: Optional[int] = None
    note: Optional[str] = None


class RoundOverrideCreate(BaseModel):
    game_type: GameType
    round_number: Optional[int] = None
    crash_point: Optional[float] = Field(None, ge=1.0)
    slot: Optional[int] = Field(None, ge=0, le=8)
    result: Optional[Dict] = None
    target_user_id: Optional[str] = None
    target_mode: Optional[TargetMode] = None
    note: Optional[str] = None


class QuickCrashSet(BaseModel):
    crash_point: float = Field(..., ge=1.0, le=10000.0)
    note: Optional[str] = None


class QuickForceWin(BaseModel):
    user_id: str
    game_type: Optional[GameType] = None
    multiplier: Optional[float] = None
    uses: int = 1
    note: Optional[str] = None


class QuickForceLose(BaseModel):
    user_id: str
    game_type: Optional[GameType] = None
    uses: int = 1
    note: Optional[str] = None


class RTPSet(BaseModel):
    rtp_percent: float = Field(..., ge=50.0, le=99.0)


# Временный admin_id (в продакшне заменить на JWT/auth)
ADMIN_ID = "admin_default"


# ==========================================
# НАСТРОЙКИ ИГР
# ==========================================

@router.get("/settings")
async def get_all_settings():
    """Получить настройки всех игр"""
    async with get_session() as session:
        service = AdminService(session)
        settings = await service.get_all_game_settings()
        return {
            "settings": [
                {
                    "id": s.id,
                    "game_type": s.game_type.value,
                    "is_enabled": s.is_enabled,
                    "rtp_percent": s.rtp_percent,
                    "house_edge_percent": s.house_edge_percent,
                    "min_multiplier": s.min_multiplier,
                    "max_multiplier": s.max_multiplier,
                    "min_bet": s.min_bet,
                    "max_bet": s.max_bet,
                    "big_win_threshold": s.big_win_threshold,
                    "big_win_frequency": s.big_win_frequency,
                    "rigged_mode": s.rigged_mode,
                    "rigged_win_rate": s.rigged_win_rate,
                    "custom_settings": s.custom_settings
                }
                for s in settings
            ]
        }


@router.get("/settings/{game_type}")
async def get_game_settings(game_type: GameType):
    """Получить настройки конкретной игры"""
    async with get_session() as session:
        service = AdminService(session)
        s = await service.get_game_settings(game_type)
        if not s:
            raise HTTPException(404, f"Settings for {game_type.value} not found")
        return {
            "id": s.id,
            "game_type": s.game_type.value,
            "is_enabled": s.is_enabled,
            "rtp_percent": s.rtp_percent,
            "house_edge_percent": s.house_edge_percent,
            "min_multiplier": s.min_multiplier,
            "max_multiplier": s.max_multiplier,
            "min_bet": s.min_bet,
            "max_bet": s.max_bet,
            "rigged_mode": s.rigged_mode,
            "rigged_win_rate": s.rigged_win_rate,
            "custom_settings": s.custom_settings
        }


@router.put("/settings/{game_type}")
async def update_game_settings(game_type: GameType, data: GameSettingsUpdate):
    """Обновить настройки игры"""
    async with get_session() as session:
        service = AdminService(session)
        s = await service.update_game_settings(
            game_type, ADMIN_ID,
            **data.model_dump(exclude_none=True)
        )
        return {"status": "ok", "game_type": game_type.value, "rtp": s.rtp_percent}


@router.post("/settings/{game_type}/rtp")
async def set_rtp(game_type: GameType, data: RTPSet):
    """Быстрая установка RTP"""
    async with get_session() as session:
        service = AdminService(session)
        s = await service.set_rtp(game_type, data.rtp_percent, ADMIN_ID)
        return {
            "status": "ok",
            "game_type": game_type.value,
            "rtp_percent": s.rtp_percent,
            "house_edge_percent": s.house_edge_percent
        }


@router.post("/settings/{game_type}/toggle")
async def toggle_game(game_type: GameType, enabled: bool = True):
    """Включить/выключить игру"""
    async with get_session() as session:
        service = AdminService(session)
        s = await service.toggle_game(game_type, enabled, ADMIN_ID)
        return {"status": "ok", "game_type": game_type.value, "is_enabled": s.is_enabled}


@router.post("/settings/{game_type}/rigged")
async def toggle_rigged(game_type: GameType, enabled: bool = True, win_rate: float = 0.3):
    """Включить/выключить режим подкрутки"""
    async with get_session() as session:
        service = AdminService(session)
        s = await service.toggle_rigged_mode(game_type, enabled, win_rate, ADMIN_ID)
        return {
            "status": "ok",
            "game_type": game_type.value,
            "rigged_mode": s.rigged_mode,
            "rigged_win_rate": s.rigged_win_rate
        }


@router.post("/settings/init-defaults")
async def init_default_settings():
    """Инициализировать дефолтные настройки для всех игр"""
    async with get_session() as session:
        service = AdminService(session)
        created = []
        for game_type in GameType:
            existing = await service.get_game_settings(game_type)
            if not existing:
                await service.create_game_settings(game_type, ADMIN_ID)
                created.append(game_type.value)
        return {"status": "ok", "created": created}


# ==========================================
# ТАРГЕТИРОВАНИЕ ПОЛЬЗОВАТЕЛЕЙ
# ==========================================

@router.get("/targets")
async def get_targets(active_only: bool = True):
    """Список всех таргетов"""
    async with get_session() as session:
        service = AdminService(session)
        targets = await service.get_all_user_targets(active_only)
        return {
            "targets": [
                {
                    "id": t.id,
                    "user_id": t.user_id,
                    "username": t.username,
                    "game_type": t.game_type.value if t.game_type else None,
                    "target_mode": t.target_mode.value,
                    "forced_multiplier": t.forced_multiplier,
                    "custom_rtp": t.custom_rtp,
                    "uses_remaining": t.uses_remaining,
                    "uses_total": t.uses_total,
                    "is_active": t.is_active,
                    "admin_note": t.admin_note,
                    "active_until": t.active_until.isoformat() if t.active_until else None
                }
                for t in targets
            ]
        }


@router.post("/targets")
async def create_target(data: UserTargetCreate):
    """Создать таргет на пользователя"""
    async with get_session() as session:
        service = AdminService(session)
        t = await service.create_user_target(
            user_id=data.user_id,
            target_mode=data.target_mode,
            admin_id=ADMIN_ID,
            game_type=data.game_type,
            username=data.username,
            forced_multiplier=data.forced_multiplier,
            forced_result=data.forced_result,
            custom_rtp=data.custom_rtp,
            uses=data.uses,
            active_hours=data.active_hours,
            note=data.note
        )
        return {"status": "ok", "target_id": t.id}


@router.post("/targets/force-win")
async def quick_force_win(data: QuickForceWin):
    """Быстро: заставить пользователя выиграть"""
    async with get_session() as session:
        service = AdminService(session)
        t = await service.force_user_win(
            user_id=data.user_id,
            admin_id=ADMIN_ID,
            game_type=data.game_type,
            multiplier=data.multiplier,
            uses=data.uses,
            note=data.note
        )
        return {"status": "ok", "target_id": t.id, "message": f"User {data.user_id} will WIN next {data.uses} game(s)"}


@router.post("/targets/force-lose")
async def quick_force_lose(data: QuickForceLose):
    """Быстро: заставить пользователя проиграть"""
    async with get_session() as session:
        service = AdminService(session)
        t = await service.force_user_lose(
            user_id=data.user_id,
            admin_id=ADMIN_ID,
            game_type=data.game_type,
            uses=data.uses,
            note=data.note
        )
        return {"status": "ok", "target_id": t.id, "message": f"User {data.user_id} will LOSE next {data.uses} game(s)"}


@router.delete("/targets/{target_id}")
async def delete_target(target_id: int):
    """Удалить таргет"""
    async with get_session() as session:
        service = AdminService(session)
        await service.delete_user_target(target_id, ADMIN_ID)
        return {"status": "ok"}


@router.get("/targets/check/{user_id}")
async def check_user_target(user_id: str, game_type: Optional[GameType] = None):
    """Проверить есть ли активный таргет на пользователя"""
    async with get_session() as session:
        service = AdminService(session)
        target = await service.get_user_target(user_id, game_type)
        if target:
            return {
                "has_target": True,
                "mode": target.target_mode.value,
                "forced_multiplier": target.forced_multiplier,
                "uses_remaining": target.uses_remaining
            }
        return {"has_target": False}


# ==========================================
# УПРАВЛЕНИЕ РАУНДАМИ
# ==========================================

@router.get("/rounds/{game_type}")
async def get_pending_overrides(game_type: GameType):
    """Получить ожидающие оверрайды"""
    async with get_session() as session:
        service = AdminService(session)
        overrides = await service.get_pending_overrides(game_type)
        return {
            "overrides": [
                {
                    "id": o.id,
                    "game_type": o.game_type.value,
                    "round_number": o.round_number,
                    "forced_crash_point": o.forced_crash_point,
                    "forced_slot": o.forced_slot,
                    "forced_result": o.forced_result,
                    "target_user_id": o.target_user_id,
                    "is_used": o.is_used,
                    "admin_note": o.admin_note
                }
                for o in overrides
            ]
        }


@router.post("/rounds")
async def create_round_override(data: RoundOverrideCreate):
    """Создать оверрайд раунда"""
    async with get_session() as session:
        service = AdminService(session)
        o = await service.create_round_override(
            game_type=data.game_type,
            admin_id=ADMIN_ID,
            round_number=data.round_number,
            crash_point=data.crash_point,
            slot=data.slot,
            result=data.result,
            target_user_id=data.target_user_id,
            target_mode=data.target_mode,
            note=data.note
        )
        return {"status": "ok", "override_id": o.id}


@router.post("/rounds/force-crash")
async def quick_force_crash(data: QuickCrashSet):
    """Быстро: установить crash point для следующего раунда Trading"""
    async with get_session() as session:
        service = AdminService(session)
        o = await service.force_next_crash(data.crash_point, ADMIN_ID, data.note)
        return {
            "status": "ok",
            "override_id": o.id,
            "message": f"Next trading round will crash at {data.crash_point}x"
        }


@router.post("/rounds/force-plinko-slot")
async def quick_force_plinko(slot: int = Query(..., ge=0, le=8), user_id: Optional[str] = None):
    """Быстро: установить слот для следующего дропа Plinko"""
    async with get_session() as session:
        service = AdminService(session)
        o = await service.force_next_plinko_slot(slot, ADMIN_ID, user_id)
        labels = ['💀', '🎁', '2.0x', '0.7x', '0.6x', '0.7x', '2.0x', '🎁', '💀']
        return {
            "status": "ok",
            "override_id": o.id,
            "message": f"Next plinko drop → slot {slot} ({labels[slot]})"
        }


# ==========================================
# СТАТИСТИКА
# ==========================================

@router.get("/stats")
async def get_summary_stats():
    """Сводная статистика"""
    async with get_session() as session:
        service = AdminService(session)
        return await service.get_summary_stats()


@router.get("/stats/{game_type}")
async def get_game_stats(game_type: GameType, days: int = 7):
    """Статистика по игре"""
    async with get_session() as session:
        service = AdminService(session)
        stats = await service.get_daily_stats(game_type, days)
        return {
            "game_type": game_type.value,
            "days": days,
            "stats": [
                {
                    "date": s.date.isoformat(),
                    "total_bets": s.total_bets,
                    "volume": s.total_bet_amount,
                    "payouts": s.total_payouts,
                    "profit": s.house_profit,
                    "actual_rtp": s.actual_rtp,
                    "unique_players": s.unique_players,
                    "biggest_win": s.biggest_win
                }
                for s in stats
            ]
        }


# ==========================================
# АУДИТ
# ==========================================

@router.get("/audit")
async def get_audit_logs(limit: int = 50):
    """Получить лог действий"""
    async with get_session() as session:
        service = AdminService(session)
        logs = await service.get_audit_logs(limit)
        return {
            "logs": [
                {
                    "id": l.id,
                    "timestamp": l.timestamp.isoformat() if l.timestamp else None,
                    "admin_id": l.admin_id,
                    "action": l.action.value,
                    "description": l.action_description,
                    "entity_type": l.entity_type,
                    "entity_id": l.entity_id,
                    "old_value": l.old_value,
                    "new_value": l.new_value
                }
                for l in logs
            ]
        }


# ==========================================
# EMERGENCY
# ==========================================

@router.post("/emergency/stop-all")
async def emergency_stop_all():
    """Экстренная остановка всех игр"""
    async with get_session() as session:
        service = AdminService(session)
        for game_type in GameType:
            await service.toggle_game(game_type, False, ADMIN_ID)
        return {"status": "ok", "message": "ALL GAMES STOPPED"}


@router.post("/emergency/resume-all")
async def emergency_resume_all():
    """Возобновить все игры"""
    async with get_session() as session:
        service = AdminService(session)
        for game_type in GameType:
            await service.toggle_game(game_type, True, ADMIN_ID)
        return {"status": "ok", "message": "ALL GAMES RESUMED"}

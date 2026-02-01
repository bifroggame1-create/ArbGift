"""
Admin Service - основная логика управления gambling

Функционал:
- CRUD для настроек игр
- Управление таргетированием пользователей
- Ручное управление раундами
- Статистика и аналитика
- Аудит логирование
"""
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy import select, update, delete, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.settings import (
    GameSettings, UserTarget, RoundOverride, GameStatistics,
    GameType, TargetMode
)
from ..models.audit import AuditLog, AuditAction
from ..config import DEFAULT_GAME_SETTINGS


class AdminService:
    """Сервис администрирования gambling"""

    def __init__(self, session: AsyncSession):
        self.session = session

    # ==========================================
    # НАСТРОЙКИ ИГР
    # ==========================================

    async def get_all_game_settings(self) -> List[GameSettings]:
        """Получить настройки всех игр"""
        result = await self.session.execute(
            select(GameSettings).order_by(GameSettings.game_type)
        )
        return result.scalars().all()

    async def get_game_settings(self, game_type: GameType) -> Optional[GameSettings]:
        """Получить настройки конкретной игры"""
        result = await self.session.execute(
            select(GameSettings).where(GameSettings.game_type == game_type)
        )
        return result.scalar_one_or_none()

    async def create_game_settings(
        self,
        game_type: GameType,
        admin_id: str,
        **kwargs
    ) -> GameSettings:
        """Создать настройки игры с дефолтными значениями"""
        # Берем дефолты из конфига
        defaults = DEFAULT_GAME_SETTINGS.get(game_type.value, {})

        settings = GameSettings(
            game_type=game_type,
            rtp_percent=kwargs.get('rtp_percent', defaults.get('rtp_percent', 97.0)),
            house_edge_percent=kwargs.get('house_edge_percent', defaults.get('house_edge_percent', 3.0)),
            min_multiplier=kwargs.get('min_multiplier', defaults.get('min_multiplier', 1.0)),
            max_multiplier=kwargs.get('max_multiplier', defaults.get('max_multiplier', 100.0)),
            min_bet=kwargs.get('min_bet', defaults.get('min_bet', 0.1)),
            max_bet=kwargs.get('max_bet', defaults.get('max_bet', 100.0)),
            custom_settings=kwargs.get('custom_settings', defaults.get('custom_settings', {})),
            is_enabled=kwargs.get('is_enabled', True),
            rigged_mode=kwargs.get('rigged_mode', False),
            rigged_win_rate=kwargs.get('rigged_win_rate', 0.3),
        )

        self.session.add(settings)
        await self.session.flush()

        # Логируем действие
        await self._log_action(
            admin_id=admin_id,
            action=AuditAction.GAME_SETTINGS_CREATE,
            entity_type="game_settings",
            entity_id=str(settings.id),
            new_value=self._settings_to_dict(settings),
            description=f"Созданы настройки для {game_type.value}"
        )

        return settings

    async def update_game_settings(
        self,
        game_type: GameType,
        admin_id: str,
        **kwargs
    ) -> Optional[GameSettings]:
        """Обновить настройки игры"""
        settings = await self.get_game_settings(game_type)
        if not settings:
            # Создаем новые настройки
            return await self.create_game_settings(game_type, admin_id, **kwargs)

        old_value = self._settings_to_dict(settings)

        # Обновляем только переданные поля
        for key, value in kwargs.items():
            if hasattr(settings, key) and value is not None:
                setattr(settings, key, value)

        await self.session.flush()

        # Логируем
        await self._log_action(
            admin_id=admin_id,
            action=AuditAction.GAME_SETTINGS_UPDATE,
            entity_type="game_settings",
            entity_id=str(settings.id),
            old_value=old_value,
            new_value=self._settings_to_dict(settings),
            description=f"Обновлены настройки {game_type.value}"
        )

        return settings

    async def set_rtp(self, game_type: GameType, rtp_percent: float, admin_id: str) -> GameSettings:
        """Быстрая установка RTP"""
        house_edge = 100.0 - rtp_percent
        return await self.update_game_settings(
            game_type, admin_id,
            rtp_percent=rtp_percent,
            house_edge_percent=house_edge
        )

    async def toggle_game(self, game_type: GameType, enabled: bool, admin_id: str) -> GameSettings:
        """Включить/выключить игру"""
        action = AuditAction.GAME_ENABLE if enabled else AuditAction.GAME_DISABLE
        settings = await self.update_game_settings(game_type, admin_id, is_enabled=enabled)

        await self._log_action(
            admin_id=admin_id,
            action=action,
            entity_type="game_settings",
            entity_id=str(settings.id),
            description=f"Игра {game_type.value} {'включена' if enabled else 'выключена'}"
        )

        return settings

    async def toggle_rigged_mode(
        self,
        game_type: GameType,
        enabled: bool,
        win_rate: float,
        admin_id: str
    ) -> GameSettings:
        """Включить/выключить режим подкрутки"""
        return await self.update_game_settings(
            game_type, admin_id,
            rigged_mode=enabled,
            rigged_win_rate=win_rate
        )

    # ==========================================
    # ТАРГЕТИРОВАНИЕ ПОЛЬЗОВАТЕЛЕЙ
    # ==========================================

    async def get_all_user_targets(self, active_only: bool = True) -> List[UserTarget]:
        """Получить все таргеты пользователей"""
        query = select(UserTarget)
        if active_only:
            query = query.where(UserTarget.is_active == True)
        result = await self.session.execute(query.order_by(UserTarget.created_at.desc()))
        return result.scalars().all()

    async def get_user_target(self, user_id: str, game_type: GameType = None) -> Optional[UserTarget]:
        """Получить активный таргет для пользователя"""
        query = select(UserTarget).where(
            and_(
                UserTarget.user_id == user_id,
                UserTarget.is_active == True
            )
        )
        if game_type:
            query = query.where(
                (UserTarget.game_type == game_type) | (UserTarget.game_type.is_(None))
            )

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def create_user_target(
        self,
        user_id: str,
        target_mode: TargetMode,
        admin_id: str,
        game_type: GameType = None,
        username: str = None,
        forced_multiplier: float = None,
        forced_result: Dict = None,
        custom_rtp: float = None,
        uses: int = 1,
        active_hours: int = None,
        note: str = None
    ) -> UserTarget:
        """Создать таргет на пользователя"""
        active_until = None
        if active_hours:
            active_until = datetime.utcnow() + timedelta(hours=active_hours)

        target = UserTarget(
            user_id=user_id,
            username=username,
            game_type=game_type,
            target_mode=target_mode,
            forced_multiplier=forced_multiplier,
            forced_result=forced_result,
            custom_rtp=custom_rtp,
            uses_remaining=uses,
            active_until=active_until,
            admin_note=note
        )

        self.session.add(target)
        await self.session.flush()

        # Логируем
        await self._log_action(
            admin_id=admin_id,
            action=AuditAction.USER_TARGET_CREATE,
            entity_type="user_target",
            entity_id=str(target.id),
            new_value={
                "user_id": user_id,
                "mode": target_mode.value,
                "game": game_type.value if game_type else "all",
                "uses": uses
            },
            description=f"Таргет на {user_id}: {target_mode.value}"
        )

        return target

    async def force_user_win(
        self,
        user_id: str,
        admin_id: str,
        game_type: GameType = None,
        multiplier: float = None,
        uses: int = 1,
        note: str = None
    ) -> UserTarget:
        """Быстрая установка принудительного выигрыша"""
        return await self.create_user_target(
            user_id=user_id,
            target_mode=TargetMode.WIN,
            admin_id=admin_id,
            game_type=game_type,
            forced_multiplier=multiplier,
            uses=uses,
            note=note or f"Forced win by admin {admin_id}"
        )

    async def force_user_lose(
        self,
        user_id: str,
        admin_id: str,
        game_type: GameType = None,
        uses: int = 1,
        note: str = None
    ) -> UserTarget:
        """Быстрая установка принудительного проигрыша"""
        return await self.create_user_target(
            user_id=user_id,
            target_mode=TargetMode.LOSE,
            admin_id=admin_id,
            game_type=game_type,
            uses=uses,
            note=note or f"Forced loss by admin {admin_id}"
        )

    async def consume_user_target(self, target: UserTarget) -> bool:
        """Использовать одно применение таргета"""
        if target.uses_remaining == 0:
            return False

        if target.uses_remaining > 0:  # -1 = бесконечно
            target.uses_remaining -= 1

        target.uses_total += 1

        if target.uses_remaining == 0:
            target.is_active = False

        await self.session.flush()
        return True

    async def delete_user_target(self, target_id: int, admin_id: str):
        """Удалить таргет"""
        result = await self.session.execute(
            select(UserTarget).where(UserTarget.id == target_id)
        )
        target = result.scalar_one_or_none()
        if target:
            await self._log_action(
                admin_id=admin_id,
                action=AuditAction.USER_TARGET_DELETE,
                entity_type="user_target",
                entity_id=str(target_id),
                old_value={"user_id": target.user_id, "mode": target.target_mode.value},
                description=f"Удален таргет {target_id}"
            )
            await self.session.delete(target)

    # ==========================================
    # УПРАВЛЕНИЕ РАУНДАМИ
    # ==========================================

    async def get_pending_overrides(self, game_type: GameType) -> List[RoundOverride]:
        """Получить неиспользованные оверрайды раундов"""
        result = await self.session.execute(
            select(RoundOverride).where(
                and_(
                    RoundOverride.game_type == game_type,
                    RoundOverride.is_used == False
                )
            ).order_by(RoundOverride.created_at)
        )
        return result.scalars().all()

    async def create_round_override(
        self,
        game_type: GameType,
        admin_id: str,
        round_number: int = None,
        crash_point: float = None,
        slot: int = None,
        result: Dict = None,
        target_user_id: str = None,
        target_mode: TargetMode = None,
        note: str = None
    ) -> RoundOverride:
        """Создать оверрайд раунда"""
        override = RoundOverride(
            game_type=game_type,
            round_number=round_number,
            forced_crash_point=crash_point,
            forced_slot=slot,
            forced_result=result,
            target_user_id=target_user_id,
            target_mode=target_mode,
            admin_note=note,
            created_by=admin_id
        )

        self.session.add(override)
        await self.session.flush()

        await self._log_action(
            admin_id=admin_id,
            action=AuditAction.ROUND_OVERRIDE_CREATE,
            entity_type="round_override",
            entity_id=str(override.id),
            new_value={
                "game": game_type.value,
                "round": round_number,
                "crash": crash_point,
                "slot": slot
            },
            description=f"Оверрайд раунда для {game_type.value}"
        )

        return override

    async def force_next_crash(
        self,
        crash_point: float,
        admin_id: str,
        note: str = None
    ) -> RoundOverride:
        """Быстрая установка crash point для следующего раунда Trading"""
        return await self.create_round_override(
            game_type=GameType.TRADING,
            admin_id=admin_id,
            crash_point=crash_point,
            note=note or f"Force crash at {crash_point}x"
        )

    async def force_next_plinko_slot(
        self,
        slot: int,
        admin_id: str,
        target_user_id: str = None,
        note: str = None
    ) -> RoundOverride:
        """Быстрая установка слота для следующего дропа Plinko"""
        return await self.create_round_override(
            game_type=GameType.PLINKO,
            admin_id=admin_id,
            slot=slot,
            target_user_id=target_user_id,
            note=note or f"Force slot {slot}"
        )

    async def consume_round_override(self, override: RoundOverride):
        """Отметить оверрайд как использованный"""
        override.is_used = True
        override.used_at = datetime.utcnow()
        await self.session.flush()

    # ==========================================
    # СТАТИСТИКА
    # ==========================================

    async def get_daily_stats(
        self,
        game_type: GameType = None,
        days: int = 7
    ) -> List[GameStatistics]:
        """Получить статистику за последние N дней"""
        since = datetime.utcnow() - timedelta(days=days)
        query = select(GameStatistics).where(GameStatistics.date >= since)
        if game_type:
            query = query.where(GameStatistics.game_type == game_type)

        result = await self.session.execute(query.order_by(GameStatistics.date.desc()))
        return result.scalars().all()

    async def record_game_result(
        self,
        game_type: GameType,
        bet_amount: float,
        payout: float,
        user_id: str,
        is_new_player: bool = False
    ):
        """Записать результат игры в статистику"""
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

        # Ищем или создаем запись за сегодня
        result = await self.session.execute(
            select(GameStatistics).where(
                and_(
                    GameStatistics.game_type == game_type,
                    GameStatistics.date == today
                )
            )
        )
        stats = result.scalar_one_or_none()

        if not stats:
            stats = GameStatistics(game_type=game_type, date=today)
            self.session.add(stats)

        # Обновляем статистику
        profit = bet_amount - payout

        stats.total_bets += 1
        stats.total_bet_amount += bet_amount
        stats.total_payouts += payout
        stats.house_profit += profit

        if bet_amount > 0:
            stats.actual_rtp = (stats.total_payouts / stats.total_bet_amount) * 100

        if payout > stats.biggest_win:
            stats.biggest_win = payout

        if profit > 0 and profit > stats.biggest_loss:
            stats.biggest_loss = profit

        if is_new_player:
            stats.new_players += 1

        await self.session.flush()

    async def get_summary_stats(self) -> Dict[str, Any]:
        """Получить сводную статистику"""
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        week_ago = today - timedelta(days=7)

        # Статистика за сегодня
        today_result = await self.session.execute(
            select(
                func.sum(GameStatistics.total_bets),
                func.sum(GameStatistics.total_bet_amount),
                func.sum(GameStatistics.total_payouts),
                func.sum(GameStatistics.house_profit)
            ).where(GameStatistics.date == today)
        )
        today_stats = today_result.one()

        # Статистика за неделю
        week_result = await self.session.execute(
            select(
                func.sum(GameStatistics.total_bets),
                func.sum(GameStatistics.total_bet_amount),
                func.sum(GameStatistics.total_payouts),
                func.sum(GameStatistics.house_profit)
            ).where(GameStatistics.date >= week_ago)
        )
        week_stats = week_result.one()

        return {
            "today": {
                "bets": today_stats[0] or 0,
                "volume": float(today_stats[1] or 0),
                "payouts": float(today_stats[2] or 0),
                "profit": float(today_stats[3] or 0)
            },
            "week": {
                "bets": week_stats[0] or 0,
                "volume": float(week_stats[1] or 0),
                "payouts": float(week_stats[2] or 0),
                "profit": float(week_stats[3] or 0)
            }
        }

    # ==========================================
    # АУДИТ
    # ==========================================

    async def _log_action(
        self,
        admin_id: str,
        action: AuditAction,
        entity_type: str = None,
        entity_id: str = None,
        old_value: Dict = None,
        new_value: Dict = None,
        description: str = None,
        metadata: Dict = None
    ):
        """Записать действие в аудит лог"""
        log = AuditLog(
            admin_id=admin_id,
            action=action,
            action_description=description,
            entity_type=entity_type,
            entity_id=entity_id,
            old_value=old_value,
            new_value=new_value,
            metadata=metadata
        )
        self.session.add(log)
        await self.session.flush()

    async def get_audit_logs(
        self,
        limit: int = 100,
        action: AuditAction = None,
        admin_id: str = None
    ) -> List[AuditLog]:
        """Получить записи аудита"""
        query = select(AuditLog)

        if action:
            query = query.where(AuditLog.action == action)
        if admin_id:
            query = query.where(AuditLog.admin_id == admin_id)

        result = await self.session.execute(
            query.order_by(AuditLog.timestamp.desc()).limit(limit)
        )
        return result.scalars().all()

    # ==========================================
    # HELPERS
    # ==========================================

    def _settings_to_dict(self, settings: GameSettings) -> Dict:
        """Конвертировать настройки в словарь"""
        return {
            "game_type": settings.game_type.value,
            "is_enabled": settings.is_enabled,
            "rtp_percent": settings.rtp_percent,
            "house_edge_percent": settings.house_edge_percent,
            "min_multiplier": settings.min_multiplier,
            "max_multiplier": settings.max_multiplier,
            "min_bet": settings.min_bet,
            "max_bet": settings.max_bet,
            "rigged_mode": settings.rigged_mode,
            "rigged_win_rate": settings.rigged_win_rate,
            "custom_settings": settings.custom_settings
        }

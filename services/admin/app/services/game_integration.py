"""
Game Integration Layer

Этот модуль используется game engines для проверки:
1. Есть ли оверрайд для текущего раунда
2. Есть ли таргет на конкретного пользователя
3. Какой RTP применять
4. Включен ли rigged mode

Game engine вызывает эти функции ПЕРЕД генерацией результата.
"""
from typing import Optional, Dict, Any, Tuple
from datetime import datetime
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.settings import (
    GameSettings, UserTarget, RoundOverride,
    GameType, TargetMode
)


class GameIntegration:
    """
    Интеграционный слой между админ-панелью и game engines

    Использование:
        integration = GameIntegration(db_session)

        # Проверить оверрайд раунда
        override = await integration.check_round_override(GameType.TRADING)
        if override:
            crash_point = override['crash_point']

        # Проверить таргет пользователя
        target = await integration.check_user_target(user_id, GameType.PLINKO)
        if target:
            if target['mode'] == 'win':
                # Генерируем выигрышный результат
            elif target['mode'] == 'lose':
                # Генерируем проигрышный результат

        # Получить RTP для игры/пользователя
        rtp = await integration.get_effective_rtp(user_id, GameType.TRADING)
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def check_round_override(self, game_type: GameType) -> Optional[Dict[str, Any]]:
        """
        Проверить есть ли оверрайд для следующего раунда

        Returns:
            None если оверрайда нет, иначе:
            {
                'id': override_id,
                'crash_point': float or None,
                'slot': int or None,
                'result': dict or None,
                'target_user_id': str or None,
                'target_mode': str or None
            }
        """
        result = await self.session.execute(
            select(RoundOverride).where(
                and_(
                    RoundOverride.game_type == game_type,
                    RoundOverride.is_used == False
                )
            ).order_by(RoundOverride.created_at).limit(1)
        )
        override = result.scalar_one_or_none()

        if not override:
            return None

        # Помечаем как использованный
        override.is_used = True
        override.used_at = datetime.utcnow()
        await self.session.flush()

        return {
            'id': override.id,
            'crash_point': override.forced_crash_point,
            'slot': override.forced_slot,
            'result': override.forced_result,
            'target_user_id': override.target_user_id,
            'target_mode': override.target_mode.value if override.target_mode else None
        }

    async def check_user_target(
        self,
        user_id: str,
        game_type: GameType
    ) -> Optional[Dict[str, Any]]:
        """
        Проверить есть ли активный таргет на пользователя

        Returns:
            None если таргета нет, иначе:
            {
                'id': target_id,
                'mode': 'win' | 'lose' | 'specific',
                'forced_multiplier': float or None,
                'forced_result': dict or None,
                'custom_rtp': float or None
            }
        """
        now = datetime.utcnow()

        result = await self.session.execute(
            select(UserTarget).where(
                and_(
                    UserTarget.user_id == user_id,
                    UserTarget.is_active == True,
                    UserTarget.target_mode != TargetMode.NONE
                )
            ).where(
                # Фильтр по игре (None = все игры)
                (UserTarget.game_type == game_type) | (UserTarget.game_type.is_(None))
            ).where(
                # Фильтр по сроку действия
                (UserTarget.active_until.is_(None)) | (UserTarget.active_until > now)
            ).where(
                # Фильтр по использованиям
                (UserTarget.uses_remaining != 0)
            ).order_by(UserTarget.created_at.desc()).limit(1)
        )
        target = result.scalar_one_or_none()

        if not target:
            return None

        # Уменьшаем счетчик
        if target.uses_remaining > 0:
            target.uses_remaining -= 1
        target.uses_total += 1

        if target.uses_remaining == 0:
            target.is_active = False

        await self.session.flush()

        return {
            'id': target.id,
            'mode': target.target_mode.value,
            'forced_multiplier': target.forced_multiplier,
            'forced_result': target.forced_result,
            'custom_rtp': target.custom_rtp
        }

    async def get_game_settings(self, game_type: GameType) -> Optional[Dict[str, Any]]:
        """Получить настройки игры"""
        result = await self.session.execute(
            select(GameSettings).where(GameSettings.game_type == game_type)
        )
        settings = result.scalar_one_or_none()

        if not settings:
            return None

        return {
            'is_enabled': settings.is_enabled,
            'rtp_percent': settings.rtp_percent,
            'house_edge_percent': settings.house_edge_percent,
            'min_multiplier': settings.min_multiplier,
            'max_multiplier': settings.max_multiplier,
            'min_bet': settings.min_bet,
            'max_bet': settings.max_bet,
            'rigged_mode': settings.rigged_mode,
            'rigged_win_rate': settings.rigged_win_rate,
            'big_win_threshold': settings.big_win_threshold,
            'big_win_frequency': settings.big_win_frequency,
            'custom_settings': settings.custom_settings
        }

    async def get_effective_rtp(
        self,
        user_id: str,
        game_type: GameType
    ) -> float:
        """
        Получить эффективный RTP для пользователя

        Приоритет:
        1. Персональный RTP пользователя (UserTarget.custom_rtp)
        2. Глобальный RTP игры (GameSettings.rtp_percent)
        3. Дефолт 97%
        """
        # Проверяем персональный RTP
        now = datetime.utcnow()
        result = await self.session.execute(
            select(UserTarget).where(
                and_(
                    UserTarget.user_id == user_id,
                    UserTarget.is_active == True,
                    UserTarget.custom_rtp.isnot(None)
                )
            ).where(
                (UserTarget.game_type == game_type) | (UserTarget.game_type.is_(None))
            ).where(
                (UserTarget.active_until.is_(None)) | (UserTarget.active_until > now)
            ).limit(1)
        )
        target = result.scalar_one_or_none()

        if target and target.custom_rtp:
            return target.custom_rtp

        # Глобальный RTP игры
        settings = await self.get_game_settings(game_type)
        if settings:
            return settings['rtp_percent']

        return 97.0  # Дефолт

    async def is_game_enabled(self, game_type: GameType) -> bool:
        """Проверить включена ли игра"""
        settings = await self.get_game_settings(game_type)
        if not settings:
            return True  # Если нет настроек, считаем включенной
        return settings['is_enabled']

    async def validate_bet(
        self,
        game_type: GameType,
        bet_amount: float
    ) -> Tuple[bool, str]:
        """
        Валидация ставки

        Returns:
            (is_valid, error_message)
        """
        settings = await self.get_game_settings(game_type)
        if not settings:
            return True, ""

        if not settings['is_enabled']:
            return False, "Game is currently disabled"

        if bet_amount < settings['min_bet']:
            return False, f"Minimum bet is {settings['min_bet']}"

        if bet_amount > settings['max_bet']:
            return False, f"Maximum bet is {settings['max_bet']}"

        return True, ""

    async def should_player_win(
        self,
        user_id: str,
        game_type: GameType
    ) -> Optional[bool]:
        """
        Определить должен ли игрок выиграть (rigged mode)

        Returns:
            True = принудительный выигрыш
            False = принудительный проигрыш
            None = обычная генерация
        """
        import random

        # Сначала проверяем персональный таргет
        target = await self.check_user_target(user_id, game_type)
        if target:
            if target['mode'] == 'win':
                return True
            elif target['mode'] == 'lose':
                return False

        # Проверяем rigged mode
        settings = await self.get_game_settings(game_type)
        if settings and settings['rigged_mode']:
            # В rigged mode выигрыш определяется rigged_win_rate
            return random.random() < settings['rigged_win_rate']

        return None  # Обычная генерация

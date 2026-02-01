"""
Staking Engine.

Расчет наград, штрафов и управление стейками.
"""
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional

from app.models.stake import StakePeriod, StakeStatus


class StakingEngine:
    """
    Движок стейкинга.

    Рассчитывает награды на основе:
    - Стоимости гифта в TON
    - Периода блокировки
    - APY для периода
    """

    # APY по периодам (годовая процентная ставка)
    APY_RATES = {
        StakePeriod.WEEK_1: Decimal("5"),    # 5% годовых
        StakePeriod.WEEK_2: Decimal("8"),    # 8% годовых
        StakePeriod.MONTH_1: Decimal("12"),  # 12% годовых
        StakePeriod.MONTH_3: Decimal("20"),  # 20% годовых
    }

    # Дни до разблокировки
    PERIOD_DAYS = {
        StakePeriod.WEEK_1: 7,
        StakePeriod.WEEK_2: 14,
        StakePeriod.MONTH_1: 30,
        StakePeriod.MONTH_3: 90,
    }

    # Штраф за досрочный вывод
    EARLY_WITHDRAWAL_PENALTY = Decimal("10")  # 10%

    # Минимальная сумма для стейка
    MIN_STAKE_VALUE_TON = Decimal("1")

    @classmethod
    def get_apy(cls, period: StakePeriod) -> Decimal:
        """Получить APY для периода."""
        return cls.APY_RATES.get(period, Decimal("0"))

    @classmethod
    def get_unlock_date(cls, period: StakePeriod, start_date: Optional[datetime] = None) -> datetime:
        """Рассчитать дату разблокировки."""
        if start_date is None:
            start_date = datetime.utcnow()

        days = cls.PERIOD_DAYS.get(period, 0)
        return start_date + timedelta(days=days)

    @classmethod
    def calculate_reward(
        cls,
        gift_value_ton: Decimal,
        period: StakePeriod,
    ) -> Decimal:
        """
        Рассчитать ожидаемую награду.

        Формула: value * (apy / 100) * (days / 365)

        Пример:
        - Гифт 10 TON на 1 месяц (12% APY)
        - Награда = 10 * 0.12 * (30/365) = 0.0986 TON
        """
        apy = cls.get_apy(period)
        days = cls.PERIOD_DAYS.get(period, 0)

        # Годовая доходность пропорционально периоду
        reward = gift_value_ton * (apy / Decimal("100")) * (Decimal(days) / Decimal("365"))

        return round(reward, 9)

    @classmethod
    def calculate_early_withdrawal_penalty(
        cls,
        gift_value_ton: Decimal,
    ) -> Decimal:
        """
        Рассчитать штраф за досрочный вывод.

        10% от стоимости гифта.
        """
        penalty = gift_value_ton * (cls.EARLY_WITHDRAWAL_PENALTY / Decimal("100"))
        return round(penalty, 9)

    @classmethod
    def validate_stake(
        cls,
        gift_value_ton: Decimal,
        period: StakePeriod,
    ) -> tuple[bool, str]:
        """
        Проверить валидность стейка.

        Возвращает (is_valid, error_message).
        """
        if gift_value_ton < cls.MIN_STAKE_VALUE_TON:
            return False, f"Minimum stake value is {cls.MIN_STAKE_VALUE_TON} TON"

        if period not in cls.APY_RATES:
            return False, f"Invalid staking period: {period}"

        return True, "Valid"

    @classmethod
    def get_stake_preview(
        cls,
        gift_value_ton: Decimal,
        period: StakePeriod,
    ) -> dict:
        """
        Превью стейка с расчетами.

        Для отображения пользователю перед подтверждением.
        """
        is_valid, error = cls.validate_stake(gift_value_ton, period)

        if not is_valid:
            return {"valid": False, "error": error}

        apy = cls.get_apy(period)
        unlock_date = cls.get_unlock_date(period)
        expected_reward = cls.calculate_reward(gift_value_ton, period)
        early_penalty = cls.calculate_early_withdrawal_penalty(gift_value_ton)

        return {
            "valid": True,
            "gift_value_ton": str(gift_value_ton),
            "period": period.value,
            "period_days": cls.PERIOD_DAYS[period],
            "apy_percent": str(apy),
            "unlock_date": unlock_date.isoformat(),
            "expected_reward_ton": str(expected_reward),
            "early_withdrawal_penalty_percent": str(cls.EARLY_WITHDRAWAL_PENALTY),
            "early_withdrawal_penalty_ton": str(early_penalty),
            "total_at_unlock_ton": str(gift_value_ton + expected_reward),
        }

    @classmethod
    def get_available_periods(cls) -> list[dict]:
        """Получить доступные периоды стейкинга."""
        periods = []

        for period in StakePeriod:
            periods.append({
                "period": period.value,
                "days": cls.PERIOD_DAYS[period],
                "apy_percent": str(cls.APY_RATES[period]),
                "label": cls._get_period_label(period),
            })

        return periods

    @staticmethod
    def _get_period_label(period: StakePeriod) -> str:
        """Человекочитаемое название периода."""
        labels = {
            StakePeriod.WEEK_1: "1 Week",
            StakePeriod.WEEK_2: "2 Weeks",
            StakePeriod.MONTH_1: "1 Month",
            StakePeriod.MONTH_3: "3 Months",
        }
        return labels.get(period, period.value)

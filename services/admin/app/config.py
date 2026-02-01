"""
Конфигурация Admin Panel

Настройки безопасности и доступа
"""
import os
from pydantic_settings import BaseSettings
from typing import List


class AdminSettings(BaseSettings):
    """Настройки админ-панели"""

    # База данных
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./admin.db")

    # Безопасность
    ADMIN_SECRET_KEY: str = os.getenv("ADMIN_SECRET_KEY", "your-super-secret-key-change-in-production")

    # Список разрешенных админов (Telegram IDs)
    ADMIN_IDS: List[str] = os.getenv("ADMIN_IDS", "123456789").split(",")

    # JWT настройки
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 часа

    # Лимиты
    MAX_RTP_PERCENT: float = 99.0
    MIN_RTP_PERCENT: float = 50.0
    MAX_HOUSE_EDGE_PERCENT: float = 50.0
    MIN_HOUSE_EDGE_PERCENT: float = 1.0

    # Алерты
    ALERT_THRESHOLD_PROFIT: float = 1000.0  # TON
    ALERT_THRESHOLD_LOSS: float = -500.0  # TON

    class Config:
        env_file = ".env"


settings = AdminSettings()


# Дефолтные настройки для каждой игры
DEFAULT_GAME_SETTINGS = {
    "plinko": {
        "rtp_percent": 97.0,
        "house_edge_percent": 3.0,
        "min_multiplier": 0.0,
        "max_multiplier": 100.0,
        "min_bet": 0.1,
        "max_bet": 50.0,
        "custom_settings": {
            "rows": 16,
            "slots": 9,
            "multipliers": [0.0, 0.0, 2.0, 0.7, 0.6, 0.7, 2.0, 0.0, 0.0]
        }
    },
    "trading": {
        "rtp_percent": 97.0,
        "house_edge_percent": 3.0,
        "min_multiplier": 1.0,
        "max_multiplier": 10000.0,
        "min_bet": 0.1,
        "max_bet": 100.0,
        "custom_settings": {
            "crash_speed": 1.0,
            "min_crash_point": 1.01,
            "round_duration_max": 120,  # секунд
            "betting_phase_duration": 10  # секунд
        }
    },
    "roulette": {
        "rtp_percent": 97.3,
        "house_edge_percent": 2.7,
        "min_multiplier": 2.0,
        "max_multiplier": 36.0,
        "min_bet": 0.1,
        "max_bet": 50.0,
        "custom_settings": {
            "numbers": 37,  # 0-36
            "green_count": 1
        }
    },
    "aviator": {
        "rtp_percent": 97.0,
        "house_edge_percent": 3.0,
        "min_multiplier": 1.0,
        "max_multiplier": 100.0,
        "min_bet": 0.1,
        "max_bet": 100.0,
        "custom_settings": {
            "flight_speed": 1.0,
            "min_flight_time": 1.0
        }
    },
    "upgrade": {
        "rtp_percent": 95.0,
        "house_edge_percent": 5.0,
        "min_multiplier": 1.5,
        "max_multiplier": 10.0,
        "min_bet": 0.5,
        "max_bet": 50.0,
        "custom_settings": {
            "upgrade_success_base": 0.5  # 50% базовый шанс
        }
    },
    "pvp": {
        "rtp_percent": 95.0,  # 5% комиссия площадки
        "house_edge_percent": 5.0,
        "min_bet": 0.5,
        "max_bet": 100.0,
        "custom_settings": {
            "commission_percent": 5.0
        }
    }
}

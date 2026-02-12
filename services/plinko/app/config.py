"""
Plinko Service Configuration.
"""
from functools import lru_cache
from typing import Optional, Dict
from pydantic_settings import BaseSettings


# Multiplier sets per risk level and row count
# Slot count = row_count + 1
MULTIPLIER_SETS: Dict[str, Dict[int, list]] = {
    "low": {
        8: [5.6, 1.5, 0.8, 0.5, 0.3, 0.5, 0.8, 1.5, 5.6],
        12: [8.9, 3, 1.2, 0.7, 0.5, 0.3, 0.2, 0.3, 0.5, 0.7, 1.2, 3, 8.9],
        16: [16, 9, 2, 1, 0.7, 0.4, 0.3, 0.2, 0.2, 0.3, 0.4, 0.7, 1, 2, 9, 16],
    },
    "medium": {
        8: [13, 3, 0.9, 0.4, 0.2, 0.4, 0.9, 3, 13],
        12: [33, 11, 3, 1.2, 0.5, 0.3, 0.2, 0.3, 0.5, 1.2, 3, 11, 33],
        16: [110, 41, 10, 3, 1.2, 0.5, 0.3, 0.2, 0.2, 0.3, 0.5, 1.2, 3, 10, 41, 110],
    },
    "high": {
        8: [29, 4, 0.9, 0.2, 0.1, 0.2, 0.9, 4, 29],
        12: [170, 24, 8.1, 1.5, 0.4, 0.1, 0.1, 0.4, 1.5, 8.1, 24, 170],
        16: [1000, 130, 26, 9, 2, 0.5, 0.1, 0.1, 0.1, 0.1, 0.5, 2, 9, 26, 130, 1000],
    },
}

VALID_RISK_LEVELS = {"low", "medium", "high"}
VALID_ROW_COUNTS = {8, 12, 16}


class Settings(BaseSettings):
    """Application settings."""

    APP_NAME: str = "Plinko Game Service"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/plinko"
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Game settings — Stars currency
    MIN_BET_STARS: int = 10
    MAX_BET_STARS: int = 10000
    MAX_BALLS_PER_PLAY: int = 10

    # Provably fair
    SERVER_SEED_LENGTH: int = 32

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

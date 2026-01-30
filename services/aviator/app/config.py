"""
Aviator game configuration settings.
"""
from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment."""

    # ============================================================
    # APPLICATION
    # ============================================================
    APP_NAME: str = "Aviator Crash Game"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    # ============================================================
    # DATABASE
    # ============================================================
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/aviator"
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10

    # ============================================================
    # REDIS
    # ============================================================
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_PUBSUB_CHANNEL: str = "aviator:game"

    # ============================================================
    # GAME SETTINGS
    # ============================================================
    # Betting limits (in TON)
    MIN_BET: float = 0.1
    MAX_BET: float = 100.0

    # Timing (in seconds)
    BETTING_PHASE_DURATION: int = 10
    MULTIPLIER_UPDATE_INTERVAL: float = 0.05  # 20 updates per second

    # Multiplier growth rate
    # Multiplier = 1.0 * e^(growth_rate * time_seconds)
    MULTIPLIER_GROWTH_RATE: float = 0.08  # ~2x at 8.6 seconds

    # House edge (1% = 0.99 multiplier on expected value)
    HOUSE_EDGE: float = 0.01

    # Server seed for provably fair generation (should be rotated periodically)
    SERVER_SEED: str = "aviator-secret-seed-change-in-production"

    # Maximum multiplier cap
    MAX_MULTIPLIER: float = 1000.0

    # ============================================================
    # WEBSOCKET
    # ============================================================
    WS_HEARTBEAT_INTERVAL: int = 30

    # ============================================================
    # API KEYS
    # ============================================================
    API_SECRET_KEY: str = "change-me-in-production"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()

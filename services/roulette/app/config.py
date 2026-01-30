"""
Roulette Service Configuration.

All settings are loaded from environment variables with sensible defaults.
"""
from functools import lru_cache
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment."""

    # ============================================================
    # APPLICATION
    # ============================================================
    APP_NAME: str = "Gift Roulette Service"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    # ============================================================
    # DATABASE
    # ============================================================
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/roulette"
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10

    # ============================================================
    # REDIS
    # ============================================================
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_CACHE_TTL: int = 300  # 5 minutes

    # ============================================================
    # ROULETTE SETTINGS
    # ============================================================
    # Classic roulette
    ROULETTE_NUMBERS: int = 37  # 0-36

    # Green numbers (0 in European, 0 and 00 in American)
    GREEN_NUMBERS: list[int] = [0]

    # Red numbers in European roulette
    RED_NUMBERS: list[int] = [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]

    # Black numbers (all others except green)
    BLACK_NUMBERS: list[int] = [2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35]

    # ============================================================
    # PAYOUT MULTIPLIERS
    # ============================================================
    PAYOUT_STRAIGHT: float = 35.0  # Single number
    PAYOUT_SPLIT: float = 17.0  # Two numbers
    PAYOUT_STREET: float = 11.0  # Three numbers (row)
    PAYOUT_CORNER: float = 8.0  # Four numbers
    PAYOUT_LINE: float = 5.0  # Six numbers (two rows)
    PAYOUT_COLUMN: float = 2.0  # 12 numbers (column)
    PAYOUT_DOZEN: float = 2.0  # 12 numbers (1-12, 13-24, 25-36)
    PAYOUT_RED_BLACK: float = 1.0  # Red or Black
    PAYOUT_ODD_EVEN: float = 1.0  # Odd or Even
    PAYOUT_HIGH_LOW: float = 1.0  # 1-18 or 19-36

    # ============================================================
    # GIFT ROULETTE SETTINGS
    # ============================================================
    GIFT_SPIN_COST_TON: float = 1.0  # Cost per spin in TON
    HOUSE_EDGE_PERCENT: float = 5.0  # House edge percentage

    # Minimum and maximum bets
    MIN_BET_TON: float = 0.1
    MAX_BET_TON: float = 100.0

    # Default TON prize amounts with probabilities (sum should be <= 100 minus gift probabilities)
    DEFAULT_TON_PRIZES: list[dict] = [
        {"amount": 0.5, "probability": 30.0},
        {"amount": 1.0, "probability": 20.0},
        {"amount": 5.0, "probability": 10.0},
        {"amount": 10.0, "probability": 5.0},
        {"amount": 50.0, "probability": 1.0},
        {"amount": 100.0, "probability": 0.1},
    ]

    # Probability of winning nothing (house wins)
    NO_WIN_PROBABILITY: float = 25.0  # Adjusted to fit house edge

    # ============================================================
    # PROVABLY FAIR
    # ============================================================
    SERVER_SEED_LENGTH: int = 32
    DEFAULT_CLIENT_SEED: str = "default_client_seed"

    # ============================================================
    # TON INTEGRATION
    # ============================================================
    TON_WALLET: Optional[str] = None  # Receiving wallet address
    TONAPI_KEY: Optional[str] = None
    TONAPI_BASE_URL: str = "https://tonapi.io"

    # ============================================================
    # WEBSOCKET
    # ============================================================
    WS_HEARTBEAT_INTERVAL: int = 30  # seconds
    WS_MAX_CONNECTIONS: int = 1000

    # ============================================================
    # RATE LIMITING
    # ============================================================
    RATE_LIMIT_SPINS_PER_MINUTE: int = 30
    RATE_LIMIT_ENABLED: bool = True

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()

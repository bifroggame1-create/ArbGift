"""
Trading Service Configuration.
"""
from decimal import Decimal
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Trading service settings."""

    APP_NAME: str = "Trading Service"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/trading"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/13"

    # Game Settings
    HOUSE_EDGE_PERCENT: Decimal = Decimal("3")  # 3% house edge
    MIN_BET_TON: Decimal = Decimal("0.1")
    MAX_BET_TON: Decimal = Decimal("100")
    GAME_INTERVAL_SECONDS: int = 10  # Time between games
    MAX_MULTIPLIER: Decimal = Decimal("10000")  # Max crash point

    # JWT
    JWT_SECRET_KEY: str = "change-me-in-production"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()

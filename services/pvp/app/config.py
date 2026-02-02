"""
PvP Service Configuration.
"""
from decimal import Decimal
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """PvP service settings."""

    APP_NAME: str = "PvP Gift Roulette"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/pvp"

    # Redis for real-time
    REDIS_URL: str = "redis://localhost:6379/11"

    # Game settings
    TICKET_VALUE_TON: Decimal = Decimal("0.01")  # 1 ticket = 0.01 TON
    HOUSE_FEE_PERCENT: Decimal = Decimal("5")  # 5% fee

    # Room settings
    MIN_PLAYERS: int = 2
    MAX_PLAYERS: int = 50
    COUNTDOWN_SECONDS: int = 30

    # Bet limits
    DEFAULT_MIN_BET_TON: Decimal = Decimal("1")
    DEFAULT_MAX_BET_TON: Decimal = Decimal("1000")

    # JWT for auth (from main app)
    JWT_SECRET_KEY: str = "change-me-in-production"

    # TON API for NFT data
    TONAPI_KEY: str = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()

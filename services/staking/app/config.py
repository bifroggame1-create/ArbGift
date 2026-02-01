"""
Staking Service Configuration.
"""
from decimal import Decimal
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Staking service settings."""

    APP_NAME: str = "Staking Service"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/staking"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/12"

    # APY Rates (annual percentage yield)
    APY_1_WEEK: Decimal = Decimal("5")
    APY_2_WEEKS: Decimal = Decimal("8")
    APY_1_MONTH: Decimal = Decimal("12")
    APY_3_MONTHS: Decimal = Decimal("20")

    # Limits
    MIN_STAKE_VALUE_TON: Decimal = Decimal("1")
    EARLY_WITHDRAWAL_PENALTY_PERCENT: Decimal = Decimal("10")

    # JWT
    JWT_SECRET_KEY: str = "change-me-in-production"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()

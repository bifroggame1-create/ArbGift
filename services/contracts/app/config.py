from decimal import Decimal
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configuration for Contracts Game Service"""

    # Application
    APP_NAME: str = "Contracts Game"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/contracts"
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10

    # Redis (optional, for caching/sessions)
    REDIS_URL: str = "redis://localhost:6379/6"

    # Risk multipliers (configured but sourced from probability engine)
    SAFE_MULTIPLIER: Decimal = Decimal("2.0")
    NORMAL_MULTIPLIER: Decimal = Decimal("8.0")
    RISKY_MULTIPLIER: Decimal = Decimal("100.0")

    # Limits
    MIN_GIFTS: int = 2
    MAX_GIFTS: int = 10
    MIN_VALUE_SAFE: Decimal = Decimal("1.0")
    MIN_VALUE_NORMAL: Decimal = Decimal("5.0")
    MIN_VALUE_RISKY: Decimal = Decimal("20.0")

    # House edge
    HOUSE_EDGE: Decimal = Decimal("0.05")

    # Server seed entropy (for provably fair)
    SERVER_SEED_LENGTH: int = 128  # hex characters

    # CORS
    CORS_ORIGINS: list = ["*"]

    # JWT/Auth (if using separate auth service)
    JWT_SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

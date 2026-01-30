from decimal import Decimal
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configuration for Upgrade Game Service"""

    # Application
    APP_NAME: str = "Upgrade Game"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/upgrade"
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10

    # Redis (optional)
    REDIS_URL: str = "redis://localhost:6379/7"

    # Probability settings
    BASE_SUCCESS_RATE: Decimal = Decimal("0.50")  # 50% for equal values
    MIN_PROBABILITY: Decimal = Decimal("0.01")  # 1%
    MAX_PROBABILITY: Decimal = Decimal("0.95")  # 95%

    # Server seed
    SERVER_SEED_LENGTH: int = 128

    # Wheel animation
    ANIMATION_DURATION_MS: int = 3000  # 3 seconds

    # CORS
    CORS_ORIGINS: list = ["*"]

    # JWT/Auth
    JWT_SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

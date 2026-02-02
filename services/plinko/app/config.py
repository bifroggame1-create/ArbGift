"""
Plinko Service Configuration.
"""
from functools import lru_cache
from typing import Optional, List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    APP_NAME: str = "Plinko Game Service"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/plinko"
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Game settings
    MIN_BET_TON: float = 0.1
    MAX_BET_TON: float = 100.0
    
    # Multipliers for each slot (9 slots, 0-8)
    MULTIPLIERS: List[float] = [0.0, 0.0, 2.0, 0.7, 0.6, 0.7, 2.0, 0.0, 0.0]
    
    # Provably fair
    SERVER_SEED_LENGTH: int = 32
    
    # TON Integration
    TON_WALLET: Optional[str] = None
    TONAPI_KEY: Optional[str] = None
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

"""
Application configuration from environment variables.
All settings are validated at startup.
"""
from functools import lru_cache
from typing import Optional, Dict
from pydantic_settings import BaseSettings


# ============================================================
# PLINKO GAME CONFIGURATION
# ============================================================

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
    """Application settings loaded from environment."""

    # ============================================================
    # APPLICATION
    # ============================================================
    APP_NAME: str = "TON Gift Aggregator"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    # ============================================================
    # CORS
    # ============================================================
    ALLOWED_ORIGINS: str = "https://arb-gift-test.vercel.app,https://localhost:3000,http://localhost:3000,http://localhost:5173"

    # ============================================================
    # ADMIN
    # ============================================================
    ADMIN_SECRET_KEY: str = ""

    # ============================================================
    # DATABASE
    # ============================================================
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/ton_gifts"

    @property
    def database_url_async(self) -> str:
        """Convert DATABASE_URL to asyncpg format (Render gives postgres://)."""
        url = self.DATABASE_URL
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+asyncpg://", 1)
        elif url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return url
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10

    # ============================================================
    # REDIS
    # ============================================================
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_CACHE_TTL: int = 300  # 5 minutes default

    # ============================================================
    # CELERY
    # ============================================================
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    # ============================================================
    # MEILISEARCH
    # ============================================================
    MEILISEARCH_URL: str = "http://localhost:7700"
    MEILISEARCH_API_KEY: Optional[str] = None
    MEILISEARCH_INDEX_GIFTS: str = "gifts"

    # ============================================================
    # TON API (tonapi.io)
    # ============================================================
    TONAPI_BASE_URL: str = "https://tonapi.io"
    TONAPI_KEY: Optional[str] = None  # Optional but recommended
    TONAPI_RATE_LIMIT: float = 5.0  # requests per second
    TONAPI_TIMEOUT: int = 30

    # ============================================================
    # TON CENTER (fallback/alternative)
    # ============================================================
    TONCENTER_BASE_URL: str = "https://toncenter.com/api/v2"
    TONCENTER_API_KEY: Optional[str] = None

    # ============================================================
    # IPFS GATEWAYS (ordered by priority)
    # ============================================================
    IPFS_GATEWAYS: list[str] = [
        "https://cloudflare-ipfs.com/ipfs/",
        "https://ipfs.io/ipfs/",
        "https://gateway.pinata.cloud/ipfs/",
        "https://dweb.link/ipfs/",
    ]
    IPFS_TIMEOUT: int = 15

    # ============================================================
    # CDN (for processed images)
    # ============================================================
    CDN_ENABLED: bool = False
    CDN_BUCKET_URL: Optional[str] = None  # S3/R2/etc
    CDN_ACCESS_KEY: Optional[str] = None
    CDN_SECRET_KEY: Optional[str] = None

    # ============================================================
    # TELEGRAM MTPROTO (Telethon)
    # ============================================================
    TELEGRAM_API_ID: int = 0  # Required from .env
    TELEGRAM_API_HASH: str = ""  # Required from .env
    TELEGRAM_SESSION_NAME: str = "gift_indexer"
    TELEGRAM_SYNC_DELAY: float = 0.5  # Delay between API calls (seconds)

    # ============================================================
    # TELEGRAM BOT (for WebApp authentication)
    # ============================================================
    TELEGRAM_BOT_TOKEN: str = ""  # Required from .env for initData verification

    # ============================================================
    # MARKET ADAPTERS
    # ============================================================
    # GetGems
    GETGEMS_GRAPHQL_URL: str = "https://api.getgems.io/graphql"
    GETGEMS_RATE_LIMIT: float = 3.0

    # MRKT
    MRKT_API_URL: str = "https://api.tgmrkt.io/api/v1"
    MRKT_INIT_DATA: Optional[str] = None  # Telegram initData for authentication
    MRKT_RATE_LIMIT: float = 3.0

    # Fragment (uses TON API)
    FRAGMENT_COLLECTION: str = "EQD-BJSVUJviud_Qv7Ymfd3qzXdrmV525e3YDzWQoHIAiInL"

    # ============================================================
    # KNOWN TELEGRAM GIFT COLLECTIONS
    # ============================================================
    TELEGRAM_GIFT_COLLECTIONS: list[str] = [
        "EQBTKUGf_2wz0mVji52re8oWcDZYUbCm2tAjAWYCODc2u5TP",  # GetGems Gifts
        "EQD-BJSVUJviud_Qv7Ymfd3qzXdrmV525e3YDzWQoHIAiInL",  # Fragment Gifts
    ]

    # ============================================================
    # SYNC SETTINGS
    # ============================================================
    SYNC_ON_STARTUP: bool = True  # Синхронизировать данные при старте
    SYNC_INTERVAL_LISTINGS: int = 60  # seconds
    SYNC_INTERVAL_METADATA: int = 3600  # 1 hour
    SYNC_BATCH_SIZE: int = 100
    SYNC_MAX_ITEMS_PORTALS: int = 500  # Макс. записей с Portals.tg
    SYNC_MAX_ITEMS_MAJOR: int = 500  # Макс. записей с Major.tg

    # ============================================================
    # FX RATES
    # ============================================================
    STARS_TO_TON_RATE: float = 0.013  # 1 STAR = 0.013 TON (default, updated dynamically)
    GAS_FEE_TON: float = 0.05  # Estimated gas fee

    # ============================================================
    # MICROSERVICES
    # ============================================================
    PLINKO_SERVICE_URL: str = "http://localhost:8001"
    SOLO_GAMES_SERVICE_URL: str = "http://localhost:8002"
    TRADING_SERVICE_URL: str = "http://localhost:8003"
    PVP_SERVICE_URL: str = "http://localhost:8004"
    INTERNAL_API_KEY: str = ""
    # Internal auth for game services
    INTERNAL_API_HEADER: str = "X-Internal-Key"
    MAIN_API_URL: str = "http://localhost:8000"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()

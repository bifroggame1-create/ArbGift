"""
Configuration settings for the Telegram Stars purchase service.
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
from decimal import Decimal


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    APP_NAME: str = "Telegram Stars Purchase Service"
    DEBUG: bool = False
    API_PREFIX: str = "/api/v1"

    # Telegram Bot Configuration
    BOT_TOKEN: str = Field(..., description="Telegram Bot API token from @BotFather")
    PAYMENT_PROVIDER_TOKEN: str = Field(
        default="",
        description="Payment provider token (empty for Telegram Stars)"
    )

    # TON Configuration
    TON_WALLET: str = Field(..., description="TON wallet address for receiving payments")
    TON_API_KEY: str = Field(..., description="API key from tonapi.io")
    TON_API_URL: str = "https://tonapi.io/v2"
    TON_TESTNET: bool = False

    # Pricing Configuration
    STARS_TO_USD: Decimal = Field(
        default=Decimal("0.013"),
        description="USD value per Telegram Star"
    )
    TON_TO_USD: Decimal = Field(
        default=Decimal("5.0"),
        description="Current TON to USD rate (updated dynamically)"
    )
    MARGIN: Decimal = Field(
        default=Decimal("0.05"),
        description="Profit margin (5%)"
    )

    # Star Packages
    STAR_PACKAGES: list[int] = [50, 100, 500, 1000]

    # Database
    DATABASE_URL: str = Field(
        default="sqlite+aiosqlite:///./stars_service.db",
        description="Database connection URL"
    )

    # Redis (for caching and rate limiting)
    REDIS_URL: Optional[str] = Field(
        default=None,
        description="Redis connection URL"
    )

    # Security
    SECRET_KEY: str = Field(
        default="your-secret-key-change-in-production",
        description="Secret key for signing tokens"
    )
    WEBHOOK_SECRET: Optional[str] = Field(
        default=None,
        description="Telegram webhook secret for verification"
    )

    # Payment Settings
    PAYMENT_TIMEOUT_MINUTES: int = 30
    MIN_CONFIRMATIONS: int = 1

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()

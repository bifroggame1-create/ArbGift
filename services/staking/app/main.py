"""
Staking Service - Main Entry Point.

Стейкинг NFT гифтов для получения наград.
"""
import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from app.core.ratelimit import limiter

from app.api.stakes import router as stakes_router
from app.config import settings
from app.database import init_db

# Logging
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    logger.info("Starting Staking service...")
    logger.info("Initializing database...")
    await init_db()
    logger.info("Database initialized")
    yield
    logger.info("Shutting down Staking service...")


# Create app
app = FastAPI(
    title="Gift Staking",
    description="Стейкинг NFT гифтов для получения наград",
    version="1.0.0",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# CORS
allowed_origins = [o.strip() for o in os.getenv("ALLOWED_ORIGINS", "").split(",") if o.strip()] or (["*"] if settings.DEBUG else [])
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(stakes_router)


@app.get("/health")
async def health_check():
    """Health check."""
    return {"status": "healthy", "service": "staking"}


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "Gift Staking",
        "version": "1.0.0",
        "docs": "/docs",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

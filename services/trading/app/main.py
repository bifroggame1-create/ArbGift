"""
Trading Service - Main Entry Point.

Crash/Trading game with provably fair mechanics.
"""
import logging
import os
from contextlib import asynccontextmanager
import asyncio

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from app.core.auth import require_internal_key
from app.core.ratelimit import limiter

from app.api import trading
from app.config import settings
from app.database import init_db
from app.services.game_loop import GameLoop

# Logging
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Global game loop instance
game_loop: GameLoop = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    global game_loop

    logger.info("Starting Trading service...")

    # Initialize database
    logger.info("Initializing database...")
    await init_db()
    logger.info("Database initialized")

    # Start game loop
    from app.database import get_db_session
    game_loop = GameLoop(get_db_session)
    asyncio.create_task(game_loop.start())
    logger.info("Game loop started")

    yield

    # Shutdown
    logger.info("Shutting down Trading service...")
    if game_loop:
        await game_loop.stop()
    logger.info("Trading service stopped")


app = FastAPI(
    title="Trading Game Service",
    description="Crash/Trading game with provably fair mechanics",
    version="1.0.0",
    lifespan=lifespan,
)

# Rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# CORS
allowed_origins_env = os.getenv("ALLOWED_ORIGINS", "")
allowed_origins = [o.strip() for o in allowed_origins_env.split(",") if o.strip()] or (["*"] if settings.DEBUG else [])
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(trading.router)


@app.get("/health")
async def health_check():
    """Health check."""
    return {"status": "healthy", "service": "trading"}


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "Trading Game",
        "version": "1.0.0",
        "docs": "/docs",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

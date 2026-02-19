"""
PvP Service — рулетка на гифтах (Rolls.codes).

PostgreSQL + WebSocket + Provably Fair.
"""
import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.api.rooms import router as rooms_router
from app.api.inventory import router as inventory_router
from app.api.websocket import router as ws_router
from app.config import settings
from app.database import init_db
from app.services.game_scheduler import game_scheduler
from app.core.ratelimit import limiter

logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown."""
    logger.info("Starting PvP service...")
    await init_db()
    logger.info("Database initialized")
    await game_scheduler.start()
    logger.info("Game scheduler started")
    yield
    await game_scheduler.stop()
    logger.info("PvP service stopped")


app = FastAPI(
    title="PvP Gift Roulette",
    description="Provably Fair PvP рулетка на Telegram гифтах",
    version="2.0.0",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in os.getenv("ALLOWED_ORIGINS", "").split(",") if o.strip()] or (["*"] if settings.DEBUG else []),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(rooms_router)
app.include_router(inventory_router)
app.include_router(ws_router)


@app.get("/health")
async def health_check():
    from app.services.websocket_manager import ws_manager
    return {
        "status": "healthy",
        "service": "pvp",
        "version": "2.0.0",
        "ws_connections": ws_manager.get_total_connections(),
    }


@app.get("/")
async def root():
    return {
        "service": "PvP Gift Roulette",
        "version": "2.0.0",
        "docs": "/docs",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8009)

"""
PvP Service - Main Entry Point.

Рулетка на гифтах по образцу Rolls.codes.
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.rooms import router as rooms_router
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
    logger.info("Starting PvP service...")
    await init_db()
    logger.info("Database initialized")
    yield
    logger.info("Shutting down PvP service...")


# Create app
app = FastAPI(
    title="PvP Gift Roulette",
    description="Provably Fair PvP рулетка на Telegram гифтах",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(rooms_router)


@app.get("/health")
async def health_check():
    """Health check."""
    return {"status": "healthy", "service": "pvp"}


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "PvP Gift Roulette",
        "version": "1.0.0",
        "docs": "/docs",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

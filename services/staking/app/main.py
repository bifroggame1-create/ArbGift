"""
Staking Service - Main Entry Point.

Стейкинг NFT гифтов для получения наград.
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.stakes import router as stakes_router
from app.config import settings

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
    yield
    logger.info("Shutting down Staking service...")


# Create app
app = FastAPI(
    title="Gift Staking",
    description="Стейкинг NFT гифтов для получения наград",
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

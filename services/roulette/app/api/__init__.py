"""API routers for the roulette service."""
from app.api.spins import router as spins_router
from app.api.prizes import router as prizes_router
from app.api.ws import router as ws_router

__all__ = ["spins_router", "prizes_router", "ws_router"]

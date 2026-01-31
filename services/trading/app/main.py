from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio

from .api import trading
from .services.game_loop import GameLoop, game_loop as global_game_loop
from .database import engine, get_db
from .models.game import Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Start game loop
    global game_loop
    game_loop = GameLoop(get_db)
    asyncio.create_task(game_loop.start())

    yield

    # Shutdown
    if game_loop:
        await game_loop.stop()


app = FastAPI(title="Trading Game Service", lifespan=lifespan)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(trading.router)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "trading"}

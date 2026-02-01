"""
TON Gift Aggregator - FastAPI Application

Main entry point for the REST API.
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.core.database import init_db, close_db
from app.api.v1.gifts import router as gifts_router

# Optional dependencies: search (Meilisearch) and websocket (Redis)
try:
    from app.api.v1.search import router as search_router
except Exception:
    search_router = None
    logging.getLogger(__name__).warning("Search router unavailable (Meilisearch not configured)")

try:
    from app.api.websocket import router as websocket_router
except Exception:
    websocket_router = None
    logging.getLogger(__name__).warning("WebSocket router unavailable (Redis not configured)")

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting TON Gift Aggregator API...")
    await init_db()
    logger.info("Database initialized")

    # Запускаем синхронизацию данных при старте (если включено)
    if settings.SYNC_ON_STARTUP:
        logger.info("Starting data sync from markets...")
        try:
            from app.sync import run_sync
            stats = await run_sync()
            logger.info(f"Sync completed: {stats.get('total', 0)} items loaded")
        except Exception as e:
            logger.error(f"Sync failed: {e}")
            # Не падаем, продолжаем работу

    yield

    # Shutdown
    logger.info("Shutting down...")
    try:
        from app.sync import get_loader
        loader = await get_loader()
        await loader.close()
    except Exception:
        pass
    await close_db()
    logger.info("Shutdown complete")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
    TON Gift Aggregator API

    Aggregates NFT gift listings from multiple TON marketplaces:
    - GetGems
    - Fragment
    - PawnStars
    - And more...

    Features:
    - Unified gift listings
    - Price comparison across markets
    - Search and filters
    - Real-time updates via WebSocket
    """,
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
    }


# API info
@app.get("/")
async def root():
    """API root - returns basic info."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs" if settings.DEBUG else None,
    }


# Include routers
app.include_router(
    gifts_router,
    prefix="/api/v1",
    tags=["Gifts"],
)

if search_router:
    app.include_router(
        search_router,
        prefix="/api/v1",
        tags=["Search"],
    )

if websocket_router:
    app.include_router(
        websocket_router,
        prefix="/ws",
        tags=["WebSocket"],
    )


# Markets endpoint
@app.get("/api/v1/markets", tags=["Markets"])
async def list_markets():
    """List all supported markets."""
    from app.core.database import get_async_session
    from app.models.market import Market
    from sqlalchemy import select

    async with get_async_session() as session:
        result = await session.execute(
            select(Market).order_by(Market.priority.desc())
        )
        markets = result.scalars().all()

        return {
            "total": len(markets),
            "markets": [
                {
                    "id": m.id,
                    "slug": m.slug,
                    "name": m.name,
                    "website_url": m.website_url,
                    "fee_buy_percent": m.fee_buy_percent,
                    "fee_sell_percent": m.fee_sell_percent,
                    "is_active": m.is_active,
                }
                for m in markets
            ],
        }


# Stats endpoint
@app.get("/api/v1/stats", tags=["Stats"])
async def get_stats():
    """Get platform statistics."""
    from app.core.database import get_async_session
    from app.models.collection import Collection
    from app.models.nft import NFT
    from app.models.listing import Listing
    from sqlalchemy import select, func

    async with get_async_session() as session:
        # Total collections
        collections_count = await session.execute(
            select(func.count(Collection.id))
        )
        total_collections = collections_count.scalar() or 0

        # Total NFTs
        nfts_count = await session.execute(
            select(func.count(NFT.id))
        )
        total_nfts = nfts_count.scalar() or 0

        # NFTs on sale
        on_sale_count = await session.execute(
            select(func.count(NFT.id)).where(NFT.is_on_sale == True)
        )
        total_on_sale = on_sale_count.scalar() or 0

        # Active listings
        listings_count = await session.execute(
            select(func.count(Listing.id)).where(Listing.is_active == True)
        )
        total_listings = listings_count.scalar() or 0

        return {
            "total_collections": total_collections,
            "total_gifts": total_nfts,
            "gifts_on_sale": total_on_sale,
            "total_listings": total_listings,
        }


# =====================================
# SYNC ENDPOINTS (БЕЗ CELERY)
# =====================================

@app.post("/api/v1/admin/sync", tags=["Admin"])
async def sync_all_markets():
    """
    Синхронизировать данные со всех маркетов.

    Запускает синхронный загрузчик (без Celery).
    Загружает данные с Portals.tg и Major.tg.
    """
    from app.sync import run_sync
    try:
        stats = await run_sync()
        return {
            "status": "completed",
            "stats": stats,
        }
    except Exception as e:
        logger.error(f"Sync error: {e}", exc_info=True)
        return JSONResponse(status_code=500, content={"detail": str(e)})


@app.post("/api/v1/admin/sync/portals", tags=["Admin"])
async def sync_portals_market(max_items: int = 500):
    """Синхронизировать только Portals.tg."""
    from app.sync import get_loader
    try:
        loader = await get_loader()
        count = await loader.sync_portals_listings(max_items)
        return {
            "status": "completed",
            "market": "portals",
            "synced": count,
        }
    except Exception as e:
        logger.error(f"Portals sync error: {e}", exc_info=True)
        return JSONResponse(status_code=500, content={"detail": str(e)})


@app.post("/api/v1/admin/sync/major", tags=["Admin"])
async def sync_major_market(max_items: int = 500):
    """Синхронизировать только Major.tg."""
    from app.sync import get_loader
    try:
        loader = await get_loader()
        count = await loader.sync_major_listings(max_items)
        return {
            "status": "completed",
            "market": "major",
            "synced": count,
        }
    except Exception as e:
        logger.error(f"Major sync error: {e}", exc_info=True)
        return JSONResponse(status_code=500, content={"detail": str(e)})


# =====================================
# LEGACY CELERY ENDPOINTS (deprecated)
# =====================================

@app.post("/api/v1/admin/index-collection", tags=["Admin"], deprecated=True)
async def trigger_index_collection(collection_address: str):
    """[DEPRECATED] Trigger collection indexing (requires Celery/Redis)."""
    try:
        from app.workers.tasks.index_collection import index_collection
        task = index_collection.delay(collection_address)
        return {
            "task_id": task.id,
            "status": "queued",
            "collection_address": collection_address,
        }
    except Exception as e:
        return JSONResponse(status_code=503, content={"detail": f"Celery unavailable: {e}"})


@app.post("/api/v1/admin/sync-listings", tags=["Admin"], deprecated=True)
async def trigger_sync_listings(market_slug: str = None):
    """[DEPRECATED] Trigger listings sync (requires Celery/Redis)."""
    try:
        if market_slug:
            from app.workers.tasks.sync_listings import sync_single_market
            task = sync_single_market.delay(market_slug)
        else:
            from app.workers.tasks.sync_listings import sync_all_listings
            task = sync_all_listings.delay()
        return {
            "task_id": task.id,
            "status": "queued",
            "market": market_slug or "all",
        }
    except Exception as e:
        return JSONResponse(status_code=503, content={"detail": f"Celery unavailable: {e}"})


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
    )

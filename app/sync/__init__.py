"""
Синхронные загрузчики данных (без Celery).
"""
from app.sync.data_loader import (
    SyncDataLoader,
    PortalsMarketLoader,
    MajorMarketLoader,
    get_loader,
    run_sync,
)

__all__ = [
    "SyncDataLoader",
    "PortalsMarketLoader",
    "MajorMarketLoader",
    "get_loader",
    "run_sync",
]

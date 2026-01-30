"""
Celery application configuration.

Defines the Celery app and its configuration for background task processing.
"""
from celery import Celery
from celery.schedules import crontab

from app.config import settings

# Create Celery app
celery_app = Celery(
    "ton_gift_aggregator",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.workers.tasks.index_collection",
        "app.workers.tasks.sync_listings",
        "app.workers.tasks.resolve_metadata",
        "app.workers.tasks.update_prices",
    ],
)

# Celery configuration
celery_app.conf.update(
    # Task settings
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,

    # Task execution settings
    task_acks_late=True,  # Ack after task completion
    task_reject_on_worker_lost=True,
    task_time_limit=3600,  # 1 hour max
    task_soft_time_limit=3000,  # 50 minutes soft limit

    # Worker settings
    worker_prefetch_multiplier=1,  # One task at a time per worker
    worker_concurrency=4,  # Number of worker processes

    # Result backend settings
    result_expires=86400,  # Results expire after 1 day

    # Rate limiting
    task_default_rate_limit="10/m",  # 10 tasks per minute default

    # Retry settings
    task_default_retry_delay=60,
    task_max_retries=3,

    # Logging
    worker_hijack_root_logger=False,
)

# Beat schedule for periodic tasks
celery_app.conf.beat_schedule = {
    # Sync listings every minute
    "sync-listings-every-minute": {
        "task": "app.workers.tasks.sync_listings.sync_all_listings",
        "schedule": 60.0,  # Every 60 seconds
        "options": {"queue": "sync"},
    },

    # Update FX rates every 5 minutes
    "update-fx-rates": {
        "task": "app.workers.tasks.update_prices.update_fx_rates",
        "schedule": 300.0,  # Every 5 minutes
        "options": {"queue": "default"},
    },

    # Reindex collection metadata hourly
    "reindex-metadata-hourly": {
        "task": "app.workers.tasks.resolve_metadata.batch_resolve_metadata",
        "schedule": crontab(minute=0),  # Every hour at :00
        "options": {"queue": "metadata"},
    },

    # Update collection stats every 10 minutes
    "update-collection-stats": {
        "task": "app.workers.tasks.update_prices.update_collection_stats",
        "schedule": 600.0,  # Every 10 minutes
        "options": {"queue": "default"},
    },

    # Clean up stale listings daily
    "cleanup-stale-listings": {
        "task": "app.workers.tasks.sync_listings.cleanup_stale_listings",
        "schedule": crontab(hour=4, minute=0),  # Daily at 4 AM
        "options": {"queue": "maintenance"},
    },
}

# Task routing
celery_app.conf.task_routes = {
    "app.workers.tasks.index_collection.*": {"queue": "indexer"},
    "app.workers.tasks.sync_listings.*": {"queue": "sync"},
    "app.workers.tasks.resolve_metadata.*": {"queue": "metadata"},
    "app.workers.tasks.update_prices.*": {"queue": "default"},
}

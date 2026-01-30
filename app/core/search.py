"""
Meilisearch client configuration and index management.

Provides a configured Meilisearch client for full-text search functionality
with automatic index initialization and settings configuration.
"""
import logging
from typing import Optional

import meilisearch
from meilisearch.errors import MeilisearchApiError
from meilisearch.index import Index

from app.config import settings

logger = logging.getLogger(__name__)

# Index configuration
GIFTS_INDEX_SETTINGS = {
    "searchableAttributes": [
        "name",
        "description",
        "collection_name",
        "rarity",
        "backdrop",
        "model",
    ],
    "filterableAttributes": [
        "collection_id",
        "rarity",
        "is_on_sale",
        "price_ton",
        "backdrop",
        "model",
    ],
    "sortableAttributes": [
        "price_ton",
        "name",
        "updated_at",
    ],
    "rankingRules": [
        "words",
        "typo",
        "proximity",
        "attribute",
        "sort",
        "exactness",
    ],
    "distinctAttribute": None,
    "typoTolerance": {
        "enabled": True,
        "minWordSizeForTypos": {
            "oneTypo": 4,
            "twoTypos": 8,
        },
    },
    "faceting": {
        "maxValuesPerFacet": 100,
    },
    "pagination": {
        "maxTotalHits": 10000,
    },
}


class MeilisearchClient:
    """
    Meilisearch client wrapper with automatic index initialization.

    Handles connection management, index creation, and settings configuration.
    Thread-safe singleton pattern for efficient resource usage.
    """

    _instance: Optional["MeilisearchClient"] = None
    _client: Optional[meilisearch.Client] = None
    _initialized: bool = False

    def __new__(cls) -> "MeilisearchClient":
        """Singleton pattern to reuse client connection."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize Meilisearch client if not already done."""
        if self._client is None:
            self._client = meilisearch.Client(
                settings.MEILISEARCH_URL,
                settings.MEILISEARCH_API_KEY,
            )
            logger.info(
                f"Meilisearch client initialized: {settings.MEILISEARCH_URL}"
            )

    @property
    def client(self) -> meilisearch.Client:
        """Get the underlying Meilisearch client."""
        return self._client

    def health_check(self) -> bool:
        """
        Check if Meilisearch is healthy and reachable.

        Returns:
            True if healthy, False otherwise.
        """
        try:
            health = self._client.health()
            return health.get("status") == "available"
        except Exception as e:
            logger.error(f"Meilisearch health check failed: {e}")
            return False

    def get_gifts_index(self) -> Index:
        """
        Get the gifts index, creating it if necessary.

        Returns:
            Configured gifts index.
        """
        index_name = settings.MEILISEARCH_INDEX_GIFTS
        return self._client.index(index_name)

    def initialize_indexes(self) -> None:
        """
        Initialize all search indexes with proper settings.

        Creates indexes if they don't exist and updates settings.
        Should be called on application startup.
        """
        if self._initialized:
            logger.debug("Indexes already initialized, skipping")
            return

        self._initialize_gifts_index()
        self._initialized = True
        logger.info("Meilisearch indexes initialized")

    def _initialize_gifts_index(self) -> None:
        """Initialize the gifts index with configured settings."""
        index_name = settings.MEILISEARCH_INDEX_GIFTS

        try:
            # Create index if it doesn't exist
            try:
                self._client.create_index(
                    index_name,
                    {"primaryKey": "id"},
                )
                logger.info(f"Created Meilisearch index: {index_name}")
            except MeilisearchApiError as e:
                if "index_already_exists" not in str(e):
                    raise
                logger.debug(f"Index {index_name} already exists")

            # Update index settings
            index = self._client.index(index_name)
            task = index.update_settings(GIFTS_INDEX_SETTINGS)

            # Wait for settings update to complete
            self._client.wait_for_task(task.task_uid, timeout_in_ms=30000)
            logger.info(f"Updated settings for index: {index_name}")

        except Exception as e:
            logger.error(f"Failed to initialize gifts index: {e}")
            raise

    def reset_gifts_index(self) -> None:
        """
        Delete and recreate the gifts index.

        Warning: This will delete all indexed documents.
        Use only for reindexing operations.
        """
        index_name = settings.MEILISEARCH_INDEX_GIFTS

        try:
            # Delete existing index
            try:
                task = self._client.delete_index(index_name)
                self._client.wait_for_task(task.task_uid, timeout_in_ms=30000)
                logger.info(f"Deleted index: {index_name}")
            except MeilisearchApiError as e:
                if "index_not_found" not in str(e):
                    raise

            # Recreate index
            self._initialized = False
            self._initialize_gifts_index()

        except Exception as e:
            logger.error(f"Failed to reset gifts index: {e}")
            raise

    def get_index_stats(self) -> dict:
        """
        Get statistics for the gifts index.

        Returns:
            Dictionary with index statistics.
        """
        try:
            index = self.get_gifts_index()
            stats = index.get_stats()
            return {
                "number_of_documents": stats.number_of_documents,
                "is_indexing": stats.is_indexing,
                "field_distribution": stats.field_distribution,
            }
        except Exception as e:
            logger.error(f"Failed to get index stats: {e}")
            return {"error": str(e)}


# Global client instance
_search_client: Optional[MeilisearchClient] = None


def get_search_client() -> MeilisearchClient:
    """
    Get the global Meilisearch client instance.

    Returns:
        Configured MeilisearchClient instance.
    """
    global _search_client
    if _search_client is None:
        _search_client = MeilisearchClient()
    return _search_client


async def init_search() -> None:
    """
    Initialize search on application startup.

    Creates indexes and configures settings.
    """
    client = get_search_client()

    if not client.health_check():
        logger.warning(
            "Meilisearch is not available. Search functionality will be limited."
        )
        return

    client.initialize_indexes()
    logger.info("Search initialization complete")


async def close_search() -> None:
    """
    Cleanup search resources on application shutdown.

    Currently a no-op as Meilisearch client doesn't need explicit cleanup,
    but included for consistency with other resources.
    """
    logger.info("Search resources cleaned up")

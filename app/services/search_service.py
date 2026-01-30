"""
Search service for gift indexing and retrieval.

Provides high-level operations for indexing gifts in Meilisearch
and searching with filters, pagination, and facets.
"""
import logging
from datetime import datetime
from decimal import Decimal
from typing import Optional, List, Dict, Any, Union

from meilisearch.errors import MeilisearchApiError

from app.core.search import get_search_client
from app.config import settings

logger = logging.getLogger(__name__)


class SearchService:
    """
    Service for gift search operations.

    Handles indexing, removal, and search with support for
    filters, sorting, pagination, and faceted search.
    """

    def __init__(self):
        """Initialize search service with Meilisearch client."""
        self._client = get_search_client()

    @staticmethod
    def _serialize_document(gift_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Serialize gift data for Meilisearch indexing.

        Converts Decimal and datetime types to JSON-compatible formats.

        Args:
            gift_data: Raw gift document data.

        Returns:
            Serialized document ready for indexing.
        """
        doc = {}
        for key, value in gift_data.items():
            if isinstance(value, Decimal):
                doc[key] = float(value)
            elif isinstance(value, datetime):
                doc[key] = int(value.timestamp())
            elif value is None:
                # Keep None values as they are filterable
                doc[key] = value
            else:
                doc[key] = value
        return doc

    def index_gift(
        self,
        gift_id: int,
        address: str,
        name: str,
        description: Optional[str],
        collection_id: int,
        collection_name: str,
        rarity: Optional[str],
        backdrop: Optional[str],
        model: Optional[str],
        is_on_sale: bool,
        price_ton: Optional[Union[Decimal, float]],
        image_url: Optional[str],
        updated_at: Optional[datetime] = None,
    ) -> str:
        """
        Add or update a single gift in the search index.

        Args:
            gift_id: Unique gift identifier (primary key).
            address: TON blockchain address.
            name: Gift name.
            description: Gift description.
            collection_id: Parent collection ID.
            collection_name: Parent collection name.
            rarity: Rarity attribute (common, uncommon, rare, etc.).
            backdrop: Backdrop attribute.
            model: Model attribute.
            is_on_sale: Whether the gift is currently listed for sale.
            price_ton: Price in TON (None if not on sale).
            image_url: URL to gift image.
            updated_at: Last update timestamp.

        Returns:
            Task UID for tracking indexing status.
        """
        document = self._serialize_document({
            "id": gift_id,
            "address": address,
            "name": name,
            "description": description,
            "collection_id": collection_id,
            "collection_name": collection_name,
            "rarity": rarity,
            "backdrop": backdrop,
            "model": model,
            "is_on_sale": is_on_sale,
            "price_ton": price_ton,
            "image_url": image_url,
            "updated_at": updated_at or datetime.utcnow(),
        })

        try:
            index = self._client.get_gifts_index()
            task = index.add_documents([document])
            logger.debug(f"Indexed gift {gift_id}: task {task.task_uid}")
            return task.task_uid
        except MeilisearchApiError as e:
            logger.error(f"Failed to index gift {gift_id}: {e}")
            raise

    def index_gifts_batch(
        self,
        gifts: List[Dict[str, Any]],
        wait_for_completion: bool = False,
        batch_size: int = 1000,
    ) -> List[str]:
        """
        Bulk index multiple gifts.

        Efficiently indexes gifts in batches for large-scale operations.

        Args:
            gifts: List of gift documents with required fields:
                - id: int
                - address: str
                - name: str
                - description: Optional[str]
                - collection_id: int
                - collection_name: str
                - rarity: Optional[str]
                - backdrop: Optional[str]
                - model: Optional[str]
                - is_on_sale: bool
                - price_ton: Optional[float]
                - image_url: Optional[str]
                - updated_at: Optional[datetime]
            wait_for_completion: Whether to wait for indexing to complete.
            batch_size: Number of documents per batch.

        Returns:
            List of task UIDs for tracking.
        """
        if not gifts:
            logger.debug("No gifts to index")
            return []

        # Serialize all documents
        documents = [self._serialize_document(gift) for gift in gifts]

        index = self._client.get_gifts_index()
        task_uids = []

        # Process in batches
        for i in range(0, len(documents), batch_size):
            batch = documents[i:i + batch_size]
            try:
                task = index.add_documents(batch)
                task_uids.append(task.task_uid)
                logger.info(
                    f"Indexed batch {i // batch_size + 1}: "
                    f"{len(batch)} documents, task {task.task_uid}"
                )
            except MeilisearchApiError as e:
                logger.error(f"Failed to index batch starting at {i}: {e}")
                raise

        # Optionally wait for all tasks to complete
        if wait_for_completion and task_uids:
            for uid in task_uids:
                try:
                    self._client.client.wait_for_task(
                        uid,
                        timeout_in_ms=60000,
                    )
                except Exception as e:
                    logger.warning(f"Task {uid} may not have completed: {e}")

        logger.info(f"Batch indexing complete: {len(documents)} total documents")
        return task_uids

    def remove_gift(self, gift_id: int) -> str:
        """
        Remove a gift from the search index.

        Args:
            gift_id: ID of the gift to remove.

        Returns:
            Task UID for tracking.
        """
        try:
            index = self._client.get_gifts_index()
            task = index.delete_document(gift_id)
            logger.debug(f"Removed gift {gift_id}: task {task.task_uid}")
            return task.task_uid
        except MeilisearchApiError as e:
            logger.error(f"Failed to remove gift {gift_id}: {e}")
            raise

    def remove_gifts_batch(self, gift_ids: List[int]) -> str:
        """
        Remove multiple gifts from the search index.

        Args:
            gift_ids: List of gift IDs to remove.

        Returns:
            Task UID for tracking.
        """
        if not gift_ids:
            return ""

        try:
            index = self._client.get_gifts_index()
            task = index.delete_documents(gift_ids)
            logger.info(f"Removed {len(gift_ids)} gifts: task {task.task_uid}")
            return task.task_uid
        except MeilisearchApiError as e:
            logger.error(f"Failed to remove gifts batch: {e}")
            raise

    def search_gifts(
        self,
        query: str = "",
        filters: Optional[Dict[str, Any]] = None,
        sort: Optional[List[str]] = None,
        page: int = 0,
        page_size: int = 20,
        facets: Optional[List[str]] = None,
        attributes_to_retrieve: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Search gifts with filters, sorting, and pagination.

        Args:
            query: Search query string.
            filters: Filter conditions:
                - collection_id: int
                - rarity: str or List[str]
                - is_on_sale: bool
                - price_min: float
                - price_max: float
                - backdrop: str
                - model: str
            sort: Sort expressions (e.g., ["price_ton:asc", "name:desc"]).
            page: Page number (0-indexed).
            page_size: Results per page (max 100).
            facets: Attributes to get facet counts for.
            attributes_to_retrieve: Specific attributes to return.

        Returns:
            Search results with structure:
            {
                "hits": [...],
                "total": int,
                "page": int,
                "page_size": int,
                "total_pages": int,
                "processing_time_ms": int,
                "facet_distribution": {...},
            }
        """
        # Build filter string
        filter_parts = []
        if filters:
            if filters.get("collection_id"):
                filter_parts.append(f"collection_id = {filters['collection_id']}")

            if filters.get("rarity"):
                rarity = filters["rarity"]
                if isinstance(rarity, list):
                    rarity_filters = " OR ".join(f'rarity = "{r}"' for r in rarity)
                    filter_parts.append(f"({rarity_filters})")
                else:
                    filter_parts.append(f'rarity = "{rarity}"')

            if filters.get("is_on_sale") is not None:
                filter_parts.append(
                    f"is_on_sale = {str(filters['is_on_sale']).lower()}"
                )

            if filters.get("price_min") is not None:
                filter_parts.append(f"price_ton >= {filters['price_min']}")

            if filters.get("price_max") is not None:
                filter_parts.append(f"price_ton <= {filters['price_max']}")

            if filters.get("backdrop"):
                filter_parts.append(f'backdrop = "{filters["backdrop"]}"')

            if filters.get("model"):
                filter_parts.append(f'model = "{filters["model"]}"')

        filter_string = " AND ".join(filter_parts) if filter_parts else None

        # Build search parameters
        search_params = {
            "offset": page * page_size,
            "limit": min(page_size, 100),
        }

        if filter_string:
            search_params["filter"] = filter_string

        if sort:
            search_params["sort"] = sort

        if facets:
            search_params["facets"] = facets

        if attributes_to_retrieve:
            search_params["attributesToRetrieve"] = attributes_to_retrieve

        # Highlight search terms in results
        search_params["attributesToHighlight"] = ["name", "description"]
        search_params["highlightPreTag"] = "<mark>"
        search_params["highlightPostTag"] = "</mark>"

        try:
            index = self._client.get_gifts_index()
            result = index.search(query, search_params)

            total = result.get("estimatedTotalHits", 0)
            total_pages = (total + page_size - 1) // page_size if total > 0 else 0

            return {
                "hits": result.get("hits", []),
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": total_pages,
                "processing_time_ms": result.get("processingTimeMs", 0),
                "facet_distribution": result.get("facetDistribution", {}),
                "facet_stats": result.get("facetStats", {}),
            }

        except MeilisearchApiError as e:
            logger.error(f"Search failed: {e}")
            raise

    def autocomplete(
        self,
        query: str,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Get autocomplete suggestions for a search query.

        Optimized for speed with minimal attributes returned.

        Args:
            query: Partial search query.
            limit: Maximum number of suggestions.

        Returns:
            List of suggestions with id, name, and collection_name.
        """
        if not query or len(query) < 1:
            return []

        try:
            index = self._client.get_gifts_index()
            result = index.search(
                query,
                {
                    "limit": min(limit, 20),
                    "attributesToRetrieve": [
                        "id",
                        "name",
                        "collection_name",
                        "rarity",
                        "image_url",
                        "price_ton",
                        "is_on_sale",
                    ],
                    "attributesToHighlight": ["name"],
                    "highlightPreTag": "<mark>",
                    "highlightPostTag": "</mark>",
                },
            )
            return result.get("hits", [])

        except MeilisearchApiError as e:
            logger.error(f"Autocomplete failed: {e}")
            return []

    def get_facets(
        self,
        query: str = "",
        filters: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Get facet counts for filter options.

        Useful for building filter UI with counts.

        Args:
            query: Optional search query to scope facets.
            filters: Current active filters.

        Returns:
            Facet distribution with counts for each value.
        """
        result = self.search_gifts(
            query=query,
            filters=filters,
            page_size=0,
            facets=["rarity", "collection_id", "backdrop", "model", "is_on_sale"],
        )

        return {
            "facet_distribution": result.get("facet_distribution", {}),
            "facet_stats": result.get("facet_stats", {}),
        }


# Module-level service instance
_search_service: Optional[SearchService] = None


def get_search_service() -> SearchService:
    """
    Get the global SearchService instance.

    Returns:
        Configured SearchService instance.
    """
    global _search_service
    if _search_service is None:
        _search_service = SearchService()
    return _search_service

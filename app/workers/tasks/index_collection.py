"""
Collection indexing tasks.

Handles:
- Full collection indexing from TON blockchain
- Incremental updates
- Metadata resolution
"""
import asyncio
import logging
from datetime import datetime

from celery import shared_task
from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert

from app.workers.celery_app import celery_app
from app.core.database import get_async_session
from app.models.collection import Collection
from app.models.nft import NFT
from app.indexer.ton_client import get_ton_client, NFTItemData
from app.indexer.metadata_resolver import get_metadata_resolver
from app.config import settings

logger = logging.getLogger(__name__)


def run_async(coro):
    """Helper to run async code in sync Celery task."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@celery_app.task(
    name="app.workers.tasks.index_collection.index_collection",
    bind=True,
    max_retries=3,
    default_retry_delay=60,
)
def index_collection(self, collection_address: str, force_reindex: bool = False):
    """
    Index all NFTs in a collection.

    Args:
        collection_address: TON collection contract address
        force_reindex: If True, re-fetch all NFTs even if already indexed
    """
    logger.info(f"Starting indexing for collection {collection_address}")

    try:
        result = run_async(_index_collection_async(collection_address, force_reindex))
        logger.info(f"Completed indexing collection {collection_address}: {result}")
        return result

    except Exception as e:
        logger.error(f"Error indexing collection {collection_address}: {e}")
        raise self.retry(exc=e)


async def _index_collection_async(
    collection_address: str,
    force_reindex: bool = False,
) -> dict:
    """Async implementation of collection indexing."""
    ton_client = get_ton_client()
    stats = {
        "collection_address": collection_address,
        "total_items": 0,
        "new_items": 0,
        "updated_items": 0,
        "errors": 0,
    }

    async with get_async_session() as session:
        # Get or create collection record
        result = await session.execute(
            select(Collection).where(Collection.address == collection_address)
        )
        collection = result.scalar_one_or_none()

        # Fetch collection metadata from TON
        try:
            collection_data = await ton_client.get_collection(collection_address)
        except Exception as e:
            logger.error(f"Failed to fetch collection {collection_address}: {e}")
            raise

        if not collection:
            # Create new collection
            collection = Collection(
                address=collection_address,
                name=collection_data.name,
                slug=_generate_slug(collection_data.name),
                description=collection_data.description,
                image_url=collection_data.image_url,
                external_url=collection_data.external_url,
                total_items=collection_data.items_count,
                is_telegram_gift=collection_address in settings.TELEGRAM_GIFT_COLLECTIONS,
                raw_metadata=collection_data.raw_metadata,
                indexing_status="indexing",
            )
            session.add(collection)
            await session.flush()
            logger.info(f"Created collection record: {collection.name}")
        else:
            # Update collection
            collection.name = collection_data.name
            collection.description = collection_data.description
            collection.image_url = collection_data.image_url
            collection.total_items = collection_data.items_count
            collection.indexing_status = "indexing"
            await session.flush()

        collection_id = collection.id

        # Index all NFTs in collection
        batch = []
        batch_size = 50

        async for nft_data in ton_client.iter_collection_items(collection_address):
            stats["total_items"] += 1

            try:
                nft_record = _build_nft_record(nft_data, collection_id)
                batch.append(nft_record)

                if len(batch) >= batch_size:
                    new, updated = await _upsert_nft_batch(session, batch)
                    stats["new_items"] += new
                    stats["updated_items"] += updated
                    batch = []

            except Exception as e:
                logger.error(f"Error processing NFT {nft_data.address}: {e}")
                stats["errors"] += 1
                continue

        # Process remaining batch
        if batch:
            new, updated = await _upsert_nft_batch(session, batch)
            stats["new_items"] += new
            stats["updated_items"] += updated

        # Update collection status
        await session.execute(
            update(Collection)
            .where(Collection.id == collection_id)
            .values(
                indexing_status="completed",
                last_indexed_at=datetime.utcnow(),
            )
        )

        await session.commit()

    return stats


def _build_nft_record(nft_data: NFTItemData, collection_id: int) -> dict:
    """Build NFT database record from TON API data."""
    # Extract common attributes
    rarity = None
    backdrop = None
    model = None
    symbol = None

    for attr in nft_data.attributes:
        trait_type = attr.get("trait_type", "").lower()
        value = attr.get("value", "")

        if "rarity" in trait_type:
            rarity = value
        elif "backdrop" in trait_type or "background" in trait_type:
            backdrop = value
        elif "model" in trait_type:
            model = value
        elif "symbol" in trait_type:
            symbol = value

    return {
        "address": nft_data.address,
        "collection_id": collection_id,
        "index": nft_data.index,
        "name": nft_data.name,
        "description": nft_data.description,
        "image_url": nft_data.image_url,
        "animation_url": nft_data.animation_url,
        "rarity": rarity,
        "backdrop": backdrop,
        "model": model,
        "symbol": symbol,
        "attributes": nft_data.attributes,
        "owner_address": nft_data.owner_address,
        "is_on_sale": nft_data.is_on_sale,
        "metadata_url": nft_data.metadata_url,
        "raw_metadata": nft_data.raw_metadata,
    }


async def _upsert_nft_batch(session, batch: list[dict]) -> tuple[int, int]:
    """
    Upsert batch of NFT records.

    Returns:
        Tuple of (new_count, updated_count)
    """
    if not batch:
        return 0, 0

    # PostgreSQL upsert
    stmt = insert(NFT).values(batch)
    stmt = stmt.on_conflict_do_update(
        index_elements=["address"],
        set_={
            "name": stmt.excluded.name,
            "description": stmt.excluded.description,
            "image_url": stmt.excluded.image_url,
            "animation_url": stmt.excluded.animation_url,
            "rarity": stmt.excluded.rarity,
            "backdrop": stmt.excluded.backdrop,
            "model": stmt.excluded.model,
            "symbol": stmt.excluded.symbol,
            "attributes": stmt.excluded.attributes,
            "owner_address": stmt.excluded.owner_address,
            "is_on_sale": stmt.excluded.is_on_sale,
            "raw_metadata": stmt.excluded.raw_metadata,
            "updated_at": datetime.utcnow(),
        },
    )

    result = await session.execute(stmt)

    # rowcount gives total affected, not distinguishing new vs updated
    # For simplicity, assume all are updated (accurate stats would need separate query)
    return 0, len(batch)


def _generate_slug(name: str) -> str:
    """Generate URL-safe slug from name."""
    import re
    slug = name.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'[\s_]+', '-', slug)
    slug = re.sub(r'-+', '-', slug)
    return slug.strip('-')


@celery_app.task(
    name="app.workers.tasks.index_collection.index_telegram_gift_collections",
    bind=True,
)
def index_telegram_gift_collections(self):
    """
    Index all known Telegram Gift collections.

    This is the main entry point for initial indexing.
    """
    logger.info("Starting Telegram Gift collections indexing")

    collections = settings.TELEGRAM_GIFT_COLLECTIONS
    results = {}

    for collection_address in collections:
        try:
            result = index_collection(collection_address)
            results[collection_address] = result
        except Exception as e:
            logger.error(f"Failed to index {collection_address}: {e}")
            results[collection_address] = {"error": str(e)}

    return results

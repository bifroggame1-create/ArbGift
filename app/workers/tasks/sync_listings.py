"""
Listings synchronization tasks.

Handles:
- Syncing active listings from all markets
- Updating listing status
- Cleaning up stale listings
"""
import asyncio
import logging
from datetime import datetime, timedelta
from decimal import Decimal

from celery import shared_task
from sqlalchemy import select, update, delete, and_
from sqlalchemy.dialects.postgresql import insert

from app.workers.celery_app import celery_app
from app.core.database import get_async_session
from app.models.nft import NFT
from app.models.listing import Listing
from app.models.market import Market
from app.adapters.getgems import GetGemsAdapter
from app.adapters.base import NormalizedListing, ListingStatus
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


# Registry of adapters
ADAPTERS = {
    "getgems": GetGemsAdapter,
    # Add more adapters here
    # "fragment": FragmentAdapter,
    # "pawnstars": PawnStarsAdapter,
}


@celery_app.task(
    name="app.workers.tasks.sync_listings.sync_all_listings",
    bind=True,
)
def sync_all_listings(self):
    """
    Sync listings from all active markets for all collections.

    This is the main periodic sync task.
    """
    logger.info("Starting full listings sync")

    try:
        result = run_async(_sync_all_listings_async())
        logger.info(f"Completed full listings sync: {result}")
        return result
    except Exception as e:
        logger.error(f"Error in full listings sync: {e}")
        raise


async def _sync_all_listings_async() -> dict:
    """Async implementation of full listings sync."""
    stats = {
        "markets_synced": 0,
        "collections_synced": 0,
        "total_listings": 0,
        "new_listings": 0,
        "updated_listings": 0,
        "deactivated_listings": 0,
        "errors": [],
    }

    async with get_async_session() as session:
        # Get all active markets
        result = await session.execute(
            select(Market).where(Market.is_active == True)
        )
        markets = result.scalars().all()

        # Get all indexed collections
        from app.models.collection import Collection
        result = await session.execute(
            select(Collection).where(Collection.indexing_status == "completed")
        )
        collections = result.scalars().all()

        for market in markets:
            adapter_class = ADAPTERS.get(market.slug)
            if not adapter_class:
                logger.warning(f"No adapter for market {market.slug}")
                continue

            adapter = adapter_class(config=market.config)

            try:
                for collection in collections:
                    try:
                        sync_result = await _sync_collection_market(
                            session, adapter, market, collection
                        )
                        stats["total_listings"] += sync_result.get("total", 0)
                        stats["new_listings"] += sync_result.get("new", 0)
                        stats["updated_listings"] += sync_result.get("updated", 0)
                        stats["deactivated_listings"] += sync_result.get("deactivated", 0)
                        stats["collections_synced"] += 1

                    except Exception as e:
                        error_msg = f"{market.slug}/{collection.address}: {e}"
                        logger.error(f"Error syncing: {error_msg}")
                        stats["errors"].append(error_msg)

                stats["markets_synced"] += 1

            finally:
                await adapter.close()

        await session.commit()

    return stats


async def _sync_collection_market(
    session,
    adapter,
    market,
    collection,
) -> dict:
    """
    Sync listings for a specific collection from a specific market.

    Returns:
        Dict with sync stats
    """
    stats = {"total": 0, "new": 0, "updated": 0, "deactivated": 0}

    # Fetch current listings from market
    listings = await adapter.fetch_collection_listings(collection.address)
    stats["total"] = len(listings)

    if not listings:
        # Mark all existing listings as inactive
        deactivated = await _deactivate_market_listings(session, market.id, collection.id)
        stats["deactivated"] = deactivated
        return stats

    # Build NFT address to ID mapping
    nft_addresses = [l.nft_address for l in listings]
    result = await session.execute(
        select(NFT.id, NFT.address)
        .where(NFT.address.in_(nft_addresses))
    )
    nft_map = {row.address: row.id for row in result}

    # Track seen listing IDs for deactivation
    seen_listing_ids = set()

    # Upsert listings
    for listing in listings:
        nft_id = nft_map.get(listing.nft_address)
        if not nft_id:
            # NFT not in our DB - skip or index it
            continue

        listing_data = {
            "nft_id": nft_id,
            "market_id": market.id,
            "market_listing_id": listing.market_listing_id,
            "price_raw": listing.price_raw,
            "currency": listing.currency,
            "price_ton": listing.price_ton,
            "seller_address": listing.seller_address,
            "listing_url": listing.listing_url,
            "is_active": True,
            "listed_at": listing.listed_at,
            "expires_at": listing.expires_at,
            "last_seen_at": datetime.utcnow(),
        }

        # Upsert listing
        stmt = insert(Listing).values(listing_data)
        stmt = stmt.on_conflict_do_update(
            constraint="uq_listings_market_nft",
            set_={
                "price_raw": stmt.excluded.price_raw,
                "price_ton": stmt.excluded.price_ton,
                "is_active": True,
                "last_seen_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            },
        )
        await session.execute(stmt)

        seen_listing_ids.add(listing.market_listing_id)
        stats["updated"] += 1

    # Deactivate listings not seen in this sync
    if seen_listing_ids:
        deactivated = await session.execute(
            update(Listing)
            .where(
                and_(
                    Listing.market_id == market.id,
                    Listing.nft_id.in_(
                        select(NFT.id).where(NFT.collection_id == collection.id)
                    ),
                    Listing.is_active == True,
                    Listing.market_listing_id.notin_(seen_listing_ids),
                )
            )
            .values(is_active=False, updated_at=datetime.utcnow())
        )
        stats["deactivated"] = deactivated.rowcount

    # Update NFT sale status
    await _update_nft_sale_status(session, list(nft_map.values()))

    return stats


async def _deactivate_market_listings(
    session,
    market_id: int,
    collection_id: int,
) -> int:
    """Deactivate all listings for a market/collection pair."""
    from app.models.nft import NFT

    result = await session.execute(
        update(Listing)
        .where(
            and_(
                Listing.market_id == market_id,
                Listing.nft_id.in_(
                    select(NFT.id).where(NFT.collection_id == collection_id)
                ),
                Listing.is_active == True,
            )
        )
        .values(is_active=False, updated_at=datetime.utcnow())
    )
    return result.rowcount


async def _update_nft_sale_status(session, nft_ids: list[int]):
    """
    Update NFT sale status based on active listings.

    Sets is_on_sale, lowest_price_ton, lowest_price_market for each NFT.
    """
    if not nft_ids:
        return

    from sqlalchemy import func

    # Find cheapest active listing for each NFT
    subquery = (
        select(
            Listing.nft_id,
            func.min(Listing.price_ton).label("min_price"),
        )
        .where(
            and_(
                Listing.nft_id.in_(nft_ids),
                Listing.is_active == True,
            )
        )
        .group_by(Listing.nft_id)
        .subquery()
    )

    # Get the market for the cheapest listing
    result = await session.execute(
        select(
            Listing.nft_id,
            Listing.price_ton,
            Market.slug,
        )
        .join(subquery, and_(
            Listing.nft_id == subquery.c.nft_id,
            Listing.price_ton == subquery.c.min_price,
        ))
        .join(Market, Listing.market_id == Market.id)
        .where(Listing.is_active == True)
    )
    cheapest = {row.nft_id: (row.price_ton, row.slug) for row in result}

    # Update NFTs
    for nft_id in nft_ids:
        if nft_id in cheapest:
            price, market_slug = cheapest[nft_id]
            await session.execute(
                update(NFT)
                .where(NFT.id == nft_id)
                .values(
                    is_on_sale=True,
                    lowest_price_ton=price,
                    lowest_price_market=market_slug,
                    updated_at=datetime.utcnow(),
                )
            )
        else:
            await session.execute(
                update(NFT)
                .where(NFT.id == nft_id)
                .values(
                    is_on_sale=False,
                    lowest_price_ton=None,
                    lowest_price_market=None,
                    updated_at=datetime.utcnow(),
                )
            )


@celery_app.task(
    name="app.workers.tasks.sync_listings.cleanup_stale_listings",
    bind=True,
)
def cleanup_stale_listings(self, hours: int = 24):
    """
    Clean up listings not seen for a specified time.

    Args:
        hours: Listings not seen for this many hours are deactivated
    """
    logger.info(f"Cleaning up listings not seen for {hours} hours")

    try:
        result = run_async(_cleanup_stale_listings_async(hours))
        logger.info(f"Cleaned up {result} stale listings")
        return result
    except Exception as e:
        logger.error(f"Error cleaning up stale listings: {e}")
        raise


async def _cleanup_stale_listings_async(hours: int) -> int:
    """Async implementation of stale listing cleanup."""
    cutoff = datetime.utcnow() - timedelta(hours=hours)

    async with get_async_session() as session:
        result = await session.execute(
            update(Listing)
            .where(
                and_(
                    Listing.is_active == True,
                    Listing.last_seen_at < cutoff,
                )
            )
            .values(is_active=False, updated_at=datetime.utcnow())
        )
        await session.commit()
        return result.rowcount


@celery_app.task(
    name="app.workers.tasks.sync_listings.sync_single_market",
    bind=True,
)
def sync_single_market(self, market_slug: str, collection_address: str = None):
    """
    Sync listings from a single market.

    Args:
        market_slug: Market identifier
        collection_address: Optional collection filter
    """
    logger.info(f"Syncing market {market_slug}")

    try:
        result = run_async(_sync_single_market_async(market_slug, collection_address))
        logger.info(f"Synced market {market_slug}: {result}")
        return result
    except Exception as e:
        logger.error(f"Error syncing market {market_slug}: {e}")
        raise


async def _sync_single_market_async(
    market_slug: str,
    collection_address: str = None,
) -> dict:
    """Async implementation of single market sync."""
    adapter_class = ADAPTERS.get(market_slug)
    if not adapter_class:
        raise ValueError(f"No adapter for market {market_slug}")

    async with get_async_session() as session:
        # Get market
        result = await session.execute(
            select(Market).where(Market.slug == market_slug)
        )
        market = result.scalar_one_or_none()
        if not market:
            raise ValueError(f"Market {market_slug} not found in database")

        # Get collections to sync
        from app.models.collection import Collection
        query = select(Collection).where(Collection.indexing_status == "completed")
        if collection_address:
            query = query.where(Collection.address == collection_address)

        result = await session.execute(query)
        collections = result.scalars().all()

        adapter = adapter_class(config=market.config)
        stats = {"total": 0, "new": 0, "updated": 0, "deactivated": 0}

        try:
            for collection in collections:
                sync_result = await _sync_collection_market(
                    session, adapter, market, collection
                )
                for key in stats:
                    stats[key] += sync_result.get(key, 0)

            await session.commit()

        finally:
            await adapter.close()

    return stats

#!/usr/bin/env python3
"""
Standalone script to sync Telegram gifts via MTProto.

Usage:
    # First run — will ask for phone number + code:
    python scripts/sync_telegram.py

    # Subsequent runs use saved session:
    python scripts/sync_telegram.py

    # Only fetch catalog (no DB writes):
    python scripts/sync_telegram.py --catalog-only

    # Limit items per gift type:
    python scripts/sync_telegram.py --max-per-type 100
"""
import asyncio
import argparse
import logging
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.indexer.telegram_gifts import TelegramGiftIndexer
from app.config import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)
logger = logging.getLogger("sync_telegram")


async def catalog_only():
    """Just print the catalog — no DB writes."""
    indexer = TelegramGiftIndexer()
    await indexer.connect()

    try:
        catalog = await indexer.get_catalog()
        total_resale = 0

        print(f"\n{'='*70}")
        print(f"{'ID':>10} | {'Title':<25} | {'Stars':>8} | {'On Resale':>10} | {'Min Stars':>10}")
        print(f"{'='*70}")

        for g in sorted(catalog, key=lambda x: x.availability_resale or 0, reverse=True):
            title = g.title or f"Gift #{g.id}"
            resale = g.availability_resale or 0
            min_stars = g.resell_min_stars or 0
            total_resale += resale
            print(f"{g.id:>10} | {title:<25} | {g.stars:>8} | {resale:>10} | {min_stars:>10}")

        print(f"{'='*70}")
        print(f"Total on resale: {total_resale}")

        # Show first 5 gifts of the most popular type
        top = max(catalog, key=lambda x: x.availability_resale or 0)
        print(f"\nTop 5 cheapest {top.title}:")
        gifts = await indexer.fetch_all_resale_gifts(top.id, max_items=5)
        for g in gifts:
            print(f"  #{g.num} slug={g.slug} price={g.price_stars} stars "
                  f"({g.price_ton:.4f} TON) "
                  f"model={g.model_name} backdrop={g.backdrop_name}")

    finally:
        await indexer.disconnect()


async def full_sync(max_per_type: int = 5000):
    """Run full sync with database writes."""
    from app.sync.data_loader import SyncDataLoader

    loader = SyncDataLoader()
    try:
        count = await loader.sync_telegram_listings(max_items_per_type=max_per_type)
        print(f"\nSynced {count} listings from Telegram")
    finally:
        await loader.close()


async def main():
    parser = argparse.ArgumentParser(description="Sync Telegram gifts via MTProto")
    parser.add_argument("--catalog-only", action="store_true", help="Only show catalog, no DB writes")
    parser.add_argument("--max-per-type", type=int, default=5000, help="Max gifts per type (default: 5000)")
    args = parser.parse_args()

    if args.catalog_only:
        await catalog_only()
    else:
        await full_sync(args.max_per_type)


if __name__ == "__main__":
    asyncio.run(main())

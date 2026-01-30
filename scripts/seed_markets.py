#!/usr/bin/env python3
"""
Seed markets table with known marketplaces.

Run: python scripts/seed_markets.py
"""
import asyncio
import sys
sys.path.insert(0, ".")

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from app.core.database import get_async_session, init_db
from app.models.market import Market


MARKETS = [
    {
        "slug": "getgems",
        "name": "GetGems",
        "website_url": "https://getgems.io",
        "api_base_url": "https://api.getgems.io",
        "fee_buy_percent": 5.0,
        "fee_sell_percent": 0,
        "is_active": True,
        "priority": 100,
        "config": {
            "graphql_url": "https://api.getgems.io/graphql",
        },
    },
    {
        "slug": "fragment",
        "name": "Fragment",
        "website_url": "https://fragment.com",
        "api_base_url": None,  # Uses TON API
        "fee_buy_percent": 0,
        "fee_sell_percent": 5.0,
        "is_active": True,
        "priority": 90,
        "config": {
            "collection_address": "EQD-BJSVUJviud_Qv7Ymfd3qzXdrmV525e3YDzWQoHIAiInL",
        },
    },
    {
        "slug": "tonnel",
        "name": "Tonnel",
        "website_url": "https://tonnel.network",
        "api_base_url": "https://api.tonnel.network",
        "fee_buy_percent": 2.5,
        "fee_sell_percent": 2.5,
        "is_active": False,  # Enable when adapter is ready
        "priority": 80,
        "config": {},
    },
    {
        "slug": "mrkt",
        "name": "MRKT",
        "website_url": "https://tgmrkt.io",
        "api_base_url": "https://api.tgmrkt.io/api/v1",
        "fee_buy_percent": 2.0,
        "fee_sell_percent": 2.0,
        "is_active": False,  # Requires Telegram auth
        "priority": 70,
        "config": {},
    },
    {
        "slug": "pawnstars",
        "name": "PawnStars",
        "website_url": "https://pawnstars-pied.vercel.app",
        "api_base_url": None,
        "fee_buy_percent": 0,
        "fee_sell_percent": 0,
        "is_active": False,
        "priority": 60,
        "config": {},
    },
]


async def seed_markets():
    """Seed markets table."""
    print("Seeding markets...")

    async with get_async_session() as session:
        for market_data in MARKETS:
            # Upsert market
            stmt = insert(Market).values(**market_data)
            stmt = stmt.on_conflict_do_update(
                index_elements=["slug"],
                set_={
                    "name": stmt.excluded.name,
                    "website_url": stmt.excluded.website_url,
                    "api_base_url": stmt.excluded.api_base_url,
                    "fee_buy_percent": stmt.excluded.fee_buy_percent,
                    "fee_sell_percent": stmt.excluded.fee_sell_percent,
                    "priority": stmt.excluded.priority,
                    "config": stmt.excluded.config,
                },
            )
            await session.execute(stmt)
            print(f"  ✓ {market_data['name']} ({market_data['slug']})")

        await session.commit()

    print("Markets seeded successfully!")


async def seed_collections():
    """Seed known Telegram Gift collections."""
    from app.config import settings
    from app.models.collection import Collection

    print("Seeding Telegram Gift collections...")

    collections = [
        {
            "address": "EQBTKUGf_2wz0mVji52re8oWcDZYUbCm2tAjAWYCODc2u5TP",
            "name": "Telegram Gifts (GetGems)",
            "slug": "telegram-gifts-getgems",
            "is_telegram_gift": True,
            "is_verified": True,
        },
        {
            "address": "EQD-BJSVUJviud_Qv7Ymfd3qzXdrmV525e3YDzWQoHIAiInL",
            "name": "Telegram Gifts (Fragment)",
            "slug": "telegram-gifts-fragment",
            "is_telegram_gift": True,
            "is_verified": True,
        },
    ]

    async with get_async_session() as session:
        for collection_data in collections:
            stmt = insert(Collection).values(**collection_data)
            stmt = stmt.on_conflict_do_update(
                index_elements=["address"],
                set_={
                    "name": stmt.excluded.name,
                    "is_telegram_gift": stmt.excluded.is_telegram_gift,
                    "is_verified": stmt.excluded.is_verified,
                },
            )
            await session.execute(stmt)
            print(f"  ✓ {collection_data['name']}")

        await session.commit()

    print("Collections seeded successfully!")


async def main():
    """Main seed function."""
    await init_db()
    await seed_markets()
    await seed_collections()
    print("\nDatabase seeded successfully!")
    print("\nNext steps:")
    print("1. Run migrations: alembic upgrade head")
    print("2. Start the API: uvicorn app.main:app --reload")
    print("3. Start Celery worker: celery -A app.workers.celery_app worker")
    print("4. Trigger indexing: POST /api/v1/admin/index-collection")


if __name__ == "__main__":
    asyncio.run(main())

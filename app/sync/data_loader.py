"""
Синхронный загрузчик данных с маркетов.

НЕ использует Celery — запускается напрямую при старте приложения
и по API-триггеру.
"""
import asyncio
import logging
from datetime import datetime
from decimal import Decimal
from typing import Optional

import httpx

from app.core.database import get_async_session
from app.models.collection import Collection
from app.models.nft import NFT
from app.models.listing import Listing
from app.models.market import Market
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert

logger = logging.getLogger(__name__)


class PortalsMarketLoader:
    """
    Загрузчик данных с Portals.tg API.

    API Base: https://portal-market.com/api

    Endpoints:
    - GET /nfts/search - список NFT с листингами
    - GET /market/volume - объём торгов
    - GET /market/config - конфиг маркета
    """

    API_BASE = "https://portal-market.com/api"
    MARKET_SLUG = "portals"
    MARKET_NAME = "Portals.tg"

    def __init__(self):
        self.client = httpx.AsyncClient(
            timeout=30.0,
            headers={
                "User-Agent": "TonGiftAggregator/1.0",
                "Accept": "application/json",
            }
        )

    async def close(self):
        await self.client.aclose()

    async def fetch_listings(
        self,
        offset: int = 0,
        limit: int = 50,
        sort_by: str = "listed_at desc",
    ) -> dict:
        """
        Получить листинги с Portals.tg.

        Response structure:
        {
            "results": [
                {
                    "id": "uuid",
                    "tg_id": "InstantRamen-130959",
                    "name": "Instant Ramen",
                    "photo_url": "https://nft.fragment.com/gift/...",
                    "price": "10",
                    "attributes": [...],
                    "listed_at": "2026-02-01T14:56:17Z",
                    "floor_price": "3.53",
                    ...
                }
            ]
        }
        """
        try:
            response = await self.client.get(
                f"{self.API_BASE}/nfts/search",
                params={
                    "offset": offset,
                    "limit": limit,
                    "sort_by": sort_by,
                    "exclude_bundled": "true",
                    "status": "listed",
                }
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"[PortalsLoader] Ошибка загрузки: {e}")
            return {"results": []}

    async def fetch_all_listings(self, max_items: int = 1000) -> list[dict]:
        """Загрузить все листинги с пагинацией."""
        all_listings = []
        offset = 0
        limit = 50

        while len(all_listings) < max_items:
            data = await self.fetch_listings(offset=offset, limit=limit)
            results = data.get("results", [])

            if not results:
                break

            all_listings.extend(results)
            offset += limit

            logger.info(f"[PortalsLoader] Загружено {len(all_listings)} листингов")

            # Небольшая пауза чтобы не нагружать API
            await asyncio.sleep(0.5)

        return all_listings[:max_items]


class MajorMarketLoader:
    """
    Загрузчик данных с Major.tg API.

    API Base: https://major.tg/api/v1

    Endpoints:
    - GET /nft/list/ - список NFT
    """

    API_BASE = "https://major.tg/api/v1"
    MARKET_SLUG = "major"
    MARKET_NAME = "Major.tg"

    def __init__(self):
        self.client = httpx.AsyncClient(
            timeout=30.0,
            headers={
                "User-Agent": "TonGiftAggregator/1.0",
                "Accept": "application/json",
            }
        )

    async def close(self):
        await self.client.aclose()

    async def fetch_listings(
        self,
        offset: int = 0,
        limit: int = 30,
        order_by: str = "price_asc",
    ) -> dict:
        """
        Получить листинги с Major.tg.

        Response structure:
        {
            "items": [
                {
                    "address": "...",
                    "name": "Desk Calendar",
                    "slug": "deskcalendar",
                    "image": "https://i.major.tg/...",
                    "min_bid": 3.50,
                    "max_bid": 10.00,
                    "market_type": "auction",
                    "is_on_sale": true,
                    "currency": "TON",
                    ...
                }
            ]
        }
        """
        try:
            response = await self.client.get(
                f"{self.API_BASE}/nft/list/",
                params={
                    "offset": offset,
                    "limit": limit,
                    "order_by": order_by,
                }
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"[MajorLoader] Ошибка загрузки: {e}")
            return {"items": []}

    async def fetch_all_listings(self, max_items: int = 500) -> list[dict]:
        """Загрузить все листинги с пагинацией."""
        all_listings = []
        offset = 0
        limit = 30

        while len(all_listings) < max_items:
            data = await self.fetch_listings(offset=offset, limit=limit)
            items = data.get("items", [])

            if not items:
                break

            all_listings.extend(items)
            offset += limit

            logger.info(f"[MajorLoader] Загружено {len(all_listings)} листингов")

            await asyncio.sleep(0.3)

        return all_listings[:max_items]


class SyncDataLoader:
    """
    Главный синхронный загрузчик.

    Объединяет данные со всех маркетов и сохраняет в БД.
    """

    def __init__(self):
        self.portals_loader = PortalsMarketLoader()
        self.major_loader = MajorMarketLoader()

    async def close(self):
        await self.portals_loader.close()
        await self.major_loader.close()

    async def ensure_market_exists(self, session, slug: str, name: str, url: str) -> Market:
        """Создать маркет если не существует."""
        result = await session.execute(
            select(Market).where(Market.slug == slug)
        )
        market = result.scalar_one_or_none()

        if not market:
            market = Market(
                slug=slug,
                name=name,
                website_url=url,
                is_active=True,
                priority=10,
            )
            session.add(market)
            await session.flush()
            logger.info(f"Создан маркет: {name}")

        return market

    async def ensure_collection_exists(
        self,
        session,
        address: str,
        name: str,
        slug: str = None,
    ) -> Collection:
        """Создать коллекцию если не существует."""
        result = await session.execute(
            select(Collection).where(Collection.address == address)
        )
        collection = result.scalar_one_or_none()

        if not collection:
            collection = Collection(
                address=address,
                name=name,
                slug=slug or name.lower().replace(" ", "-"),
                is_verified=True,
            )
            session.add(collection)
            await session.flush()
            logger.info(f"Создана коллекция: {name}")

        return collection

    async def sync_portals_listings(self, max_items: int = 500) -> int:
        """
        Синхронизировать листинги с Portals.tg.

        Returns: количество добавленных/обновлённых записей
        """
        logger.info("[SyncLoader] Начинаю синхронизацию с Portals.tg...")

        listings = await self.portals_loader.fetch_all_listings(max_items)

        if not listings:
            logger.warning("[SyncLoader] Нет данных с Portals.tg")
            return 0

        count = 0

        async with get_async_session() as session:
            # Создаём маркет
            market = await self.ensure_market_exists(
                session,
                slug="portals",
                name="Portals.tg",
                url="https://portals.tg",
            )

            # Создаём дефолтную коллекцию для гифтов
            collection = await self.ensure_collection_exists(
                session,
                address="telegram-gifts",
                name="Telegram Gifts",
                slug="telegram-gifts",
            )

            for item in listings:
                try:
                    # Парсим данные
                    tg_id = item.get("tg_id", "")
                    name = item.get("name", "Unknown")
                    photo_url = item.get("photo_url", "")
                    price = Decimal(str(item.get("price", "0")))
                    floor_price = Decimal(str(item.get("floor_price", "0")))
                    listed_at = item.get("listed_at")
                    market_listing_id = item.get("id", tg_id)

                    # Атрибуты
                    attributes = item.get("attributes", [])
                    model = None
                    backdrop = None
                    symbol = None

                    for attr in attributes:
                        attr_type = attr.get("type", "")
                        attr_value = attr.get("value", "")
                        if attr_type == "model":
                            model = attr_value
                        elif attr_type == "backdrop":
                            backdrop = attr_value
                        elif attr_type == "symbol":
                            symbol = attr_value

                    # Создаём или обновляем NFT
                    nft_address = f"portals-{tg_id}"

                    result = await session.execute(
                        select(NFT).where(NFT.address == nft_address)
                    )
                    nft = result.scalar_one_or_none()

                    if not nft:
                        nft = NFT(
                            address=nft_address,
                            collection_id=collection.id,
                            name=name,
                            image_url=photo_url,
                            model=model,
                            backdrop=backdrop,
                            symbol=symbol,
                            attributes=attributes,
                            is_on_sale=True,
                            lowest_price_ton=price,
                            lowest_price_market="portals",
                        )
                        session.add(nft)
                        await session.flush()
                    else:
                        nft.is_on_sale = True
                        nft.lowest_price_ton = min(nft.lowest_price_ton or price, price)

                    # Создаём или обновляем листинг
                    result = await session.execute(
                        select(Listing).where(
                            Listing.market_id == market.id,
                            Listing.market_listing_id == market_listing_id,
                        )
                    )
                    listing = result.scalar_one_or_none()

                    if not listing:
                        listing = Listing(
                            nft_id=nft.id,
                            market_id=market.id,
                            market_listing_id=market_listing_id,
                            price_raw=price,
                            currency="TON",
                            price_ton=price,
                            listing_url=f"https://portals.tg/nft/{tg_id}",
                            is_active=True,
                            listed_at=datetime.fromisoformat(listed_at.replace("Z", "+00:00")) if listed_at else None,
                            last_seen_at=datetime.utcnow(),
                        )
                        session.add(listing)
                    else:
                        listing.price_raw = price
                        listing.price_ton = price
                        listing.is_active = True
                        listing.last_seen_at = datetime.utcnow()

                    count += 1

                except Exception as e:
                    logger.error(f"[SyncLoader] Ошибка обработки: {e}")
                    continue

            await session.commit()

        logger.info(f"[SyncLoader] Синхронизировано {count} листингов с Portals.tg")
        return count

    async def sync_major_listings(self, max_items: int = 500) -> int:
        """
        Синхронизировать листинги с Major.tg.

        Returns: количество добавленных/обновлённых записей
        """
        logger.info("[SyncLoader] Начинаю синхронизацию с Major.tg...")

        listings = await self.major_loader.fetch_all_listings(max_items)

        if not listings:
            logger.warning("[SyncLoader] Нет данных с Major.tg")
            return 0

        count = 0

        async with get_async_session() as session:
            # Создаём маркет
            market = await self.ensure_market_exists(
                session,
                slug="major",
                name="Major.tg",
                url="https://major.tg",
            )

            # Создаём дефолтную коллекцию
            collection = await self.ensure_collection_exists(
                session,
                address="telegram-gifts",
                name="Telegram Gifts",
                slug="telegram-gifts",
            )

            for item in listings:
                try:
                    address = item.get("address", "")
                    name = item.get("name", "Unknown")
                    slug = item.get("slug", "")
                    image = item.get("image", "")
                    min_bid = Decimal(str(item.get("min_bid", 0)))

                    # Создаём или обновляем NFT
                    nft_address = f"major-{address}" if address else f"major-{slug}"

                    result = await session.execute(
                        select(NFT).where(NFT.address == nft_address)
                    )
                    nft = result.scalar_one_or_none()

                    if not nft:
                        nft = NFT(
                            address=nft_address,
                            collection_id=collection.id,
                            name=name,
                            image_url=image,
                            is_on_sale=True,
                            lowest_price_ton=min_bid,
                            lowest_price_market="major",
                        )
                        session.add(nft)
                        await session.flush()
                    else:
                        nft.is_on_sale = True
                        if min_bid > 0:
                            nft.lowest_price_ton = min(nft.lowest_price_ton or min_bid, min_bid)

                    # Создаём или обновляем листинг
                    market_listing_id = address or slug

                    result = await session.execute(
                        select(Listing).where(
                            Listing.market_id == market.id,
                            Listing.market_listing_id == market_listing_id,
                        )
                    )
                    listing = result.scalar_one_or_none()

                    if not listing:
                        listing = Listing(
                            nft_id=nft.id,
                            market_id=market.id,
                            market_listing_id=market_listing_id,
                            price_raw=min_bid,
                            currency="TON",
                            price_ton=min_bid,
                            listing_url=f"https://major.tg/nft/{slug}",
                            is_active=True,
                            last_seen_at=datetime.utcnow(),
                        )
                        session.add(listing)
                    else:
                        listing.price_raw = min_bid
                        listing.price_ton = min_bid
                        listing.is_active = True
                        listing.last_seen_at = datetime.utcnow()

                    count += 1

                except Exception as e:
                    logger.error(f"[SyncLoader] Ошибка обработки Major: {e}")
                    continue

            await session.commit()

        logger.info(f"[SyncLoader] Синхронизировано {count} листингов с Major.tg")
        return count

    async def sync_all(self) -> dict:
        """
        Синхронизировать данные со всех маркетов.

        Returns: статистика синхронизации
        """
        logger.info("[SyncLoader] ===== НАЧАЛО ПОЛНОЙ СИНХРОНИЗАЦИИ =====")

        stats = {
            "started_at": datetime.utcnow().isoformat(),
            "portals": 0,
            "major": 0,
            "total": 0,
            "errors": [],
        }

        try:
            stats["portals"] = await self.sync_portals_listings()
        except Exception as e:
            logger.error(f"[SyncLoader] Ошибка Portals: {e}")
            stats["errors"].append(f"portals: {str(e)}")

        try:
            stats["major"] = await self.sync_major_listings()
        except Exception as e:
            logger.error(f"[SyncLoader] Ошибка Major: {e}")
            stats["errors"].append(f"major: {str(e)}")

        stats["total"] = stats["portals"] + stats["major"]
        stats["finished_at"] = datetime.utcnow().isoformat()

        logger.info(f"[SyncLoader] ===== СИНХРОНИЗАЦИЯ ЗАВЕРШЕНА: {stats['total']} записей =====")

        return stats


# Глобальный экземпляр загрузчика
_loader: Optional[SyncDataLoader] = None


async def get_loader() -> SyncDataLoader:
    """Получить экземпляр загрузчика."""
    global _loader
    if _loader is None:
        _loader = SyncDataLoader()
    return _loader


async def run_sync():
    """Запустить синхронизацию (для вызова при старте приложения)."""
    loader = await get_loader()
    return await loader.sync_all()

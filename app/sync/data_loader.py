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
        self._adapters = []
        self._telegram_indexer = None

    async def close(self):
        await self.portals_loader.close()
        await self.major_loader.close()
        for adapter in self._adapters:
            try:
                await adapter.close()
            except Exception:
                pass
        if self._telegram_indexer:
            try:
                await self._telegram_indexer.disconnect()
            except Exception:
                pass

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

    async def sync_adapter_listings(
        self,
        adapter,
        collection_address: str,
        market_slug: str,
        market_name: str,
        market_url: str,
        max_items: int = 1000,
    ) -> int:
        """
        Синхронизировать листинги через адаптер маркета.

        Универсальный метод для любого адаптера, который реализует
        BaseMarketAdapter.fetch_collection_listings().

        Returns: количество добавленных/обновлённых записей
        """
        logger.info(f"[SyncLoader] Начинаю синхронизацию с {market_name}...")

        try:
            normalized_listings = await adapter.fetch_collection_listings(
                collection_address=collection_address,
                limit=max_items,
            )
        except Exception as e:
            logger.error(f"[SyncLoader] Ошибка загрузки с {market_name}: {e}")
            return 0

        if not normalized_listings:
            logger.warning(f"[SyncLoader] Нет данных с {market_name}")
            return 0

        logger.info(f"[SyncLoader] Загружено {len(normalized_listings)} листингов с {market_name}")

        count = 0

        async with get_async_session() as session:
            market = await self.ensure_market_exists(
                session, slug=market_slug, name=market_name, url=market_url,
            )

            collection = await self.ensure_collection_exists(
                session,
                address="telegram-gifts",
                name="Telegram Gifts",
                slug="telegram-gifts",
            )

            for nl in normalized_listings:
                try:
                    nft_address = nl.nft_address
                    if not nft_address:
                        continue

                    extra = nl.extra or {}
                    name = extra.get("name", "Unknown")
                    image_url = extra.get("image_url", "")
                    attributes = extra.get("attributes") or []

                    # Парсим атрибуты (model, backdrop, symbol)
                    model = None
                    backdrop = None
                    symbol = None
                    if isinstance(attributes, list):
                        for attr in attributes:
                            if isinstance(attr, dict):
                                attr_name = attr.get("trait_type", attr.get("type", ""))
                                attr_value = attr.get("value", "")
                                if attr_name.lower() == "model":
                                    model = attr_value
                                elif attr_name.lower() == "backdrop":
                                    backdrop = attr_value
                                elif attr_name.lower() == "symbol":
                                    symbol = attr_value

                    # Создаём или обновляем NFT
                    result = await session.execute(
                        select(NFT).where(NFT.address == nft_address)
                    )
                    nft = result.scalar_one_or_none()

                    price_ton = nl.price_ton

                    if not nft:
                        nft = NFT(
                            address=nft_address,
                            collection_id=collection.id,
                            name=name,
                            image_url=image_url or None,
                            model=model,
                            backdrop=backdrop,
                            symbol=symbol,
                            is_on_sale=True,
                            lowest_price_ton=price_ton,
                            lowest_price_market=market_slug,
                        )
                        session.add(nft)
                        await session.flush()
                    else:
                        nft.is_on_sale = True
                        # Обновляем lowest_price если новая цена ниже
                        if price_ton > 0 and (nft.lowest_price_ton is None or price_ton < nft.lowest_price_ton):
                            nft.lowest_price_ton = price_ton
                            nft.lowest_price_market = market_slug
                        # Обновляем данные если они лучше
                        if image_url and not nft.image_url:
                            nft.image_url = image_url
                        if model and not nft.model:
                            nft.model = model
                        if backdrop and not nft.backdrop:
                            nft.backdrop = backdrop

                    # Создаём или обновляем листинг
                    market_listing_id = nl.market_listing_id or nft_address

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
                            price_raw=price_ton,
                            currency=nl.currency or "TON",
                            price_ton=price_ton,
                            seller_address=nl.seller_address,
                            listing_url=nl.listing_url,
                            is_active=True,
                            listed_at=nl.listed_at,
                            last_seen_at=datetime.utcnow(),
                        )
                        session.add(listing)
                    else:
                        listing.price_raw = price_ton
                        listing.price_ton = price_ton
                        listing.is_active = True
                        listing.last_seen_at = datetime.utcnow()
                        if nl.seller_address:
                            listing.seller_address = nl.seller_address

                    count += 1

                except Exception as e:
                    logger.error(f"[SyncLoader] Ошибка обработки {market_name}: {e}")
                    continue

            await session.commit()

        logger.info(f"[SyncLoader] Синхронизировано {count} листингов с {market_name}")
        return count

    async def sync_getgems_listings(self, max_items: int = 1000) -> int:
        """Синхронизировать листинги с GetGems."""
        from app.adapters.getgems import GetGemsAdapter

        adapter = GetGemsAdapter()
        self._adapters.append(adapter)

        return await self.sync_adapter_listings(
            adapter=adapter,
            collection_address="EQBTKUGf_2wz0mVji52re8oWcDZYUbCm2tAjAWYCODc2u5TP",
            market_slug="getgems",
            market_name="GetGems",
            market_url="https://getgems.io",
            max_items=max_items,
        )

    async def sync_fragment_listings(self, max_items: int = 1000) -> int:
        """Синхронизировать листинги с Fragment."""
        from app.adapters.fragment import FragmentAdapter

        adapter = FragmentAdapter()
        self._adapters.append(adapter)

        return await self.sync_adapter_listings(
            adapter=adapter,
            collection_address="EQD-BJSVUJviud_Qv7Ymfd3qzXdrmV525e3YDzWQoHIAiInL",
            market_slug="fragment",
            market_name="Fragment",
            market_url="https://fragment.com",
            max_items=max_items,
        )

    async def sync_telegram_listings(self, max_items_per_type: int = 5000) -> int:
        """
        Синхронизировать листинги через Telegram MTProto API.

        Это основной источник данных — видит ВСЕ гифты на ресейле,
        т.к. ресейл происходит через сам Telegram.

        Returns: количество добавленных/обновлённых записей
        """
        from app.indexer.telegram_gifts import TelegramGiftIndexer

        logger.info("[SyncLoader] Начинаю синхронизацию с Telegram MTProto...")

        indexer = TelegramGiftIndexer()
        self._telegram_indexer = indexer

        try:
            await indexer.connect()
        except Exception as e:
            logger.error(f"[SyncLoader] Не удалось подключиться к Telegram: {e}")
            return 0

        count = 0

        try:
            catalog = await indexer.get_catalog()

            async with get_async_session() as session:
                # Маркет "telegram" — сам Telegram (ресейл через приложение)
                market = await self.ensure_market_exists(
                    session,
                    slug="telegram",
                    name="Telegram",
                    url="https://t.me",
                )

                collection = await self.ensure_collection_exists(
                    session,
                    address="telegram-gifts",
                    name="Telegram Gifts",
                    slug="telegram-gifts",
                )

                for gift_type in catalog:
                    type_count = 0
                    logger.info(
                        f"[SyncLoader] Telegram: {gift_type.title or gift_type.id} "
                        f"({gift_type.availability_resale} on resale)"
                    )

                    async for gift in indexer.iter_resale_gifts(
                        gift_type.id,
                        max_pages=max_items_per_type // 100 + 1,
                    ):
                        try:
                            # NFT address: используем slug (уникальный) или gift_address (TON)
                            nft_address = gift.gift_address or f"tg-{gift.slug}"

                            price_ton = gift.price_ton or Decimal("0")
                            price_stars = gift.price_stars or 0

                            # Определяем rarity
                            rarity = None
                            min_rarity = min(
                                r for r in [
                                    gift.model_rarity,
                                    gift.pattern_rarity,
                                    gift.backdrop_rarity,
                                ] if r is not None
                            ) if any(r is not None for r in [gift.model_rarity, gift.pattern_rarity, gift.backdrop_rarity]) else None

                            if min_rarity is not None:
                                if min_rarity <= 10:
                                    rarity = "Legendary"
                                elif min_rarity <= 50:
                                    rarity = "Epic"
                                elif min_rarity <= 150:
                                    rarity = "Rare"
                                elif min_rarity <= 350:
                                    rarity = "Uncommon"
                                else:
                                    rarity = "Common"

                            # Upsert NFT
                            result = await session.execute(
                                select(NFT).where(NFT.address == nft_address)
                            )
                            nft = result.scalar_one_or_none()

                            attributes_json = gift.attributes_raw or []

                            if not nft:
                                nft = NFT(
                                    address=nft_address,
                                    collection_id=collection.id,
                                    index=gift.num,
                                    name=f"{gift.title} #{gift.num}",
                                    image_url=f"https://t.me/nft/{gift.slug}",
                                    model=gift.model_name,
                                    backdrop=gift.backdrop_name,
                                    pattern=gift.pattern_name,
                                    rarity=rarity,
                                    attributes=attributes_json,
                                    owner_address=gift.owner_address,
                                    is_on_sale=True,
                                    lowest_price_ton=price_ton if price_ton > 0 else None,
                                    lowest_price_market="telegram",
                                    raw_metadata={
                                        'unique_id': gift.unique_id,
                                        'gift_id': gift.gift_id,
                                        'slug': gift.slug,
                                        'num': gift.num,
                                        'price_stars': price_stars,
                                        'availability_issued': gift.availability_issued,
                                        'availability_total': gift.availability_total,
                                    },
                                )
                                session.add(nft)
                                await session.flush()
                            else:
                                nft.is_on_sale = True
                                nft.owner_address = gift.owner_address or nft.owner_address
                                nft.attributes = attributes_json
                                if rarity:
                                    nft.rarity = rarity
                                if gift.model_name:
                                    nft.model = gift.model_name
                                if gift.backdrop_name:
                                    nft.backdrop = gift.backdrop_name
                                if gift.pattern_name:
                                    nft.pattern = gift.pattern_name
                                # Обновляем lowest_price
                                if price_ton > 0 and (nft.lowest_price_ton is None or price_ton < nft.lowest_price_ton):
                                    nft.lowest_price_ton = price_ton
                                    nft.lowest_price_market = "telegram"

                            # Upsert Listing
                            market_listing_id = gift.slug

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
                                    price_raw=Decimal(str(price_stars)),
                                    currency="STARS",
                                    price_ton=price_ton,
                                    listing_url=f"https://t.me/nft/{gift.slug}",
                                    is_active=True,
                                    last_seen_at=datetime.utcnow(),
                                )
                                session.add(listing)
                            else:
                                listing.price_raw = Decimal(str(price_stars))
                                listing.price_ton = price_ton
                                listing.is_active = True
                                listing.last_seen_at = datetime.utcnow()

                            type_count += 1
                            count += 1

                            # Flush every 100 items
                            if count % 100 == 0:
                                await session.flush()

                        except Exception as e:
                            logger.error(f"[SyncLoader] Ошибка обработки Telegram gift {gift.slug}: {e}")
                            continue

                    logger.info(f"[SyncLoader] Telegram {gift_type.title}: {type_count} gifts synced")

                await session.commit()

        except Exception as e:
            logger.error(f"[SyncLoader] Ошибка синхронизации Telegram: {e}")
        finally:
            await indexer.disconnect()

        logger.info(f"[SyncLoader] Синхронизировано {count} листингов с Telegram")
        return count

    async def sync_all(self) -> dict:
        """
        Синхронизировать данные со всех маркетов.

        Returns: статистика синхронизации
        """
        logger.info("[SyncLoader] ===== НАЧАЛО ПОЛНОЙ СИНХРОНИЗАЦИИ =====")

        stats = {
            "started_at": datetime.utcnow().isoformat(),
            "telegram": 0,
            "portals": 0,
            "major": 0,
            "getgems": 0,
            "fragment": 0,
            "total": 0,
            "errors": [],
        }

        # Telegram MTProto — основной источник
        try:
            stats["telegram"] = await self.sync_telegram_listings()
        except Exception as e:
            logger.error(f"[SyncLoader] Ошибка Telegram: {e}")
            stats["errors"].append(f"telegram: {str(e)}")

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

        try:
            stats["getgems"] = await self.sync_getgems_listings()
        except Exception as e:
            logger.error(f"[SyncLoader] Ошибка GetGems: {e}")
            stats["errors"].append(f"getgems: {str(e)}")

        try:
            stats["fragment"] = await self.sync_fragment_listings()
        except Exception as e:
            logger.error(f"[SyncLoader] Ошибка Fragment: {e}")
            stats["errors"].append(f"fragment: {str(e)}")

        stats["total"] = sum(v for k, v in stats.items() if isinstance(v, int) and k != "total")
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

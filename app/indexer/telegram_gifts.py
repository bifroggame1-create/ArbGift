"""
Telegram MTProto gift indexer via Telethon.

Uses payments.getStarGifts (catalog) and payments.getResaleStarGifts
to fetch ALL unique gifts on resale directly from Telegram.

This is the primary data source — it sees every gift on every market
because resale happens through Telegram itself.

Requires a USER account (not a bot).
"""
import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional

from telethon import TelegramClient, functions, types

from app.config import settings

logger = logging.getLogger(__name__)


def int_to_hex(n: int) -> str:
    """Convert RGB24 integer to #RRGGBB hex string."""
    return f"#{n & 0xFFFFFF:06X}"


@dataclass
class ParsedGift:
    """Parsed unique gift from Telegram API."""
    # Identity
    unique_id: int          # starGiftUnique.id
    gift_id: int            # base gift type id
    title: str
    slug: str               # t.me/nft/{slug}
    num: int                # sequential number

    # Owner
    owner_address: Optional[str] = None
    gift_address: Optional[str] = None  # TON NFT address

    # Price (in Stars)
    price_stars: Optional[int] = None
    price_ton: Optional[Decimal] = None

    # Availability
    availability_issued: int = 0
    availability_total: int = 0

    # Attributes
    model_name: Optional[str] = None
    model_doc_id: Optional[int] = None
    pattern_name: Optional[str] = None
    pattern_doc_id: Optional[int] = None
    backdrop_name: Optional[str] = None
    backdrop_id: Optional[int] = None
    backdrop_center_color: Optional[str] = None
    backdrop_edge_color: Optional[str] = None
    backdrop_pattern_color: Optional[str] = None
    backdrop_text_color: Optional[str] = None

    # Rarity (permille — per 1000)
    model_rarity: Optional[int] = None
    pattern_rarity: Optional[int] = None
    backdrop_rarity: Optional[int] = None

    # Raw attributes list
    attributes_raw: Optional[list] = None


@dataclass
class CatalogGift:
    """Gift type from the catalog."""
    id: int
    title: Optional[str] = None
    stars: int = 0
    availability_resale: Optional[int] = None
    resell_min_stars: Optional[int] = None
    sticker_doc_id: Optional[int] = None


class TelegramGiftIndexer:
    """
    Indexes all Telegram gifts on resale via MTProto API.

    Usage:
        indexer = TelegramGiftIndexer()
        await indexer.connect()
        catalog = await indexer.get_catalog()
        for gift_type in catalog:
            async for gift in indexer.iter_resale_gifts(gift_type.id):
                # process gift
                pass
        await indexer.disconnect()
    """

    def __init__(
        self,
        api_id: int = None,
        api_hash: str = None,
        session_name: str = None,
    ):
        self.api_id = api_id or settings.TELEGRAM_API_ID
        self.api_hash = api_hash or settings.TELEGRAM_API_HASH
        self.session_name = session_name or settings.TELEGRAM_SESSION_NAME
        self.delay = settings.TELEGRAM_SYNC_DELAY
        self.stars_to_ton = Decimal(str(settings.STARS_TO_TON_RATE))
        self.client: Optional[TelegramClient] = None

    async def connect(self):
        """Connect to Telegram."""
        self.client = TelegramClient(
            self.session_name,
            self.api_id,
            self.api_hash,
        )
        await self.client.start()
        me = await self.client.get_me()
        logger.info(f"[TelegramIndexer] Connected as {me.first_name} (id={me.id})")

    async def disconnect(self):
        """Disconnect from Telegram."""
        if self.client:
            await self.client.disconnect()
            self.client = None

    async def get_catalog(self) -> list[CatalogGift]:
        """
        Get the full gift catalog via payments.getStarGifts.

        Returns list of gift types, filtered to those with resale availability.
        """
        result = await self.client(functions.payments.GetStarGiftsRequest(hash=0))

        catalog = []
        for gift in getattr(result, 'gifts', []):
            resale = getattr(gift, 'availability_resale', None)
            catalog.append(CatalogGift(
                id=gift.id,
                title=getattr(gift, 'title', None),
                stars=getattr(gift, 'stars', 0),
                availability_resale=resale,
                resell_min_stars=getattr(gift, 'resell_min_stars', None),
                sticker_doc_id=gift.sticker.id if hasattr(gift, 'sticker') and gift.sticker else None,
            ))

        # Only return those with resale
        on_resale = [g for g in catalog if g.availability_resale and g.availability_resale > 0]
        logger.info(
            f"[TelegramIndexer] Catalog: {len(catalog)} gift types, "
            f"{len(on_resale)} with resale ({sum(g.availability_resale for g in on_resale)} total gifts)"
        )
        return on_resale

    async def get_resale_page(
        self,
        gift_id: int,
        offset: str = '',
        limit: int = 100,
    ) -> dict:
        """
        Fetch one page of resale gifts for a gift type.

        Returns dict with keys: gifts, count, next_offset, attributes.
        """
        kwargs = {
            'gift_id': gift_id,
            'offset': offset,
            'limit': limit,
            'sort_by_price': True,
        }
        # Get attributes on first page only
        if offset == '':
            kwargs['attributes_hash'] = 0

        result = await self.client(functions.payments.GetResaleStarGiftsRequest(**kwargs))

        return {
            'gifts': getattr(result, 'gifts', []),
            'count': getattr(result, 'count', 0),
            'next_offset': getattr(result, 'next_offset', None),
            'attributes': getattr(result, 'attributes', []),
        }

    def _parse_resell_amount(self, gift) -> Optional[int]:
        """Extract resale price in stars from gift."""
        amounts = getattr(gift, 'resell_amount', None)
        if not amounts:
            return None
        # resell_amount is a Vector<StarsAmount>
        # Each StarsAmount has .amount (int)
        for amt in amounts:
            stars = getattr(amt, 'amount', None)
            if stars:
                return int(stars)
        return None

    def _parse_unique_gift(self, gift) -> Optional[ParsedGift]:
        """Parse a starGiftUnique into a ParsedGift."""
        if not hasattr(gift, 'slug'):
            return None

        price_stars = self._parse_resell_amount(gift)
        price_ton = Decimal(str(price_stars)) * self.stars_to_ton if price_stars else None

        parsed = ParsedGift(
            unique_id=gift.id,
            gift_id=gift.gift_id,
            title=gift.title,
            slug=gift.slug,
            num=gift.num,
            owner_address=getattr(gift, 'owner_address', None),
            gift_address=getattr(gift, 'gift_address', None),
            price_stars=price_stars,
            price_ton=price_ton,
            availability_issued=getattr(gift, 'availability_issued', 0),
            availability_total=getattr(gift, 'availability_total', 0),
        )

        # Parse attributes
        attrs_raw = []
        model_idx = 0  # Track which document attribute is model vs pattern
        for attr in getattr(gift, 'attributes', []):
            if hasattr(attr, 'backdrop_id'):
                # starGiftAttributeBackdrop
                parsed.backdrop_name = attr.name
                parsed.backdrop_id = attr.backdrop_id
                parsed.backdrop_center_color = int_to_hex(attr.center_color)
                parsed.backdrop_edge_color = int_to_hex(attr.edge_color)
                parsed.backdrop_pattern_color = int_to_hex(attr.pattern_color)
                parsed.backdrop_text_color = int_to_hex(attr.text_color)
                parsed.backdrop_rarity = attr.rarity_permille
                attrs_raw.append({
                    'type': 'backdrop',
                    'name': attr.name,
                    'backdrop_id': attr.backdrop_id,
                    'center_color': parsed.backdrop_center_color,
                    'edge_color': parsed.backdrop_edge_color,
                    'pattern_color': parsed.backdrop_pattern_color,
                    'text_color': parsed.backdrop_text_color,
                    'rarity_permille': attr.rarity_permille,
                })
            elif hasattr(attr, 'document') and hasattr(attr, 'rarity_permille'):
                doc_id = attr.document.id if attr.document else None
                if model_idx == 0:
                    parsed.model_name = attr.name
                    parsed.model_doc_id = doc_id
                    parsed.model_rarity = attr.rarity_permille
                    attrs_raw.append({
                        'type': 'model',
                        'name': attr.name,
                        'document_id': doc_id,
                        'rarity_permille': attr.rarity_permille,
                    })
                else:
                    parsed.pattern_name = attr.name
                    parsed.pattern_doc_id = doc_id
                    parsed.pattern_rarity = attr.rarity_permille
                    attrs_raw.append({
                        'type': 'pattern',
                        'name': attr.name,
                        'document_id': doc_id,
                        'rarity_permille': attr.rarity_permille,
                    })
                model_idx += 1

        parsed.attributes_raw = attrs_raw
        return parsed

    async def iter_resale_gifts(
        self,
        gift_id: int,
        max_pages: int = 100,
    ):
        """
        Iterate through ALL resale gifts for a gift type.

        Yields ParsedGift objects.
        """
        offset = ''
        page = 0

        while page < max_pages:
            page += 1
            data = await self.get_resale_page(gift_id, offset=offset)

            for raw_gift in data['gifts']:
                parsed = self._parse_unique_gift(raw_gift)
                if parsed:
                    yield parsed

            next_offset = data.get('next_offset')
            if not next_offset:
                break

            offset = next_offset
            await asyncio.sleep(self.delay)

    async def fetch_all_resale_gifts(
        self,
        gift_id: int,
        max_items: int = 5000,
    ) -> list[ParsedGift]:
        """Fetch all resale gifts for a gift type into a list."""
        gifts = []
        async for gift in self.iter_resale_gifts(gift_id):
            gifts.append(gift)
            if len(gifts) >= max_items:
                break
        return gifts

    async def fetch_all_on_resale(
        self,
        max_items_per_type: int = 5000,
    ) -> dict[int, list[ParsedGift]]:
        """
        Fetch ALL gifts on resale across ALL gift types.

        Returns dict: gift_type_id -> list of ParsedGift.
        """
        catalog = await self.get_catalog()
        all_gifts = {}

        for gift_type in catalog:
            logger.info(
                f"[TelegramIndexer] Fetching {gift_type.title or gift_type.id} "
                f"({gift_type.availability_resale} on resale)..."
            )
            gifts = await self.fetch_all_resale_gifts(
                gift_type.id,
                max_items=max_items_per_type,
            )
            all_gifts[gift_type.id] = gifts
            logger.info(f"[TelegramIndexer] Got {len(gifts)} gifts for {gift_type.title or gift_type.id}")
            await asyncio.sleep(self.delay)

        total = sum(len(g) for g in all_gifts.values())
        logger.info(f"[TelegramIndexer] Total: {total} gifts across {len(all_gifts)} types")
        return all_gifts

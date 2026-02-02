"""
Backend Escrow — проверка владения NFT и управление ставками.

MVP: без смарт-контрактов, backend как координатор.
"""
import logging
from decimal import Decimal
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.inventory import InventoryService
from app.services.pricing import PricingService
from app.repositories.room_repository import RoomRepository

logger = logging.getLogger(__name__)


class EscrowService:
    """
    Backend escrow for PvP games.

    Flow:
    1. Player selects NFT → backend verifies ownership via TON API
    2. NFT "locked" in DB (can't be used in other rooms)
    3. Game plays → winner determined
    4. Backend records result (actual NFT transfer = TODO)
    """

    def __init__(
        self,
        session: AsyncSession,
        tonapi_key: Optional[str] = None,
    ):
        self.session = session
        self.repo = RoomRepository(session)
        self.inventory = InventoryService(tonapi_key)
        self.pricing = PricingService(tonapi_key)

    async def verify_and_price_nft(
        self,
        wallet_address: str,
        nft_address: str,
    ) -> Optional[Decimal]:
        """
        Verify ownership and return price.

        Returns:
            Price in TON if verified, None if failed.
        """
        # 1. Verify ownership
        owns = await self.inventory.verify_ownership(wallet_address, nft_address)
        if not owns:
            logger.warning(f"Ownership failed: {wallet_address} doesn't own {nft_address}")
            return None

        # 2. Check not already locked
        locked = await self.repo.is_nft_locked(nft_address)
        if locked:
            logger.warning(f"NFT {nft_address} already locked in active room")
            return None

        # 3. Get price
        price = await self.pricing.get_nft_price(nft_address)
        if not price or price <= 0:
            logger.warning(f"Could not determine price for {nft_address}")
            return None

        return price

    async def calculate_payout(
        self,
        total_pool: Decimal,
        house_fee_percent: Decimal,
    ) -> tuple[Decimal, Decimal]:
        """Calculate winner payout after fees."""
        fee = total_pool * (house_fee_percent / Decimal("100"))
        payout = total_pool - fee
        return payout, fee

    async def close(self):
        await self.inventory.close()
        await self.pricing.close()

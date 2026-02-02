"""
Inventory API — инвентарь пользователя и цены NFT.
"""
from decimal import Decimal
from typing import List, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.config import settings
from app.services.inventory import InventoryService
from app.services.pricing import PricingService

router = APIRouter(prefix="/api/pvp/inventory", tags=["Inventory"])


class NFTResponse(BaseModel):
    address: str
    name: str
    collection_name: str
    image_url: Optional[str] = None
    price_ton: Optional[str] = None


@router.get("/user/{wallet_address}", response_model=List[NFTResponse])
async def get_user_inventory(wallet_address: str):
    """Get user's NFT inventory with prices."""
    inventory = InventoryService(tonapi_key=getattr(settings, "TONAPI_KEY", None))
    pricing = PricingService(tonapi_key=getattr(settings, "TONAPI_KEY", None))

    try:
        nfts = await inventory.get_user_nfts(wallet_address)

        results = []
        for nft in nfts:
            price = await pricing.get_nft_price(nft.address)
            results.append(NFTResponse(
                address=nft.address,
                name=nft.name,
                collection_name=nft.collection_name,
                image_url=nft.image_url,
                price_ton=str(price) if price else None,
            ))

        return results
    finally:
        await inventory.close()
        await pricing.close()


@router.get("/verify/{wallet_address}/{nft_address}")
async def verify_ownership(wallet_address: str, nft_address: str):
    """Verify user owns specific NFT."""
    inventory = InventoryService(tonapi_key=getattr(settings, "TONAPI_KEY", None))
    try:
        owns = await inventory.verify_ownership(wallet_address, nft_address)
        return {"owns": owns}
    finally:
        await inventory.close()

"""
User NFT Inventory — получение гифтов пользователя из TON блокчейна.
"""
import logging
from typing import List, Optional
from dataclasses import dataclass, field

import httpx

logger = logging.getLogger(__name__)


@dataclass
class UserNFT:
    """NFT owned by user."""
    address: str
    name: str
    collection_address: str
    collection_name: str
    image_url: Optional[str] = None
    attributes: dict = field(default_factory=dict)


class InventoryService:
    """Fetch user's NFT inventory from TON blockchain via tonapi.io."""

    def __init__(self, tonapi_key: Optional[str] = None):
        headers = {}
        if tonapi_key:
            headers["Authorization"] = f"Bearer {tonapi_key}"
        self.client = httpx.AsyncClient(
            base_url="https://tonapi.io/v2",
            headers=headers,
            timeout=15.0,
        )

    async def get_user_nfts(
        self,
        wallet_address: str,
        collection: Optional[str] = None,
        limit: int = 100,
    ) -> List[UserNFT]:
        """
        Get all NFTs owned by wallet address.

        Args:
            wallet_address: TON wallet address
            collection: Optional collection address filter
            limit: Max results
        """
        try:
            params: dict = {"limit": limit, "indirect_ownership": True}
            if collection:
                params["collection"] = collection

            resp = await self.client.get(
                f"/accounts/{wallet_address}/nfts",
                params=params,
            )
            resp.raise_for_status()
            data = resp.json()

            nfts = []
            for item in data.get("nft_items", []):
                metadata = item.get("metadata") or {}
                previews = item.get("previews") or []
                image_url = previews[0]["url"] if previews else metadata.get("image")

                nft = UserNFT(
                    address=item["address"],
                    name=metadata.get("name", "Unknown Gift"),
                    collection_address=item.get("collection", {}).get("address", ""),
                    collection_name=item.get("collection", {}).get("name", ""),
                    image_url=image_url,
                    attributes={
                        a["trait_type"]: a["value"]
                        for a in metadata.get("attributes", [])
                    },
                )
                nfts.append(nft)

            return nfts

        except Exception as e:
            logger.error(f"Failed to fetch NFTs for {wallet_address}: {e}")
            return []

    async def verify_ownership(
        self,
        wallet_address: str,
        nft_address: str,
    ) -> bool:
        """Verify user still owns specific NFT."""
        try:
            resp = await self.client.get(f"/nfts/{nft_address}")
            resp.raise_for_status()
            data = resp.json()
            owner = data.get("owner", {}).get("address", "")
            return owner == wallet_address
        except Exception as e:
            logger.error(f"Ownership check failed: {e}")
            return False

    async def close(self):
        await self.client.aclose()

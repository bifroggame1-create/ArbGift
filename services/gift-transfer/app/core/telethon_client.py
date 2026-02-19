"""
Telethon MTProto client for Telegram Gift operations.

Handles:
- User authorization
- Gift transfer between users
- Gift ownership verification
- Gift inventory sync from Telegram
"""
import logging
import os
from typing import Optional, List, Dict, Any
from datetime import datetime

from telethon import TelegramClient, functions, types
from telethon.errors import SessionPasswordNeededError
from telethon.tl.custom import Message

logger = logging.getLogger(__name__)


class GiftTelethonClient:
    """
    Wrapper around Telethon for Gift NFT operations.

    Implements Telegram MTProto API methods:
    - payments.getSavedStarGifts - get user's gifts
    - payments.transferStarGift - transfer gift to another user
    - payments.getSavedStarGift - get specific gift details
    """

    def __init__(
        self,
        api_id: int,
        api_hash: str,
        session_name: str = "gift_transfer_session",
        phone: Optional[str] = None,
    ):
        """
        Initialize Telethon client.

        Args:
            api_id: Telegram API ID from my.telegram.org
            api_hash: Telegram API Hash
            session_name: Session file name (saved to disk)
            phone: Phone number for user authorization
        """
        self.api_id = api_id
        self.api_hash = api_hash
        self.session_name = session_name
        self.phone = phone
        self.client: Optional[TelegramClient] = None
        self._is_connected = False

    async def connect(self):
        """Connect to Telegram and authorize if needed."""
        if self._is_connected and self.client:
            return

        logger.info(f"Connecting Telethon client: {self.session_name}")

        self.client = TelegramClient(
            self.session_name,
            self.api_id,
            self.api_hash,
        )

        await self.client.connect()

        # Check authorization
        if not await self.client.is_user_authorized():
            if not self.phone:
                raise ValueError("Phone number required for initial authorization")

            logger.info(f"Starting authorization for {self.phone}")
            await self.client.send_code_request(self.phone)

            # Note: In production, you need to implement a callback
            # to get the verification code from user
            # For now, this will need manual setup
            raise RuntimeError(
                "First-time authorization required. "
                "Please run this service manually with phone authorization, "
                "then restart. Session will be saved."
            )

        self._is_connected = True
        me = await self.client.get_me()
        logger.info(f"Telethon client connected as: {me.username} ({me.id})")

    async def disconnect(self):
        """Disconnect from Telegram."""
        if self.client and self._is_connected:
            await self.client.disconnect()
            self._is_connected = False
            logger.info("Telethon client disconnected")

    async def get_user_gifts(
        self,
        peer: str | int,
        limit: int = 100,
        exclude_unsaved: bool = False,
        exclude_saved: bool = False,
    ) -> List[Dict[str, Any]]:
        """
        Get user's Telegram gifts inventory.

        Args:
            peer: Username, phone, or user_id
            limit: Max gifts to return
            exclude_unsaved: Filter out unsaved gifts
            exclude_saved: Filter out saved gifts

        Returns:
            List of gift dicts with fields: msg_id, slug, name, rarity, etc.
        """
        if not self._is_connected:
            await self.connect()

        logger.info(f"Fetching gifts for peer: {peer}")

        try:
            result = await self.client(
                functions.payments.GetSavedStarGiftsRequest(
                    peer=peer,
                    offset="",
                    limit=limit,
                    exclude_unsaved=exclude_unsaved,
                    exclude_saved=exclude_saved,
                    exclude_unlimited=False,
                    exclude_unique=False,
                    sort_by_value=True,
                    exclude_upgradable=False,
                    exclude_unupgradable=False,
                    peer_color_available=False,
                    exclude_hosted=False,
                    collection_id=None,
                )
            )

            # Parse result
            gifts = []
            if hasattr(result, 'gifts'):
                for gift in result.gifts:
                    gifts.append(self._parse_saved_star_gift(gift))

            logger.info(f"Found {len(gifts)} gifts for peer {peer}")
            return gifts

        except Exception as e:
            logger.error(f"Error fetching gifts for {peer}: {e}", exc_info=True)
            raise

    async def transfer_gift(
        self,
        from_user_id: int,
        to_user_id: int,
        gift_msg_id: int,
    ) -> Dict[str, Any]:
        """
        Transfer a gift from one user to another.

        Args:
            from_user_id: Sender's Telegram user ID
            to_user_id: Recipient's Telegram user ID
            gift_msg_id: Message ID of the gift

        Returns:
            Transfer result dict with status and details

        Raises:
            ValueError: If gift not found or not transferable
            RuntimeError: If transfer fails
        """
        if not self._is_connected:
            await self.connect()

        logger.info(
            f"Transferring gift: msg_id={gift_msg_id} "
            f"from={from_user_id} to={to_user_id}"
        )

        try:
            # Create InputSavedStarGift from msg_id
            stargift = types.InputSavedStarGiftUser(msg_id=gift_msg_id)

            # Transfer the gift
            result = await self.client(
                functions.payments.TransferStarGiftRequest(
                    stargift=stargift,
                    to_id=to_user_id,
                )
            )

            logger.info(f"Gift transferred successfully: {result}")

            return {
                "success": True,
                "msg_id": gift_msg_id,
                "from_user_id": from_user_id,
                "to_user_id": to_user_id,
                "result": str(result),
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(
                f"Error transferring gift msg_id={gift_msg_id}: {e}",
                exc_info=True
            )
            return {
                "success": False,
                "error": str(e),
                "msg_id": gift_msg_id,
                "from_user_id": from_user_id,
                "to_user_id": to_user_id,
            }

    async def verify_gift_ownership(
        self,
        user_id: int,
        gift_slug: str,
    ) -> bool:
        """
        Verify that a user owns a specific gift.

        Args:
            user_id: Telegram user ID
            gift_slug: Unique gift slug

        Returns:
            True if user owns this gift, False otherwise
        """
        if not self._is_connected:
            await self.connect()

        try:
            # Get user's gifts
            gifts = await self.get_user_gifts(user_id, limit=500)

            # Check if gift_slug is in the list
            for gift in gifts:
                if gift.get("slug") == gift_slug:
                    logger.info(f"Ownership verified: user={user_id} owns {gift_slug}")
                    return True

            logger.warning(f"Ownership denied: user={user_id} does not own {gift_slug}")
            return False

        except Exception as e:
            logger.error(
                f"Error verifying ownership for user={user_id} gift={gift_slug}: {e}",
                exc_info=True
            )
            return False

    async def get_gift_details(
        self,
        user_id: int,
        gift_msg_id: int,
    ) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific gift.

        Args:
            user_id: Owner's Telegram user ID
            gift_msg_id: Gift message ID

        Returns:
            Gift details dict or None if not found
        """
        if not self._is_connected:
            await self.connect()

        try:
            stargift = types.InputSavedStarGiftUser(msg_id=gift_msg_id)

            result = await self.client(
                functions.payments.GetSavedStarGiftRequest(
                    peer=user_id,
                    stargift=stargift,
                )
            )

            if hasattr(result, 'gift'):
                return self._parse_saved_star_gift(result.gift)

            return None

        except Exception as e:
            logger.error(
                f"Error getting gift details msg_id={gift_msg_id}: {e}",
                exc_info=True
            )
            return None

    def _parse_saved_star_gift(self, gift: Any) -> Dict[str, Any]:
        """Parse Telegram SavedStarGift object to dict."""
        # Extract common fields
        data = {
            "msg_id": getattr(gift, "msg_id", None),
            "slug": getattr(gift, "slug", None),
            "title": getattr(gift, "title", None),
            "num": getattr(gift, "num", None),
            "transfer_stars": getattr(gift, "transfer_stars", 0),
            "can_upgrade": getattr(gift, "can_upgrade", False),
            "can_export": getattr(gift, "can_export", False),
            "unsaved": getattr(gift, "unsaved", False),
        }

        # Extract gift_id if available
        if hasattr(gift, "gift"):
            gift_obj = gift.gift
            data["gift_id"] = getattr(gift_obj, "id", None)
            data["gift_type"] = type(gift_obj).__name__

            # For unique gifts
            if hasattr(gift_obj, "slug"):
                data["unique_slug"] = gift_obj.slug
            if hasattr(gift_obj, "owner_id"):
                data["owner_id"] = gift_obj.owner_id

        return data

    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.disconnect()


# Singleton instance
_client_instance: Optional[GiftTelethonClient] = None


async def get_telethon_client() -> GiftTelethonClient:
    """
    Get or create singleton Telethon client.

    Reads credentials from environment variables.
    """
    global _client_instance

    if _client_instance is None:
        api_id = int(os.getenv("TELEGRAM_API_ID"))
        api_hash = os.getenv("TELEGRAM_API_HASH")
        session_name = os.getenv("TELEGRAM_SESSION_NAME", "gift_transfer_session")
        phone = os.getenv("TELEGRAM_PHONE")

        if not api_id or not api_hash:
            raise ValueError(
                "TELEGRAM_API_ID and TELEGRAM_API_HASH must be set in environment"
            )

        _client_instance = GiftTelethonClient(
            api_id=api_id,
            api_hash=api_hash,
            session_name=session_name,
            phone=phone,
        )

        await _client_instance.connect()

    return _client_instance

"""
Gift Transfer Microservice - MTProto Integration

Handles Telegram Gift NFT operations via MTProto API:
- Gift inventory sync from Telegram
- Gift transfers between users
- Ownership verification
"""
import logging
import os
from contextlib import asynccontextmanager
from typing import Optional, List

from fastapi import FastAPI, HTTPException, Header, Depends
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from app.core.telethon_client import get_telethon_client, GiftTelethonClient

# Load environment
load_dotenv()

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


# ============================================================
# SCHEMAS
# ============================================================

class SyncUserGiftsRequest(BaseModel):
    """Request to sync user's gifts from Telegram."""
    telegram_user_id: int = Field(..., description="Telegram user ID")
    limit: int = Field(100, ge=1, le=500, description="Max gifts to fetch")


class TransferGiftRequest(BaseModel):
    """Request to transfer a gift."""
    from_user_id: int = Field(..., description="Sender Telegram ID")
    to_user_id: int = Field(..., description="Recipient Telegram ID")
    gift_msg_id: int = Field(..., description="Gift message ID from Telegram")


class VerifyOwnershipRequest(BaseModel):
    """Request to verify gift ownership."""
    user_id: int = Field(..., description="Telegram user ID")
    gift_slug: str = Field(..., description="Unique gift slug")


class GiftDetailsRequest(BaseModel):
    """Request to get gift details."""
    user_id: int = Field(..., description="Owner Telegram ID")
    gift_msg_id: int = Field(..., description="Gift message ID")


# ============================================================
# DEPENDENCIES
# ============================================================

def verify_admin_key(x_admin_key: str = Header(None)):
    """Verify admin key for service authentication."""
    admin_key = os.getenv("ADMIN_SECRET_KEY")
    if not admin_key or x_admin_key != admin_key:
        raise HTTPException(status_code=403, detail="Invalid admin key")
    return True


# ============================================================
# LIFESPAN
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info("Starting Gift Transfer Service...")

    # Initialize Telethon client
    try:
        client = await get_telethon_client()
        logger.info("Telethon client initialized")
    except RuntimeError as e:
        logger.error(f"Telethon initialization failed: {e}")
        logger.error(
            "If this is first run, please authorize manually:\n"
            "1. cd services/gift-transfer\n"
            "2. python -c 'from app.core.telethon_client import get_telethon_client; import asyncio; asyncio.run(get_telethon_client())'\n"
            "3. Enter phone code when prompted\n"
            "4. Restart this service"
        )

    yield

    # Shutdown
    logger.info("Shutting down...")
    try:
        client = await get_telethon_client()
        await client.disconnect()
    except Exception:
        pass
    logger.info("Shutdown complete")


# ============================================================
# APP
# ============================================================

app = FastAPI(
    title="Gift Transfer Service",
    version="1.0.0",
    description="Telegram Gift NFT operations via MTProto API",
    lifespan=lifespan,
)


# ============================================================
# ENDPOINTS
# ============================================================

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    client = await get_telethon_client()
    return {
        "status": "healthy",
        "service": "gift-transfer",
        "telethon_connected": client._is_connected,
    }


@app.post("/sync-user-gifts", dependencies=[Depends(verify_admin_key)])
async def sync_user_gifts(request: SyncUserGiftsRequest):
    """
    Sync user's gift inventory from Telegram.

    Returns list of gifts owned by user from Telegram MTProto API.
    Main API service will use this to populate UserGiftInventory table.
    """
    try:
        client = await get_telethon_client()
        gifts = await client.get_user_gifts(
            peer=request.telegram_user_id,
            limit=request.limit,
        )

        logger.info(f"Synced {len(gifts)} gifts for user {request.telegram_user_id}")

        return {
            "success": True,
            "user_id": request.telegram_user_id,
            "gifts_count": len(gifts),
            "gifts": gifts,
        }

    except Exception as e:
        logger.error(f"Error syncing gifts for user {request.telegram_user_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/transfer-gift", dependencies=[Depends(verify_admin_key)])
async def transfer_gift(request: TransferGiftRequest):
    """
    Transfer a gift from one user to another via Telegram.

    This performs the actual Telegram MTProto API call to transfer ownership.
    Called by main API when game ends or P2P trade completes.
    """
    try:
        client = await get_telethon_client()
        result = await client.transfer_gift(
            from_user_id=request.from_user_id,
            to_user_id=request.to_user_id,
            gift_msg_id=request.gift_msg_id,
        )

        if result.get("success"):
            logger.info(
                f"Gift transferred: msg_id={request.gift_msg_id} "
                f"from={request.from_user_id} to={request.to_user_id}"
            )
            return result
        else:
            logger.error(f"Gift transfer failed: {result}")
            raise HTTPException(status_code=400, detail=result.get("error"))

    except Exception as e:
        logger.error(f"Error transferring gift: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/verify-ownership", dependencies=[Depends(verify_admin_key)])
async def verify_ownership(request: VerifyOwnershipRequest):
    """
    Verify that a user owns a specific gift in Telegram.

    Returns True if user owns the gift, False otherwise.
    Used for security checks before allowing bets or transfers.
    """
    try:
        client = await get_telethon_client()
        owns_gift = await client.verify_gift_ownership(
            user_id=request.user_id,
            gift_slug=request.gift_slug,
        )

        return {
            "user_id": request.user_id,
            "gift_slug": request.gift_slug,
            "owns_gift": owns_gift,
        }

    except Exception as e:
        logger.error(f"Error verifying ownership: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/gift-details", dependencies=[Depends(verify_admin_key)])
async def get_gift_details(request: GiftDetailsRequest):
    """
    Get detailed information about a specific gift from Telegram.

    Returns gift metadata including transferability, upgrade status, etc.
    """
    try:
        client = await get_telethon_client()
        details = await client.get_gift_details(
            user_id=request.user_id,
            gift_msg_id=request.gift_msg_id,
        )

        if not details:
            raise HTTPException(status_code=404, detail="Gift not found")

        return {
            "success": True,
            "gift": details,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting gift details: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
async def root():
    """Service info."""
    return {
        "service": "Gift Transfer MTProto Service",
        "version": "1.0.0",
        "endpoints": {
            "/sync-user-gifts": "Sync user's gifts from Telegram",
            "/transfer-gift": "Transfer gift between users",
            "/verify-ownership": "Verify gift ownership",
            "/gift-details": "Get gift details",
        },
        "authentication": "Requires X-Admin-Key header",
    }


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("SERVICE_PORT", 8010))
    debug = os.getenv("DEBUG", "false").lower() == "true"

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=debug,
    )

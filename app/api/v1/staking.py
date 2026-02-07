"""
Staking API proxy endpoints.

Proxies requests to the Staking microservice (port 8001).
Provides unified API for frontend to access staking functionality.
"""
import logging
from decimal import Decimal
from datetime import datetime
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Header
import httpx
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)
router = APIRouter()

# Staking service URL (microservice)
STAKING_SERVICE_URL = "http://localhost:8001"
STAKING_SERVICE_TIMEOUT = 30.0


# ============================================================
# SCHEMAS
# ============================================================

class StakeCreateRequest(BaseModel):
    """Create stake request."""
    gift_address: str = Field(..., description="NFT address to stake")
    gift_value_ton: Decimal = Field(..., description="Gift value in TON")
    gift_rarity: Optional[str] = Field(None, description="Gift rarity (common, rare, legendary, etc.)")
    period: str = Field(..., description="Stake period: WEEK_1, WEEK_2, MONTH_1, MONTH_3")
    auto_compound: bool = Field(False, description="Auto-compound rewards")


class StakeSchema(BaseModel):
    """Stake response schema."""
    id: int
    user_id: int
    gift_address: str
    gift_value_ton: Decimal
    gift_rarity: Optional[str]

    # Period & APY
    period: str
    days: int
    apy_percent: Decimal
    rarity_multiplier: Decimal
    collection_set_bonus: Decimal
    effective_apy_percent: Decimal

    # Rewards
    expected_reward_ton: Decimal
    claimed_reward_ton: Decimal

    # Dates
    staked_at: datetime
    unlock_at: datetime
    claimed_at: Optional[datetime]

    # Status
    status: str
    is_active: bool
    auto_compound: bool

    class Config:
        from_attributes = True


class StakeListResponse(BaseModel):
    """Paginated stake list."""
    total: int
    active_count: int
    completed_count: int
    total_staked_value_ton: Decimal
    total_rewards_ton: Decimal
    stakes: List[StakeSchema]


class StakeStatsSchema(BaseModel):
    """User staking statistics."""
    total_stakes_count: int
    active_stakes_count: int
    completed_stakes_count: int

    total_staked_value_ton: Decimal
    total_rewards_earned_ton: Decimal
    total_rewards_pending_ton: Decimal

    average_apy: Decimal
    best_apy: Decimal


class PlatformStatsSchema(BaseModel):
    """Platform-wide staking statistics."""
    total_value_locked_ton: Decimal
    total_rewards_paid_ton: Decimal
    active_stakers_count: int
    total_stakes_count: int

    current_apy_min: Decimal
    current_apy_max: Decimal
    average_stake_duration_days: int


# ============================================================
# HELPERS
# ============================================================

async def proxy_to_staking_service(
    method: str,
    path: str,
    telegram_id: Optional[int] = None,
    json_data: Optional[dict] = None,
    params: Optional[dict] = None,
) -> dict:
    """
    Proxy request to staking microservice.

    Args:
        method: HTTP method (GET, POST, etc.)
        path: API path (e.g., "/stakes")
        telegram_id: User's Telegram ID for authentication
        json_data: JSON request body
        params: Query parameters

    Returns:
        Response JSON from staking service
    """
    url = f"{STAKING_SERVICE_URL}{path}"
    headers = {}

    if telegram_id:
        headers["X-Telegram-User-Id"] = str(telegram_id)

    async with httpx.AsyncClient(timeout=STAKING_SERVICE_TIMEOUT) as client:
        try:
            response = await client.request(
                method=method,
                url=url,
                headers=headers,
                json=json_data,
                params=params,
            )
            response.raise_for_status()
            return response.json()

        except httpx.HTTPStatusError as e:
            # Pass through HTTP errors from staking service
            logger.error(f"Staking service error: {e.response.status_code} - {e.response.text}")
            raise HTTPException(
                status_code=e.response.status_code,
                detail=e.response.text
            )
        except httpx.RequestError as e:
            # Network/connection errors
            logger.error(f"Failed to connect to staking service: {e}")
            raise HTTPException(
                status_code=503,
                detail="Staking service unavailable"
            )


# ============================================================
# ENDPOINTS
# ============================================================

@router.post("/stakes", response_model=StakeSchema, status_code=201)
async def create_stake(
    request: StakeCreateRequest,
    telegram_id: int = Header(..., alias="X-Telegram-User-Id"),
):
    """
    Create new stake.

    Stakes an NFT gift for a specific period to earn rewards.
    Calculates APY based on period, rarity, and collection bonuses.
    """
    data = await proxy_to_staking_service(
        method="POST",
        path="/stakes",
        telegram_id=telegram_id,
        json_data=request.dict(),
    )
    return data


@router.get("/stakes", response_model=StakeListResponse)
async def get_user_stakes(
    telegram_id: int = Header(..., alias="X-Telegram-User-Id"),
    status: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
):
    """
    Get user's stakes.

    Query parameters:
    - status: Filter by status (active, completed, claimed)
    - limit: Max results
    - offset: Pagination offset
    """
    params = {
        "status": status,
        "limit": limit,
        "offset": offset,
    }

    data = await proxy_to_staking_service(
        method="GET",
        path="/stakes",
        telegram_id=telegram_id,
        params=params,
    )
    return data


@router.get("/stakes/{stake_id}", response_model=StakeSchema)
async def get_stake_detail(
    stake_id: int,
    telegram_id: int = Header(..., alias="X-Telegram-User-Id"),
):
    """
    Get stake details by ID.

    Includes current reward amount, unlock time, and status.
    """
    data = await proxy_to_staking_service(
        method="GET",
        path=f"/stakes/{stake_id}",
        telegram_id=telegram_id,
    )
    return data


@router.post("/stakes/{stake_id}/claim", response_model=StakeSchema)
async def claim_stake_rewards(
    stake_id: int,
    telegram_id: int = Header(..., alias="X-Telegram-User-Id"),
):
    """
    Claim stake rewards.

    - Stake must be completed (unlock_at passed)
    - Rewards transferred to user balance
    - Gift NFT returned to user
    """
    data = await proxy_to_staking_service(
        method="POST",
        path=f"/stakes/{stake_id}/claim",
        telegram_id=telegram_id,
    )
    return data


@router.post("/stakes/{stake_id}/compound", response_model=StakeSchema)
async def compound_stake_rewards(
    stake_id: int,
    telegram_id: int = Header(..., alias="X-Telegram-User-Id"),
):
    """
    Compound stake rewards.

    - Adds earned rewards to principal
    - Extends stake period
    - Increases future rewards
    """
    data = await proxy_to_staking_service(
        method="POST",
        path=f"/stakes/{stake_id}/compound",
        telegram_id=telegram_id,
    )
    return data


@router.delete("/stakes/{stake_id}")
async def cancel_stake(
    stake_id: int,
    telegram_id: int = Header(..., alias="X-Telegram-User-Id"),
):
    """
    Cancel stake (emergency unstake).

    - Available before unlock time
    - May incur early withdrawal penalty
    - Returns gift immediately
    """
    data = await proxy_to_staking_service(
        method="DELETE",
        path=f"/stakes/{stake_id}",
        telegram_id=telegram_id,
    )
    return data


@router.get("/stakes/me/stats", response_model=StakeStatsSchema)
async def get_user_staking_stats(
    telegram_id: int = Header(..., alias="X-Telegram-User-Id"),
):
    """
    Get user's staking statistics.

    Returns comprehensive stats about user's staking activity.
    """
    data = await proxy_to_staking_service(
        method="GET",
        path="/stakes/me/stats",
        telegram_id=telegram_id,
    )
    return data


@router.get("/platform/stats", response_model=PlatformStatsSchema)
async def get_platform_stats():
    """
    Get platform-wide staking statistics.

    Public endpoint showing total value locked, rewards paid, etc.
    """
    data = await proxy_to_staking_service(
        method="GET",
        path="/platform/stats",
    )
    return data


@router.get("/apy/rates")
async def get_apy_rates():
    """
    Get current APY rates by period.

    Returns:
    - Base APY for each staking period
    - Rarity multipliers
    - Collection set bonuses
    """
    data = await proxy_to_staking_service(
        method="GET",
        path="/apy/rates",
    )
    return data


@router.get("/apy/calculate")
async def calculate_potential_apy(
    gift_value_ton: Decimal,
    period: str,
    rarity: Optional[str] = None,
    collection_bonus: Decimal = Decimal("0"),
):
    """
    Calculate potential APY for a stake.

    Query parameters:
    - gift_value_ton: Value of gift to stake
    - period: Staking period (WEEK_1, WEEK_2, MONTH_1, MONTH_3)
    - rarity: Gift rarity (common, rare, legendary, etc.)
    - collection_bonus: Additional bonus from collection sets

    Returns estimated rewards and effective APY.
    """
    params = {
        "gift_value_ton": float(gift_value_ton),
        "period": period,
        "rarity": rarity,
        "collection_bonus": float(collection_bonus),
    }

    data = await proxy_to_staking_service(
        method="GET",
        path="/apy/calculate",
        params=params,
    )
    return data

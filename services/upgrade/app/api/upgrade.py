from datetime import datetime
from decimal import Decimal
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.models import Upgrade, UpgradeStatus, User
from app.services import UpgradeEngine
from app.database import get_db

router = APIRouter(prefix="/upgrade", tags=["Upgrade"])


# Request/Response Models
class CalculateUpgradeRequest(BaseModel):
    """Request to calculate upgrade probability"""

    input_gift_id: int
    target_gift_id: int


class CalculateUpgradeResponse(BaseModel):
    """Response with probability calculation"""

    input_value: str  # Decimal as string
    target_value: str
    success_probability: float
    wheel_sectors: dict  # {success_angle, fail_angle}
    expected_value: str  # Decimal as string


class CreateUpgradeRequest(BaseModel):
    """Request to create upgrade"""

    input_gift_id: int
    target_gift_id: int
    client_seed: str = Field(..., min_length=8, max_length=64)


class CreateUpgradeResponse(BaseModel):
    """Response after creating upgrade"""

    upgrade_id: UUID
    server_seed_hash: str
    probability: float
    wheel_sectors: dict


class SpinWheelResponse(BaseModel):
    """Response after spinning wheel"""

    success: bool
    won: bool
    result_angle: float
    server_seed: str  # Revealed
    animation_duration: int  # milliseconds


class UpgradeHistoryItem(BaseModel):
    """Single upgrade in history"""

    id: UUID
    won: bool
    input_gift_value_ton: str
    target_gift_value_ton: str
    success_probability: float
    created_at: datetime
    resolved_at: datetime | None


class UpgradeHistoryResponse(BaseModel):
    """Upgrade history with pagination"""

    upgrades: List[UpgradeHistoryItem]
    total: int
    offset: int
    limit: int


# Helper functions
async def get_or_create_user(telegram_id: int, db: AsyncSession) -> User:
    """Get existing user or create new one"""
    result = await db.execute(select(User).where(User.telegram_id == telegram_id))
    user = result.scalar_one_or_none()

    if not user:
        user = User(telegram_id=telegram_id)
        db.add(user)
        await db.flush()

    return user


async def get_current_user_id() -> int:
    """
    Get current user's Telegram ID from auth.
    TODO: Implement real authentication
    """
    return 123456789


# API Endpoints

@router.post("/calculate", response_model=CalculateUpgradeResponse)
async def calculate_upgrade_probability(
    request: CalculateUpgradeRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Calculate probability for upgrading between two gifts.

    Does not create an upgrade, just calculates the odds.
    """
    # TODO: Fetch gift values from main app API/database
    # Mock values for now
    input_value = Decimal("5.5")
    target_value = Decimal("12.3")

    # Validate upgrade
    is_valid, error_msg = UpgradeEngine.validate_upgrade(input_value, target_value)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=error_msg
        )

    # Calculate probability
    probability = UpgradeEngine.calculate_success_probability(
        input_value, target_value
    )

    # Generate wheel sectors
    wheel_sectors = UpgradeEngine.generate_wheel_sectors(probability)

    # Calculate expected value
    expected_value = UpgradeEngine.calculate_expected_value(input_value, target_value)

    return CalculateUpgradeResponse(
        input_value=str(input_value),
        target_value=str(target_value),
        success_probability=float(probability),
        wheel_sectors=wheel_sectors,
        expected_value=str(expected_value),
    )


@router.post("/create", response_model=CreateUpgradeResponse)
async def create_upgrade(
    request: CreateUpgradeRequest,
    telegram_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new upgrade (does not execute yet).

    Stores the upgrade with hashed server seed and returns probability info.
    User must call /spin to execute.
    """
    # Get or create user
    user = await get_or_create_user(telegram_id, db)

    # TODO: Fetch gift values from main app
    input_value = Decimal("5.5")
    target_value = Decimal("12.3")

    # Validate
    is_valid, error_msg = UpgradeEngine.validate_upgrade(input_value, target_value)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=error_msg
        )

    # Generate seeds
    server_seed = UpgradeEngine.generate_server_seed()
    server_seed_hash = UpgradeEngine.hash_server_seed(server_seed)

    # Calculate probability
    probability = UpgradeEngine.calculate_success_probability(
        input_value, target_value
    )

    # Create upgrade
    upgrade = Upgrade(
        user_id=user.id,
        input_gift_id=request.input_gift_id,
        input_gift_value_ton=input_value,
        target_gift_id=request.target_gift_id,
        target_gift_value_ton=target_value,
        value_difference=target_value - input_value,
        success_probability=probability,
        server_seed_hash=server_seed_hash,
        server_seed=server_seed,  # Store but don't reveal
        client_seed=request.client_seed,
        nonce=1,
        status=UpgradeStatus.PENDING,
    )

    db.add(upgrade)
    await db.commit()
    await db.refresh(upgrade)

    # Generate wheel sectors
    wheel_sectors = UpgradeEngine.generate_wheel_sectors(probability)

    return CreateUpgradeResponse(
        upgrade_id=upgrade.id,
        server_seed_hash=server_seed_hash,
        probability=float(probability),
        wheel_sectors=wheel_sectors,
    )


@router.post("/{upgrade_id}/spin", response_model=SpinWheelResponse)
async def spin_wheel(
    upgrade_id: UUID,
    telegram_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    Execute upgrade by spinning the wheel.

    Generates provably fair result and reveals server seed.
    """
    # Load upgrade
    result = await db.execute(select(Upgrade).where(Upgrade.id == upgrade_id))
    upgrade = result.scalar_one_or_none()

    if not upgrade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Upgrade not found"
        )

    # Verify ownership
    user = await get_or_create_user(telegram_id, db)
    if upgrade.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to spin this upgrade",
        )

    # Verify pending
    if upgrade.status != UpgradeStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Upgrade already spun",
        )

    # Generate result
    won, result_angle = UpgradeEngine.generate_result(
        upgrade.server_seed,
        upgrade.client_seed,
        upgrade.nonce,
        upgrade.success_probability,
    )

    # Update upgrade
    upgrade.won = won
    upgrade.status = UpgradeStatus.SUCCESS if won else UpgradeStatus.FAILED
    upgrade.result_angle = result_angle
    upgrade.resolved_at = datetime.utcnow()

    # Update user stats
    user.total_upgrades += 1
    user.total_value_risked_ton += upgrade.input_gift_value_ton
    if won:
        user.upgrades_won += 1
        user.total_value_won_ton += upgrade.target_gift_value_ton

    await db.commit()
    await db.refresh(upgrade)

    # Animation duration (3 seconds for wheel spin)
    animation_duration = 3000

    return SpinWheelResponse(
        success=True,
        won=won,
        result_angle=float(result_angle),
        server_seed=upgrade.server_seed,
        animation_duration=animation_duration,
    )


@router.get("/history", response_model=UpgradeHistoryResponse)
async def get_upgrade_history(
    limit: int = 20,
    offset: int = 0,
    telegram_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Get user's upgrade history"""
    user = await get_or_create_user(telegram_id, db)

    # Get total count
    total_result = await db.execute(
        select(Upgrade).where(Upgrade.user_id == user.id)
    )
    total = len(total_result.all())

    # Get paginated upgrades
    result = await db.execute(
        select(Upgrade)
        .where(Upgrade.user_id == user.id)
        .order_by(desc(Upgrade.created_at))
        .limit(limit)
        .offset(offset)
    )
    upgrades = result.scalars().all()

    items = [
        UpgradeHistoryItem(
            id=u.id,
            won=u.won or False,
            input_gift_value_ton=str(u.input_gift_value_ton),
            target_gift_value_ton=str(u.target_gift_value_ton),
            success_probability=float(u.success_probability),
            created_at=u.created_at,
            resolved_at=u.resolved_at,
        )
        for u in upgrades
    ]

    return UpgradeHistoryResponse(
        upgrades=items, total=total, offset=offset, limit=limit
    )

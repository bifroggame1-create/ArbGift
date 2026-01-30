from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.models import Contract, ContractStatus, RiskLevel, User
from app.services import ContractProbabilityEngine, RewardManager
from app.database import get_db

router = APIRouter(prefix="/contracts", tags=["Contracts"])


# Request/Response Models
class CreateContractRequest(BaseModel):
    """Request to create a new contract"""

    gift_ids: List[int] = Field(..., min_items=2, max_items=10)
    risk_level: RiskLevel
    client_seed: str = Field(..., min_length=8, max_length=64)


class CreateContractResponse(BaseModel):
    """Response after creating contract"""

    contract_id: UUID
    server_seed_hash: str
    estimated_probability: float
    potential_payout: str  # Decimal as string


class ExecuteContractResponse(BaseModel):
    """Response after executing contract"""

    success: bool
    won: bool
    multiplier: float
    payout_value: str  # Decimal as string
    reward_gift_id: Optional[int]
    server_seed: str  # Revealed after execution
    proof: dict  # Verification data


class ContractHistoryItem(BaseModel):
    """Single contract in history"""

    id: UUID
    risk_level: str
    won: bool
    total_input_value_ton: str
    payout_value_ton: Optional[str]
    created_at: datetime
    resolved_at: Optional[datetime]


class ContractHistoryResponse(BaseModel):
    """Contract history with pagination"""

    contracts: List[ContractHistoryItem]
    total: int
    offset: int
    limit: int


class VerifyContractResponse(BaseModel):
    """Contract verification result"""

    valid: bool
    server_seed: str
    client_seed: str
    nonce: int
    risk_level: str
    result_won: bool
    verification_hash: str


# Helper function to get or create user
async def get_or_create_user(telegram_id: int, db: AsyncSession) -> User:
    """Get existing user or create new one"""
    result = await db.execute(select(User).where(User.telegram_id == telegram_id))
    user = result.scalar_one_or_none()

    if not user:
        user = User(telegram_id=telegram_id)
        db.add(user)
        await db.flush()

    return user


# Dependency for getting current user (mock - replace with real auth)
async def get_current_user_id() -> int:
    """
    Get current user's Telegram ID from auth token.
    TODO: Implement real authentication with JWT/session
    """
    # Mock user ID for development
    return 123456789


# API Endpoints

@router.post("/create", response_model=CreateContractResponse)
async def create_contract(
    request: CreateContractRequest,
    telegram_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new contract with selected gifts and risk level.

    This endpoint:
    1. Validates gift selection
    2. Calculates total input value
    3. Generates server seed (hashed)
    4. Stores contract in database
    5. Returns contract ID and probability info
    """
    # Get or create user
    user = await get_or_create_user(telegram_id, db)

    # TODO: Fetch gift values from main app API/database
    # For now, use mock values
    total_value = Decimal("10.5")  # Mock total value

    # Validate selection
    is_valid, error_msg = ContractProbabilityEngine.validate_gift_selection(
        len(request.gift_ids), total_value, request.risk_level
    )

    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=error_msg
        )

    # Generate provably fair seeds
    server_seed = ContractProbabilityEngine.generate_server_seed()
    server_seed_hash = ContractProbabilityEngine.hash_server_seed(server_seed)

    # Calculate probability and payout
    probability = ContractProbabilityEngine.calculate_success_probability(
        request.risk_level, total_value
    )
    potential_payout = ContractProbabilityEngine.calculate_payout(
        total_value, request.risk_level
    )

    # Create contract
    contract = Contract(
        user_id=user.id,
        risk_level=request.risk_level,
        input_gift_ids=request.gift_ids,
        total_input_value_ton=total_value,
        server_seed_hash=server_seed_hash,
        server_seed=server_seed,  # Store but don't reveal until execution
        client_seed=request.client_seed,
        nonce=1,
        status=ContractStatus.PENDING,
    )

    db.add(contract)
    await db.commit()
    await db.refresh(contract)

    return CreateContractResponse(
        contract_id=contract.id,
        server_seed_hash=server_seed_hash,
        estimated_probability=float(probability),
        potential_payout=str(potential_payout),
    )


@router.post("/{contract_id}/execute", response_model=ExecuteContractResponse)
async def execute_contract(
    contract_id: UUID,
    telegram_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    Execute a pending contract and reveal result.

    This endpoint:
    1. Loads contract from database
    2. Generates provably fair result
    3. Selects reward gift if won
    4. Updates user statistics
    5. Returns result with revealed server seed
    """
    # Load contract
    result = await db.execute(select(Contract).where(Contract.id == contract_id))
    contract = result.scalar_one_or_none()

    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contract not found"
        )

    # Verify ownership
    user = await get_or_create_user(telegram_id, db)
    if contract.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to execute this contract",
        )

    # Verify contract is pending
    if contract.status != ContractStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Contract already executed",
        )

    # Generate result
    won = ContractProbabilityEngine.generate_result(
        contract.server_seed, contract.client_seed, contract.nonce, contract.risk_level
    )

    # Calculate payout
    multiplier = ContractProbabilityEngine.get_multiplier(contract.risk_level)
    payout_value = (
        ContractProbabilityEngine.calculate_payout(
            contract.total_input_value_ton, contract.risk_level
        )
        if won
        else Decimal("0")
    )

    # Select reward gift if won
    reward_gift_id = None
    if won:
        reward_gift_id = await RewardManager.select_reward_gift(
            contract.total_input_value_ton, multiplier, contract.risk_level.value
        )

    # Update contract
    contract.won = won
    contract.status = ContractStatus.SUCCESS if won else ContractStatus.FAILED
    contract.payout_multiplier = multiplier
    contract.payout_value_ton = payout_value
    contract.reward_gift_id = reward_gift_id
    contract.resolved_at = datetime.utcnow()

    # Update user stats
    user.total_contracts += 1
    user.total_wagered_ton += contract.total_input_value_ton
    if won:
        user.contracts_won += 1
        user.total_won_ton += payout_value

    await db.commit()
    await db.refresh(contract)

    # Prepare proof data
    proof = {
        "server_seed_hash": contract.server_seed_hash,
        "server_seed": contract.server_seed,
        "client_seed": contract.client_seed,
        "nonce": contract.nonce,
        "risk_level": contract.risk_level.value,
    }

    return ExecuteContractResponse(
        success=True,
        won=won,
        multiplier=float(multiplier),
        payout_value=str(payout_value),
        reward_gift_id=reward_gift_id,
        server_seed=contract.server_seed,
        proof=proof,
    )


@router.get("/history", response_model=ContractHistoryResponse)
async def get_contract_history(
    limit: int = 20,
    offset: int = 0,
    telegram_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Get user's contract history with pagination"""
    user = await get_or_create_user(telegram_id, db)

    # Get total count
    total_result = await db.execute(
        select(Contract).where(Contract.user_id == user.id)
    )
    total = len(total_result.all())

    # Get paginated contracts
    result = await db.execute(
        select(Contract)
        .where(Contract.user_id == user.id)
        .order_by(desc(Contract.created_at))
        .limit(limit)
        .offset(offset)
    )
    contracts = result.scalars().all()

    items = [
        ContractHistoryItem(
            id=c.id,
            risk_level=c.risk_level.value,
            won=c.won or False,
            total_input_value_ton=str(c.total_input_value_ton),
            payout_value_ton=str(c.payout_value_ton) if c.payout_value_ton else None,
            created_at=c.created_at,
            resolved_at=c.resolved_at,
        )
        for c in contracts
    ]

    return ContractHistoryResponse(
        contracts=items, total=total, offset=offset, limit=limit
    )


@router.get("/{contract_id}/verify", response_model=VerifyContractResponse)
async def verify_contract(contract_id: UUID, db: AsyncSession = Depends(get_db)):
    """
    Verify provably fair result of a contract.

    Public endpoint that allows anyone to verify a contract's fairness
    after the server seed has been revealed.
    """
    # Load contract
    result = await db.execute(select(Contract).where(Contract.id == contract_id))
    contract = result.scalar_one_or_none()

    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contract not found"
        )

    if contract.status == ContractStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Contract not yet executed - server seed not revealed",
        )

    # Verify result
    is_valid = ContractProbabilityEngine.verify_result(
        contract.server_seed,
        contract.client_seed,
        contract.nonce,
        contract.risk_level,
        contract.won,
    )

    # Generate verification hash
    combined = f"{contract.server_seed}:{contract.client_seed}:{contract.nonce}"
    verification_hash = ContractProbabilityEngine.hash_server_seed(combined)

    return VerifyContractResponse(
        valid=is_valid,
        server_seed=contract.server_seed,
        client_seed=contract.client_seed,
        nonce=contract.nonce,
        risk_level=contract.risk_level.value,
        result_won=contract.won,
        verification_hash=verification_hash,
    )

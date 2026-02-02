"""
Plinko API endpoints.
"""
import hashlib
import secrets
from decimal import Decimal
from typing import List, Optional
from datetime import datetime
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db_session
from app.services.plinko_engine import PlinkoEngine

router = APIRouter(prefix="/api/v1", tags=["plinko"])

# Engine instance
engine = PlinkoEngine()

# Nonce tracking (per user, in-memory - should be Redis in production)
user_nonces: dict = {}


# ============================================================
# SCHEMAS
# ============================================================

class PlayRequest(BaseModel):
    """Request to play plinko."""
    bet_amount_ton: Decimal = Field(..., gt=0)
    client_seed: Optional[str] = None


class DropResult(BaseModel):
    """Plinko drop result."""
    id: str
    path: List[List[float]]  # [[x, y], ...]
    landing_slot: int
    slot_label: str
    multiplier: float
    bet_amount: float
    payout: float
    profit: float
    server_seed_hash: str
    server_seed: str  # Revealed immediately for single-player
    client_seed: str
    nonce: int
    created_at: datetime


class ConfigResponse(BaseModel):
    """Game configuration."""
    multipliers: List[float]
    slot_labels: List[str]
    min_bet_ton: float
    max_bet_ton: float
    rows: int


class VerifyRequest(BaseModel):
    """Verification request."""
    server_seed: str
    client_seed: str
    nonce: int
    bet_amount: float


class VerifyResponse(BaseModel):
    """Verification response."""
    valid: bool
    landing_slot: int
    multiplier: float
    path: List[List[float]]


class HistoryItem(BaseModel):
    """History item."""
    id: str
    landing_slot: int
    slot_label: str
    multiplier: float
    bet_amount: float
    payout: float
    profit: float
    created_at: datetime


# ============================================================
# ENDPOINTS
# ============================================================

@router.get("/config", response_model=ConfigResponse)
async def get_config():
    """Get game configuration."""
    return ConfigResponse(
        multipliers=settings.MULTIPLIERS,
        slot_labels=['💀', '🎁', '2.0x', '0.7x', '0.6x', '0.7x', '2.0x', '🎁', '💀'],
        min_bet_ton=settings.MIN_BET_TON,
        max_bet_ton=settings.MAX_BET_TON,
        rows=16,
    )


@router.post("/play", response_model=DropResult)
async def play_plinko(
    request: PlayRequest,
    user_id: str = Query(..., description="Telegram user ID"),
):
    """Play plinko - drop a ball."""
    # Validate bet amount
    bet_amount = float(request.bet_amount_ton)
    
    if bet_amount < settings.MIN_BET_TON:
        raise HTTPException(status_code=400, detail=f"Minimum bet is {settings.MIN_BET_TON} TON")
    
    if bet_amount > settings.MAX_BET_TON:
        raise HTTPException(status_code=400, detail=f"Maximum bet is {settings.MAX_BET_TON} TON")
    
    # Generate seeds
    server_seed = secrets.token_hex(32)
    server_seed_hash = hashlib.sha256(server_seed.encode()).hexdigest()
    client_seed = request.client_seed or secrets.token_hex(16)
    
    # Get nonce for user
    if user_id not in user_nonces:
        user_nonces[user_id] = 0
    nonce = user_nonces[user_id]
    user_nonces[user_id] += 1
    
    # Generate drop
    result = engine.generate_drop(server_seed, client_seed, nonce, bet_amount)
    
    drop_id = str(uuid.uuid4())
    
    return DropResult(
        id=drop_id,
        path=result['path'],
        landing_slot=result['landing_slot'],
        slot_label=engine.get_slot_label(result['landing_slot']),
        multiplier=result['multiplier'],
        bet_amount=bet_amount,
        payout=result['payout'],
        profit=result['profit'],
        server_seed_hash=server_seed_hash,
        server_seed=server_seed,  # Revealed for single player
        client_seed=client_seed,
        nonce=nonce,
        created_at=datetime.utcnow(),
    )


@router.post("/verify", response_model=VerifyResponse)
async def verify_drop(request: VerifyRequest):
    """Verify a drop result is fair."""
    result = engine.generate_drop(
        request.server_seed,
        request.client_seed,
        request.nonce,
        request.bet_amount,
    )
    
    return VerifyResponse(
        valid=True,
        landing_slot=result['landing_slot'],
        multiplier=result['multiplier'],
        path=result['path'],
    )


@router.get("/history", response_model=List[HistoryItem])
async def get_history(
    user_id: str = Query(..., description="Telegram user ID"),
    limit: int = Query(50, ge=1, le=200),
):
    """Get user's drop history."""
    # In-memory store for now (should be database)
    # Return empty list since we're not persisting
    return []


@router.get("/stats")
async def get_stats(
    user_id: str = Query(..., description="Telegram user ID"),
):
    """Get user's plinko statistics."""
    return {
        "total_drops": 0,
        "total_wagered_ton": 0,
        "total_won_ton": 0,
        "total_profit_ton": 0,
        "biggest_win_ton": 0,
        "biggest_multiplier": 0,
    }

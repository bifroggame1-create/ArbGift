from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from ..services.plinko import PlinkoService
from ..services.gonka import GonkaService
from ..services.escape import EscapeService

router = APIRouter(prefix="/api", tags=["solo-games"])

# Service instances
plinko = PlinkoService()
gonka = GonkaService()
escape = EscapeService()


# --- Plinko ---

class PlinkoGameActive(BaseModel):
    server_seed_hash: str
    configs: dict

class PlinkoBuyRequest(BaseModel):
    amount: float
    client_seed: str = ""
    nonce: int = 0
    user_id: str = "anonymous"

class PlinkoBuyResponse(BaseModel):
    landing_slot: int
    slot_label: str
    multiplier: float
    payout: float
    profit: float
    path: list
    server_seed: str
    server_seed_hash: str
    nonce: int


@router.get("/solo-plinko-game/active")
async def plinko_active():
    """Get current plinko game state"""
    import hashlib, random
    seed_hash = hashlib.sha256(str(random.random()).encode()).hexdigest()[:8] + "..." + hashlib.sha256(str(random.random()).encode()).hexdigest()[-4:]
    return {
        "status": "active",
        "server_seed_hash": seed_hash
    }


@router.get("/solo-plinko-game/configs")
async def plinko_configs():
    """Get plinko slot configuration"""
    return {
        "slots": [
            {"index": i, "multiplier": m, "label": l}
            for i, (m, l) in enumerate(zip(
                PlinkoService.SLOT_MULTIPLIERS,
                PlinkoService.SLOT_LABELS
            ))
        ],
        "rows": PlinkoService.ROWS,
        "weights": PlinkoService.SLOT_WEIGHTS
    }


@router.get("/solo-plinko-game/ghost-games")
async def plinko_ghost_games():
    """Get other players' recent games for ghost animations"""
    import random
    ghosts = []
    for _ in range(random.randint(0, 3)):
        ghosts.append({
            "slot": random.choice([2, 3, 4, 5, 6]),
            "user_avatar": "",
            "timestamp": 0
        })
    return {"games": ghosts}


@router.post("/solo-plinko-game/buy/ton", response_model=PlinkoBuyResponse)
async def plinko_buy(request: PlinkoBuyRequest):
    """Place a plinko bet and get result"""
    if request.amount <= 0:
        raise HTTPException(status_code=400, detail="Invalid amount")

    result = plinko.play(
        user_id=request.user_id,
        bet_amount=request.amount,
        client_seed=request.client_seed,
        nonce=request.nonce
    )

    return PlinkoBuyResponse(**result)


# --- Gonka (Race) ---

class GonkaBuyRequest(BaseModel):
    amount: float
    mode: str = "lite"
    client_seed: str = ""
    nonce: int = 0
    user_id: str = "anonymous"

class GonkaBuyResponse(BaseModel):
    cell_index: int
    mode: str
    multiplier: float
    balls: int
    payout: float
    profit: float
    server_seed: str
    server_seed_hash: str
    nonce: int


@router.get("/solo-race-game/active")
async def gonka_active():
    import hashlib, random
    seed_hash = hashlib.sha256(str(random.random()).encode()).hexdigest()[:8] + "..." + hashlib.sha256(str(random.random()).encode()).hexdigest()[-4:]
    return {"status": "active", "server_seed_hash": seed_hash}


@router.get("/solo-race-game/configs")
async def gonka_configs():
    """Get gonka grid configuration for all modes"""
    return {
        "lite": gonka.get_config("lite"),
        "hard": gonka.get_config("hard")
    }


@router.post("/solo-race-game/buy/ton", response_model=GonkaBuyResponse)
async def gonka_buy(request: GonkaBuyRequest):
    """Place a Gonka bet and get result"""
    if request.amount <= 0:
        raise HTTPException(status_code=400, detail="Invalid amount")
    if request.mode not in ("lite", "hard"):
        raise HTTPException(status_code=400, detail="Invalid mode")

    result = gonka.play(
        user_id=request.user_id,
        bet_amount=request.amount,
        mode=request.mode,
        client_seed=request.client_seed,
        nonce=request.nonce
    )

    return GonkaBuyResponse(**result)


# --- Ball Escape ---

class EscapeBuyRequest(BaseModel):
    amount: float
    client_seed: str = ""
    nonce: int = 0
    user_id: str = "anonymous"

class EscapeBuyResponse(BaseModel):
    escaped: bool
    duration_ms: int
    multiplier: float
    payout: float
    profit: float
    server_seed: str
    server_seed_hash: str
    nonce: int


@router.get("/solo-escape-game/active")
async def escape_active():
    import hashlib, random
    seed_hash = hashlib.sha256(str(random.random()).encode()).hexdigest()[:8] + "..." + hashlib.sha256(str(random.random()).encode()).hexdigest()[-4:]
    return {"status": "active", "server_seed_hash": seed_hash}


@router.post("/solo-escape-game/buy/ton", response_model=EscapeBuyResponse)
async def escape_buy(request: EscapeBuyRequest):
    """Place a Ball Escape bet and get result"""
    if request.amount <= 0:
        raise HTTPException(status_code=400, detail="Invalid amount")

    result = escape.play(
        user_id=request.user_id,
        bet_amount=request.amount,
        client_seed=request.client_seed,
        nonce=request.nonce
    )

    return EscapeBuyResponse(**result)


# --- Health ---

@router.get("/health")
async def health():
    return {"status": "healthy", "service": "solo-games", "games": ["plinko", "gonka", "escape"]}

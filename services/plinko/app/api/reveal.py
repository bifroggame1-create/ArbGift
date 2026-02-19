from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.game_round import GameRound

router = APIRouter(prefix="/api/v1", tags=["reveal"])


@router.get("/reveal")
async def reveal(round_id: str = Query(...), session: AsyncSession = Depends(get_db)):
    result = await session.execute(select(GameRound).where(GameRound.round_id == round_id))
    round_obj = result.scalar_one_or_none()
    if not round_obj:
        raise HTTPException(status_code=404, detail="Round not found")
    return {
        "round_id": round_obj.round_id,
        "server_seed": round_obj.server_seed,
        "server_seed_hash": round_obj.server_seed_hash,
    }

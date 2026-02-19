from fastapi import Header, HTTPException

from app.config import settings


async def require_internal_key(x_internal_key: str = Header(..., alias="X-Internal-Key")) -> None:
    if settings.DEBUG and not settings.INTERNAL_API_KEY:
        return
    if not settings.INTERNAL_API_KEY or x_internal_key != settings.INTERNAL_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid internal key")

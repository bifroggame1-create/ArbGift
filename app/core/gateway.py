from fastapi import Header, HTTPException

from app.config import settings


def internal_headers() -> dict:
    key = settings.INTERNAL_API_KEY
    if not key:
        raise HTTPException(status_code=500, detail="Internal API key not configured")
    return {settings.INTERNAL_API_HEADER: key}

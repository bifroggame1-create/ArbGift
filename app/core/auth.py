import hashlib
import hmac
import json
import os
from urllib.parse import parse_qs

from fastapi import Header, HTTPException

from app.config import settings


def verify_telegram_init_data(init_data: str, bot_token: str) -> dict:
    """Validate Telegram WebApp initData signature and return user dict."""
    try:
        parsed = parse_qs(init_data)

        received_hash = parsed.get("hash", [""])[0]
        if not received_hash:
            raise ValueError("No hash in initData")

        data_check_string_parts = []
        for key in sorted(parsed.keys()):
            if key != "hash":
                value = parsed[key][0]
                data_check_string_parts.append(f"{key}={value}")
        data_check_string = "\n".join(data_check_string_parts)

        secret_key = hmac.new(
            "WebAppData".encode(),
            bot_token.encode(),
            hashlib.sha256,
        ).digest()

        calculated_hash = hmac.new(
            secret_key, data_check_string.encode(), hashlib.sha256
        ).hexdigest()

        if calculated_hash != received_hash:
            raise ValueError("Invalid hash")

        user_json = parsed.get("user", ["{}"])[0]
        user_data = json.loads(user_json)
        return user_data
    except Exception as exc:  # noqa: BLE001 broad but intentional to return 401
        raise HTTPException(status_code=401, detail="Invalid Telegram authentication") from exc


async def get_verified_telegram_id(
    init_data: str = Header(..., alias="X-Telegram-Init-Data"),
) -> int:
    bot_token = settings.TELEGRAM_BOT_TOKEN or os.getenv("TELEGRAM_BOT_TOKEN")
    if not bot_token:
        raise HTTPException(status_code=500, detail="Server auth not configured")

    user_data = verify_telegram_init_data(init_data, bot_token)
    telegram_id = user_data.get("id")
    if not telegram_id:
        raise HTTPException(status_code=401, detail="No user ID in initData")
    return telegram_id


async def get_optional_verified_telegram_id(
    init_data: str | None = Header(None, alias="X-Telegram-Init-Data"),
) -> int | None:
    """Return verified telegram id if header provided, else None."""
    if not init_data:
        return None
    return await get_verified_telegram_id(init_data)  # type: ignore[arg-type]

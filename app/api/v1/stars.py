"""
Telegram Stars API endpoints.

Provides REST API for purchasing Telegram Stars.
Uses Telegram Bot API createInvoiceLink for payment processing.
"""
import logging
import os
from typing import Optional

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

logger = logging.getLogger(__name__)
router = APIRouter()

# Telegram Bot API
TELEGRAM_API_URL = "https://api.telegram.org/bot"
BOT_TOKEN = os.getenv("BOT_TOKEN", "")

# Stars packages
STARS_PACKAGES = {
    50: {"price_rub": 90, "label": "50 Stars"},
    100: {"price_rub": 180, "label": "100 Stars"},
    250: {"price_rub": 450, "label": "250 Stars"},
    500: {"price_rub": 900, "label": "500 Stars"},
}


class CreateInvoiceRequest(BaseModel):
    """Request to create Stars invoice."""
    user_id: int
    amount: int  # Stars amount (50, 100, 250, 500)


class InvoiceResponse(BaseModel):
    """Invoice creation response."""
    invoice_url: str
    amount: int
    price_stars: int


@router.post("/stars/invoice", response_model=InvoiceResponse, tags=["Stars"])
async def create_stars_invoice(request: CreateInvoiceRequest):
    """
    Create a Telegram Stars invoice link.

    The invoice can be opened via Telegram WebApp.openInvoice()
    to process payment in Stars (XTR currency).
    """
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN not configured")
        raise HTTPException(status_code=503, detail="Stars payments not configured")

    if request.amount not in STARS_PACKAGES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid amount. Available: {list(STARS_PACKAGES.keys())}"
        )

    package = STARS_PACKAGES[request.amount]

    # Create invoice via Telegram Bot API
    payload = {
        "title": f"Пополнение {request.amount} Stars",
        "description": f"Покупка {request.amount} Stars для Gift Aggregator",
        "payload": f"stars_{request.user_id}_{request.amount}",
        "provider_token": "",  # Empty for Telegram Stars
        "currency": "XTR",  # Telegram Stars currency
        "prices": [
            {
                "label": package["label"],
                "amount": request.amount  # In Stars (integer)
            }
        ],
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{TELEGRAM_API_URL}{BOT_TOKEN}/createInvoiceLink",
                json=payload,
                timeout=10.0
            )

            data = response.json()

            if not data.get("ok"):
                error_msg = data.get("description", "Unknown error")
                logger.error(f"Telegram API error: {error_msg}")
                raise HTTPException(status_code=502, detail=f"Telegram API: {error_msg}")

            invoice_url = data["result"]

            return InvoiceResponse(
                invoice_url=invoice_url,
                amount=request.amount,
                price_stars=request.amount
            )

    except httpx.TimeoutException:
        logger.error("Telegram API timeout")
        raise HTTPException(status_code=504, detail="Telegram API timeout")
    except httpx.RequestError as e:
        logger.error(f"Telegram API request error: {e}")
        raise HTTPException(status_code=502, detail="Failed to connect to Telegram API")


@router.get("/stars/packages", tags=["Stars"])
async def get_stars_packages():
    """Get available Stars packages."""
    return {
        "packages": [
            {
                "amount": amount,
                "price_rub": pkg["price_rub"],
                "label": pkg["label"],
            }
            for amount, pkg in STARS_PACKAGES.items()
        ]
    }


@router.post("/stars/webhook", tags=["Stars"], include_in_schema=False)
async def stars_webhook(update: dict):
    """
    Webhook endpoint for Telegram Stars payment notifications.

    Telegram sends pre_checkout_query and successful_payment updates here.
    """
    if "pre_checkout_query" in update:
        # Answer pre-checkout query (must respond within 10 seconds)
        query = update["pre_checkout_query"]
        query_id = query["id"]

        try:
            async with httpx.AsyncClient() as client:
                await client.post(
                    f"{TELEGRAM_API_URL}{BOT_TOKEN}/answerPreCheckoutQuery",
                    json={
                        "pre_checkout_query_id": query_id,
                        "ok": True
                    },
                    timeout=5.0
                )
        except Exception as e:
            logger.error(f"Failed to answer pre-checkout: {e}")

        return {"ok": True}

    if "message" in update and "successful_payment" in update["message"]:
        # Payment was successful
        payment = update["message"]["successful_payment"]
        payload = payment.get("invoice_payload", "")

        # Parse payload: "stars_{user_id}_{amount}"
        parts = payload.split("_")
        if len(parts) == 3 and parts[0] == "stars":
            user_id = int(parts[1])
            amount = int(parts[2])

            logger.info(f"Stars payment successful: user={user_id}, amount={amount}")

            # TODO: Update user's Stars balance in database
            # await update_user_stars(user_id, amount)

        return {"ok": True}

    return {"ok": True}

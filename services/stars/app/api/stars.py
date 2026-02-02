"""
Stars API endpoints.
"""
from decimal import Decimal
from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models import get_db, Order, OrderStatus
from app.services.order_service import OrderService

router = APIRouter(prefix="/api/v1", tags=["stars"])


# ============================================================
# SCHEMAS
# ============================================================

class PackageResponse(BaseModel):
    """Star package response."""
    stars_amount: int
    usd_price: float
    ton_price: float
    rate_usd_per_star: float


class PackagesResponse(BaseModel):
    """All packages response."""
    packages: List[PackageResponse]
    ton_to_usd: float


class CreateOrderRequest(BaseModel):
    """Create order request."""
    stars_amount: int = Field(..., description="Number of stars to purchase")
    username: Optional[str] = None
    first_name: Optional[str] = None


class OrderResponse(BaseModel):
    """Order response."""
    order_uuid: str
    stars_amount: int
    ton_price: float
    usd_price: float
    status: OrderStatus
    payment_address: str
    payment_memo: str
    expires_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


class VerifyResponse(BaseModel):
    """Payment verification response."""
    verified: bool
    status: str
    tx_hash: Optional[str] = None
    stars_added: Optional[int] = None
    error: Optional[str] = None


class UserBalanceResponse(BaseModel):
    """User balance response."""
    telegram_id: int
    stars_balance: int
    total_stars_purchased: int


# ============================================================
# ENDPOINTS
# ============================================================

@router.get("/packages", response_model=PackagesResponse)
async def get_packages():
    """Get available star packages with pricing."""
    packages = []
    
    for stars in settings.STAR_PACKAGES:
        # Calculate price for each package
        usd_price = float(Decimal(stars) * settings.STARS_TO_USD * (1 + settings.MARGIN))
        ton_price = float(Decimal(str(usd_price)) / settings.TON_TO_USD)
        
        packages.append(PackageResponse(
            stars_amount=stars,
            usd_price=round(usd_price, 2),
            ton_price=round(ton_price, 4),
            rate_usd_per_star=float(settings.STARS_TO_USD),
        ))
    
    return PackagesResponse(
        packages=packages,
        ton_to_usd=float(settings.TON_TO_USD),
    )


@router.post("/orders", response_model=OrderResponse)
async def create_order(
    request: CreateOrderRequest,
    telegram_id: int = Query(..., description="Telegram user ID"),
    session: AsyncSession = Depends(get_db),
):
    """Create a new order for stars purchase."""
    service = OrderService(session)
    
    try:
        order = await service.create_order(
            telegram_id=telegram_id,
            stars_amount=request.stars_amount,
            username=request.username,
            first_name=request.first_name,
        )
        
        return OrderResponse(
            order_uuid=order.order_uuid,
            stars_amount=order.stars_amount,
            ton_price=float(order.ton_price),
            usd_price=float(order.usd_price) if order.usd_price else 0,
            status=order.status,
            payment_address=order.payment_address,
            payment_memo=order.payment_memo,
            expires_at=order.expires_at,
            created_at=order.created_at,
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/orders/{order_uuid}", response_model=OrderResponse)
async def get_order(
    order_uuid: str,
    session: AsyncSession = Depends(get_db),
):
    """Get order details."""
    service = OrderService(session)
    order = await service.get_order(order_uuid)
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    return OrderResponse(
        order_uuid=order.order_uuid,
        stars_amount=order.stars_amount,
        ton_price=float(order.ton_price),
        usd_price=float(order.usd_price) if order.usd_price else 0,
        status=order.status,
        payment_address=order.payment_address or "",
        payment_memo=order.payment_memo or "",
        expires_at=order.expires_at,
        created_at=order.created_at,
    )


@router.post("/orders/{order_uuid}/verify", response_model=VerifyResponse)
async def verify_payment(
    order_uuid: str,
    session: AsyncSession = Depends(get_db),
):
    """Verify payment for an order."""
    service = OrderService(session)
    result = await service.verify_payment(order_uuid)
    
    return VerifyResponse(
        verified=result.get("verified", False),
        status=result.get("status", "unknown"),
        tx_hash=result.get("tx_hash"),
        stars_added=result.get("stars_added"),
        error=result.get("error"),
    )


@router.get("/orders", response_model=List[OrderResponse])
async def get_user_orders(
    telegram_id: int = Query(..., description="Telegram user ID"),
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db),
):
    """Get user's order history."""
    service = OrderService(session)
    orders = await service.get_user_orders(telegram_id, limit)
    
    return [
        OrderResponse(
            order_uuid=order.order_uuid,
            stars_amount=order.stars_amount,
            ton_price=float(order.ton_price),
            usd_price=float(order.usd_price) if order.usd_price else 0,
            status=order.status,
            payment_address=order.payment_address or "",
            payment_memo=order.payment_memo or "",
            expires_at=order.expires_at,
            created_at=order.created_at,
        )
        for order in orders
    ]


@router.get("/balance", response_model=UserBalanceResponse)
async def get_user_balance(
    telegram_id: int = Query(..., description="Telegram user ID"),
    session: AsyncSession = Depends(get_db),
):
    """Get user's stars balance."""
    service = OrderService(session)
    user = await service.get_or_create_user(telegram_id)
    
    return UserBalanceResponse(
        telegram_id=user.telegram_id,
        stars_balance=user.stars_balance,
        total_stars_purchased=user.total_stars_purchased,
    )

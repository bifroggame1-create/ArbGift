"""
Order service for Stars purchase management.
"""
from decimal import Decimal
from typing import Optional, List
from datetime import datetime
import httpx

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.order import Order, OrderStatus
from app.models.user import User


class OrderService:
    """Service for managing star purchase orders."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_or_create_user(
        self,
        telegram_id: int,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
    ) -> User:
        """Get existing user or create new one."""
        result = await self.session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            user = User(
                telegram_id=telegram_id,
                username=username,
                first_name=first_name,
                last_name=last_name,
            )
            self.session.add(user)
            await self.session.flush()
        
        return user
    
    def calculate_price(self, stars_amount: int) -> dict:
        """
        Calculate price for stars purchase.
        
        Returns:
            dict with usd_price, ton_price, rate
        """
        # USD price = stars * rate per star
        usd_price = Decimal(stars_amount) * settings.STARS_TO_USD
        
        # Add margin
        usd_price_with_margin = usd_price * (1 + settings.MARGIN)
        
        # Convert to TON
        ton_price = usd_price_with_margin / settings.TON_TO_USD
        
        return {
            "stars_amount": stars_amount,
            "usd_price": round(usd_price_with_margin, 2),
            "ton_price": round(ton_price, 4),
            "rate_usd_per_star": float(settings.STARS_TO_USD),
            "ton_to_usd": float(settings.TON_TO_USD),
        }
    
    async def create_order(
        self,
        telegram_id: int,
        stars_amount: int,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
    ) -> Order:
        """Create a new order for stars purchase."""
        # Validate stars amount
        if stars_amount not in settings.STAR_PACKAGES:
            raise ValueError(f"Invalid stars amount. Choose from: {settings.STAR_PACKAGES}")
        
        # Get or create user
        user = await self.get_or_create_user(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
        )
        
        # Calculate price
        pricing = self.calculate_price(stars_amount)
        
        # Create order
        order = Order.create_order(
            user_id=user.id,
            telegram_id=telegram_id,
            stars_amount=stars_amount,
            ton_price=Decimal(str(pricing["ton_price"])),
            usd_price=Decimal(str(pricing["usd_price"])),
        )
        
        # Set payment address
        order.mark_awaiting_payment(settings.TON_WALLET)
        
        self.session.add(order)
        await self.session.flush()
        await self.session.refresh(order)
        
        return order
    
    async def get_order(self, order_uuid: str) -> Optional[Order]:
        """Get order by UUID."""
        result = await self.session.execute(
            select(Order).where(Order.order_uuid == order_uuid)
        )
        return result.scalar_one_or_none()
    
    async def get_user_orders(
        self,
        telegram_id: int,
        limit: int = 20,
    ) -> List[Order]:
        """Get orders for a user."""
        result = await self.session.execute(
            select(Order)
            .where(Order.telegram_id == telegram_id)
            .order_by(Order.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def verify_payment(self, order_uuid: str) -> dict:
        """
        Verify payment for an order.
        
        Checks TON blockchain for incoming transaction matching order.
        """
        order = await self.get_order(order_uuid)
        if not order:
            return {"verified": False, "error": "Order not found"}
        
        if order.status == OrderStatus.COMPLETED:
            return {"verified": True, "status": "already_completed"}
        
        if not order.is_payable:
            return {"verified": False, "error": "Order expired or not payable"}
        
        # Check TON API for transaction
        try:
            verified, tx_hash = await self._check_ton_payment(
                order.payment_address,
                order.payment_memo,
                float(order.ton_price),
            )
            
            if verified and tx_hash:
                order.mark_payment_received(tx_hash)
                
                # Get user and add stars
                result = await self.session.execute(
                    select(User).where(User.id == order.user_id)
                )
                user = result.scalar_one_or_none()
                if user:
                    user.add_stars(order.stars_amount)
                
                order.mark_completed()
                await self.session.flush()
                
                return {
                    "verified": True,
                    "status": "completed",
                    "tx_hash": tx_hash,
                    "stars_added": order.stars_amount,
                }
            
            return {"verified": False, "status": "payment_not_found"}
        
        except Exception as e:
            return {"verified": False, "error": str(e)}
    
    async def _check_ton_payment(
        self,
        wallet_address: str,
        memo: str,
        expected_amount: float,
    ) -> tuple[bool, Optional[str]]:
        """
        Check TON blockchain for payment.
        
        Returns:
            Tuple of (verified, tx_hash)
        """
        if not settings.TON_API_KEY:
            # For testing without API key
            return False, None
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{settings.TON_API_URL}/accounts/{wallet_address}/events",
                    headers={"Authorization": f"Bearer {settings.TON_API_KEY}"},
                    params={"limit": 20},
                )
                
                if response.status_code != 200:
                    return False, None
                
                events = response.json().get("events", [])
                
                for event in events:
                    # Check if this is an incoming TON transfer with matching memo
                    actions = event.get("actions", [])
                    for action in actions:
                        if action.get("type") == "TonTransfer":
                            transfer = action.get("TonTransfer", {})
                            comment = transfer.get("comment", "")
                            amount = int(transfer.get("amount", 0)) / 1e9  # Convert from nanoTON
                            
                            # Check memo and amount (with 1% tolerance)
                            if memo in comment and abs(amount - expected_amount) <= expected_amount * 0.01:
                                return True, event.get("event_id")
                
                return False, None
        
        except Exception:
            return False, None

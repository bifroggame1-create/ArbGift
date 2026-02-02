"""
Room repository — CRUD для PvP комнат и ставок.
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional, List

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Room, Bet, UserStats, RoomStatus


class RoomRepository:
    """Database operations for rooms and bets."""

    def __init__(self, session: AsyncSession):
        self.session = session

    # ── Rooms ──────────────────────────────────────────────────────────

    async def create_room(self, **kwargs) -> Room:
        room = Room(**kwargs)
        self.session.add(room)
        await self.session.commit()
        await self.session.refresh(room)
        return room

    async def get_room(self, room_code: str) -> Optional[Room]:
        result = await self.session.execute(
            select(Room)
            .options(selectinload(Room.bets))
            .where(Room.room_code == room_code)
        )
        return result.scalar_one_or_none()

    async def update_room(self, room_code: str, **kwargs) -> Optional[Room]:
        await self.session.execute(
            update(Room).where(Room.room_code == room_code).values(**kwargs)
        )
        await self.session.commit()
        return await self.get_room(room_code)

    async def list_rooms(
        self,
        status: Optional[RoomStatus] = None,
        limit: int = 20,
    ) -> List[Room]:
        query = select(Room).options(selectinload(Room.bets))
        if status:
            query = query.where(Room.status == status)
        query = query.order_by(Room.created_at.desc()).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def list_active_rooms(self, limit: int = 20) -> List[Room]:
        query = (
            select(Room)
            .options(selectinload(Room.bets))
            .where(Room.status.in_([RoomStatus.WAITING, RoomStatus.COUNTDOWN]))
            .order_by(Room.created_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    # ── Bets ───────────────────────────────────────────────────────────

    async def add_bet(self, room: Room, **kwargs) -> Bet:
        bet = Bet(room_id=room.id, **kwargs)
        self.session.add(bet)

        room.total_pool_ton += kwargs["gift_value_ton"]
        room.total_bets += 1

        unique_users = {b.user_id for b in room.bets}
        unique_users.add(kwargs["user_id"])
        room.total_players = len(unique_users)

        await self.session.commit()
        await self.session.refresh(bet)
        return bet

    async def get_room_bets(self, room_id: int) -> List[Bet]:
        result = await self.session.execute(
            select(Bet).where(Bet.room_id == room_id)
        )
        return list(result.scalars().all())

    async def is_nft_locked(self, gift_address: str) -> bool:
        """Check if NFT is already bet in an active room."""
        result = await self.session.execute(
            select(Bet)
            .join(Room)
            .where(
                Bet.gift_address == gift_address,
                Room.status.in_([
                    RoomStatus.WAITING,
                    RoomStatus.COUNTDOWN,
                    RoomStatus.SPINNING,
                ]),
            )
        )
        return result.scalar_one_or_none() is not None

    # ── User Stats ─────────────────────────────────────────────────────

    async def get_or_create_stats(self, user_id: int, telegram_id: int) -> UserStats:
        result = await self.session.execute(
            select(UserStats).where(UserStats.user_id == user_id)
        )
        stats = result.scalar_one_or_none()
        if not stats:
            stats = UserStats(user_id=user_id, telegram_id=telegram_id)
            self.session.add(stats)
            await self.session.commit()
            await self.session.refresh(stats)
        return stats

    async def update_stats_win(
        self,
        user_id: int,
        wagered: Decimal,
        won: Decimal,
    ) -> None:
        stats = await self.session.execute(
            select(UserStats).where(UserStats.user_id == user_id)
        )
        s = stats.scalar_one_or_none()
        if not s:
            return
        s.total_wins += 1
        s.total_games += 1
        s.total_wagered_ton += wagered
        s.total_won_ton += won
        s.total_profit_ton += (won - wagered)
        s.current_win_streak += 1
        s.max_win_streak = max(s.max_win_streak, s.current_win_streak)
        if won > s.biggest_win_ton:
            s.biggest_win_ton = won
        s.last_game_at = datetime.utcnow()
        await self.session.commit()

    async def update_stats_loss(
        self,
        user_id: int,
        wagered: Decimal,
    ) -> None:
        stats = await self.session.execute(
            select(UserStats).where(UserStats.user_id == user_id)
        )
        s = stats.scalar_one_or_none()
        if not s:
            return
        s.total_losses += 1
        s.total_games += 1
        s.total_wagered_ton += wagered
        s.total_profit_ton -= wagered
        s.current_win_streak = 0
        if wagered > s.biggest_loss_ton:
            s.biggest_loss_ton = wagered
        s.last_game_at = datetime.utcnow()
        await self.session.commit()

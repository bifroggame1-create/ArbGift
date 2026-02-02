"""
Game Scheduler — автоматический countdown и auto-spin.
"""
import asyncio
import logging
from datetime import datetime, timezone
from decimal import Decimal

from app.database import async_session_maker
from app.models import RoomStatus
from app.repositories.room_repository import RoomRepository
from app.services.engine import PvPGameEngine
from app.services.websocket_manager import ws_manager

logger = logging.getLogger(__name__)


class GameScheduler:
    """Background task that processes countdowns and auto-spins."""

    def __init__(self):
        self.engine = PvPGameEngine()
        self._running = False
        self._task: asyncio.Task | None = None

    async def start(self):
        self._running = True
        self._task = asyncio.create_task(self._loop())
        logger.info("GameScheduler started")

    async def stop(self):
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("GameScheduler stopped")

    async def _loop(self):
        while self._running:
            try:
                await self._tick()
            except Exception as e:
                logger.error(f"Scheduler tick error: {e}")
            await asyncio.sleep(1)

    async def _tick(self):
        """Process one scheduler tick."""
        async with async_session_maker() as session:
            repo = RoomRepository(session)

            # Find rooms in countdown
            rooms = await repo.list_rooms(status=RoomStatus.COUNTDOWN, limit=50)

            for room in rooms:
                if not room.started_at:
                    # Mark countdown start
                    await repo.update_room(
                        room.room_code,
                        started_at=datetime.now(timezone.utc),
                    )
                    await ws_manager.broadcast(room.room_code, {
                        "type": "countdown_start",
                        "data": {"countdown_seconds": room.countdown_seconds},
                    })
                    continue

                # Calculate remaining time
                now = datetime.now(timezone.utc)
                started = room.started_at.replace(tzinfo=timezone.utc) if room.started_at.tzinfo is None else room.started_at
                elapsed = (now - started).total_seconds()
                remaining = room.countdown_seconds - elapsed

                # Broadcast countdown updates every 5 seconds
                if remaining > 0 and int(remaining) % 5 == 0:
                    await ws_manager.broadcast(room.room_code, {
                        "type": "countdown_update",
                        "data": {"remaining_seconds": int(remaining)},
                    })

                # Time's up → spin
                if remaining <= 0:
                    await self._auto_spin(room, repo)

    async def _auto_spin(self, room, repo: RoomRepository):
        """Execute automatic spin for a room."""
        try:
            # Update status to spinning
            await repo.update_room(room.room_code, status=RoomStatus.SPINNING)

            await ws_manager.broadcast(room.room_code, {
                "type": "spin_start",
                "data": {},
            })

            # Small delay for animation
            await asyncio.sleep(1)

            # Refresh room to get latest bets
            room = await repo.get_room(room.room_code)
            if not room or not room.bets:
                await repo.update_room(room.room_code, status=RoomStatus.CANCELLED)
                return

            # Unique players check
            unique_users = {b.user_id for b in room.bets}
            if len(unique_users) < 2:
                await repo.update_room(room.room_code, status=RoomStatus.CANCELLED)
                await ws_manager.broadcast(room.room_code, {
                    "type": "room_cancelled",
                    "data": {"reason": "Not enough players"},
                })
                return

            # Execute spin
            result = self.engine.spin_wheel(room, room.bets)

            # Find winner bet
            winner_bet = next(
                (b for b in room.bets if b.id == result.winning_bet_id),
                None,
            )

            # Calculate payout
            winnings, fee = self.engine.calculate_winnings(
                room.total_pool_ton,
                room.house_fee_percent,
            )

            # Update room
            await repo.update_room(
                room.room_code,
                status=RoomStatus.FINISHED,
                winner_user_id=result.winner_user_id,
                winner_ticket=result.winning_ticket,
                winning_spin_degree=result.spin_degree,
                finished_at=datetime.now(timezone.utc),
            )

            # Update user stats
            for bet in room.bets:
                user_wagered = bet.gift_value_ton
                if bet.user_id == result.winner_user_id:
                    await repo.update_stats_win(bet.user_id, user_wagered, winnings)
                else:
                    await repo.update_stats_loss(bet.user_id, user_wagered)

            # Broadcast result
            await ws_manager.broadcast(room.room_code, {
                "type": "spin_result",
                "data": {
                    "winner_user_id": result.winner_user_id,
                    "winner_user_name": winner_bet.user_name if winner_bet else "Unknown",
                    "winning_ticket": result.winning_ticket,
                    "total_tickets": sum(b.tickets_count for b in room.bets),
                    "spin_degree": str(result.spin_degree),
                    "winnings_ton": str(winnings),
                    "house_fee_ton": str(fee),
                    "server_seed": room.server_seed,
                },
            })

            logger.info(
                f"Room {room.room_code} finished. "
                f"Winner: {result.winner_user_id}, "
                f"Pool: {room.total_pool_ton} TON"
            )

        except Exception as e:
            logger.error(f"Auto-spin failed for {room.room_code}: {e}")
            await repo.update_room(room.room_code, status=RoomStatus.CANCELLED)


# Global singleton
game_scheduler = GameScheduler()

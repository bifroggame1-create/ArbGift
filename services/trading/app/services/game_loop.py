"""
Trading Game Loop.

Background task that runs continuous trading/crash games.
"""
import asyncio
import logging
from datetime import datetime
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.models.game import TradingGame, GameStatus
from app.models.bet import TradingBet, BetStatus
from app.services.game_engine import TradingGameEngine
from app.websocket.manager import manager

logger = logging.getLogger(__name__)


class GameLoop:
    """Background task that runs trading games."""

    def __init__(self, db_session_factory):
        self.db_session_factory = db_session_factory
        self.engine = TradingGameEngine()
        self.current_game: TradingGame = None
        self.is_running = False
        self.game_counter = 1

    async def start(self):
        """Start the game loop."""
        self.is_running = True
        logger.info("Game loop started")

        # Get latest game number from DB
        async for session in self.db_session_factory():
            result = await session.execute(
                select(TradingGame.game_number)
                .order_by(TradingGame.game_number.desc())
                .limit(1)
            )
            last_number = result.scalar_one_or_none()
            if last_number:
                self.game_counter = last_number + 1
            break

        while self.is_running:
            try:
                await self.run_game()
            except Exception as e:
                logger.error(f"Error in game loop: {e}")
                await asyncio.sleep(5)

    async def stop(self):
        """Stop the game loop."""
        self.is_running = False
        logger.info("Game loop stopped")

    async def run_game(self):
        """Run a single game cycle."""
        # Create new game
        async for session in self.db_session_factory():
            server_seed, server_seed_hash, crash_point = self.engine.create_new_game(
                self.game_counter
            )

            game = TradingGame(
                game_number=self.game_counter,
                status=GameStatus.PENDING,
                server_seed_hash=server_seed_hash,
                server_seed=server_seed,
                nonce=self.game_counter,
                crash_point=crash_point,
            )

            session.add(game)
            await session.commit()
            await session.refresh(game)

            self.current_game = game
            self.game_counter += 1
            break

        # Betting phase (5 seconds)
        await manager.broadcast_game_state(
            game_number=game.game_number,
            status="pending",
            multiplier=1.00,
            server_seed_hash=game.server_seed_hash,
        )
        await asyncio.sleep(5)

        # Start game
        async for session in self.db_session_factory():
            await session.execute(
                update(TradingGame)
                .where(TradingGame.id == game.id)
                .values(status=GameStatus.ACTIVE, started_at=datetime.utcnow())
            )
            await session.commit()
            break

        # Game loop - update multiplier every 100ms
        start_time = datetime.utcnow()
        crashed = False

        while not crashed:
            elapsed = (datetime.utcnow() - start_time).total_seconds()
            current_multiplier = self.engine.calculate_multiplier(elapsed, game.crash_point)

            # Check if game should crash
            if current_multiplier >= game.crash_point:
                crashed = True
                current_multiplier = game.crash_point

            # Update database
            async for session in self.db_session_factory():
                await session.execute(
                    update(TradingGame)
                    .where(TradingGame.id == game.id)
                    .values(current_multiplier=current_multiplier)
                )
                await session.commit()
                break

            # Broadcast to clients
            await manager.broadcast_game_state(
                game_number=game.game_number,
                status="active",
                multiplier=float(current_multiplier),
            )

            if not crashed:
                await asyncio.sleep(0.1)  # 100ms update interval

        # Game crashed
        async for session in self.db_session_factory():
            # Mark game as crashed
            await session.execute(
                update(TradingGame)
                .where(TradingGame.id == game.id)
                .values(
                    status=GameStatus.CRASHED,
                    crashed_at=datetime.utcnow(),
                    current_multiplier=game.crash_point,
                )
            )

            # Mark all active bets as lost
            await session.execute(
                update(TradingBet)
                .where(TradingBet.game_id == game.id)
                .where(TradingBet.status == BetStatus.ACTIVE)
                .values(status=BetStatus.LOST)
            )

            await session.commit()
            break

        # Broadcast crash event
        await manager.broadcast_crash(
            game_number=game.game_number,
            crash_point=float(game.crash_point),
            server_seed=game.server_seed,
        )

        # Wait 3 seconds before next game
        await asyncio.sleep(3)


# Global game loop instance
game_loop = None

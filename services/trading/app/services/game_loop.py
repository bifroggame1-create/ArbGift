import asyncio
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from ..models.game import TradingGame, GameStatus
from ..models.bet import Bet, BetStatus
from ..services.game_engine import TradingGameEngine
from ..websocket.manager import manager


class GameLoop:
    """Background task that runs trading games"""

    def __init__(self, db_session_factory):
        self.db_session_factory = db_session_factory
        self.engine = TradingGameEngine()
        self.current_game: TradingGame = None
        self.is_running = False
        self.game_counter = 1

    async def start(self):
        """Start the game loop"""
        self.is_running = True
        while self.is_running:
            try:
                await self.run_game()
            except Exception as e:
                print(f"Error in game loop: {e}")
                await asyncio.sleep(5)

    async def stop(self):
        """Stop the game loop"""
        self.is_running = False

    async def run_game(self):
        """Run a single game cycle"""
        # Create new game
        async with self.db_session_factory() as session:
            server_seed = self.engine.generate_server_seed()
            server_seed_hash = self.engine.generate_server_seed()  # Hash for public display

            game = TradingGame(
                game_number=self.game_counter,
                status=GameStatus.PENDING,
                server_seed_hash=server_seed_hash,
                server_seed=server_seed,
                nonce=self.game_counter,
                crash_point=self.engine.generate_crash_point(server_seed, self.game_counter)
            )

            session.add(game)
            await session.commit()
            await session.refresh(game)

            self.current_game = game
            self.game_counter += 1

        # Betting phase (5 seconds)
        await manager.broadcast_game_state(
            game_number=game.game_number,
            status="pending",
            multiplier=1.00
        )
        await asyncio.sleep(5)

        # Start game
        async with self.db_session_factory() as session:
            await session.execute(
                update(TradingGame)
                .where(TradingGame.id == game.id)
                .values(status=GameStatus.ACTIVE, started_at=datetime.utcnow())
            )
            await session.commit()

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
            async with self.db_session_factory() as session:
                await session.execute(
                    update(TradingGame)
                    .where(TradingGame.id == game.id)
                    .values(current_multiplier=current_multiplier)
                )
                await session.commit()

            # Broadcast to clients
            await manager.broadcast_game_state(
                game_number=game.game_number,
                status="active",
                multiplier=current_multiplier
            )

            if not crashed:
                await asyncio.sleep(0.1)  # 100ms update interval

        # Game crashed
        async with self.db_session_factory() as session:
            # Mark game as crashed
            await session.execute(
                update(TradingGame)
                .where(TradingGame.id == game.id)
                .values(
                    status=GameStatus.CRASHED,
                    crashed_at=datetime.utcnow(),
                    current_multiplier=game.crash_point
                )
            )

            # Mark all active bets as lost
            await session.execute(
                update(Bet)
                .where(Bet.game_id == game.id)
                .where(Bet.status == BetStatus.ACTIVE)
                .values(status=BetStatus.LOST)
            )

            await session.commit()

        # Broadcast crash event
        await manager.broadcast_crash(
            game_number=game.game_number,
            crash_point=game.crash_point,
            server_seed=game.server_seed
        )

        # Wait 3 seconds before next game
        await asyncio.sleep(3)


# Global game loop instance
game_loop = None

import hashlib
import random


class EscapeService:
    """
    Ball Escape game logic — matches myballs.io solo-escape-game

    Character moves around circular ring.
    Green zone = escape (win), Red zone = caught (lose).
    Multiplier grows from 1.0x to ~3.75x over game duration.
    Player taps to influence character movement.

    House edge: ~65% lose, ~35% win
    (Higher multiplier compensates for lower win probability)

    API mirrors: POST /api/solo-escape-game/buy/ton
    """

    WIN_PROBABILITY = 0.35  # 35% chance to escape
    MAX_MULTIPLIER = 3.75
    MIN_DURATION_MS = 3000  # 3 seconds minimum
    MAX_DURATION_MS = 5000  # 5 seconds maximum

    def generate_seeds(self) -> tuple[str, str]:
        server_seed = hashlib.sha256(str(random.random()).encode()).hexdigest()
        server_seed_hash = hashlib.sha256(server_seed.encode()).hexdigest()
        return server_seed, server_seed_hash

    def determine_outcome(self, server_seed: str, client_seed: str, nonce: int) -> dict:
        """
        Provably fair outcome determination.

        Returns whether player escaped and the game duration.
        """
        combined = f"{server_seed}:{client_seed}:{nonce}"
        hash_hex = hashlib.sha256(combined.encode()).hexdigest()
        hash_int = int(hash_hex[:8], 16)
        normalized = hash_int / (16 ** 8)

        escaped = normalized < self.WIN_PROBABILITY

        # Duration hash (second part of hash)
        duration_int = int(hash_hex[8:16], 16)
        duration_normalized = duration_int / (16 ** 8)
        duration_ms = int(
            self.MIN_DURATION_MS +
            duration_normalized * (self.MAX_DURATION_MS - self.MIN_DURATION_MS)
        )

        # Multiplier based on duration (longer game = higher multiplier)
        duration_ratio = (duration_ms - self.MIN_DURATION_MS) / (self.MAX_DURATION_MS - self.MIN_DURATION_MS)
        multiplier = 1.0 + duration_ratio * (self.MAX_MULTIPLIER - 1.0)

        return {
            "escaped": escaped,
            "duration_ms": duration_ms,
            "multiplier": round(multiplier, 2)
        }

    def play(self, user_id: str, bet_amount: float,
             client_seed: str = "", nonce: int = 0) -> dict:
        """Execute a single Ball Escape game"""
        server_seed, server_seed_hash = self.generate_seeds()

        outcome = self.determine_outcome(server_seed, client_seed, nonce)

        if outcome["escaped"]:
            multiplier = outcome["multiplier"]
            payout = bet_amount * multiplier
        else:
            multiplier = outcome["multiplier"]  # shown but not paid
            payout = 0.0

        profit = payout - bet_amount

        return {
            "escaped": outcome["escaped"],
            "duration_ms": outcome["duration_ms"],
            "multiplier": multiplier,
            "payout": round(payout, 4),
            "profit": round(profit, 4),
            "server_seed": server_seed,
            "server_seed_hash": server_seed_hash,
            "nonce": nonce
        }

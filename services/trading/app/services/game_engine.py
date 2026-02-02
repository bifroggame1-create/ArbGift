"""
Trading Game Engine.

Provably fair crash game mechanics using cryptographic randomness.
"""
import hashlib
import secrets
from decimal import Decimal
from typing import Tuple


class TradingGameEngine:
    """
    Trading game engine for provably fair crash game.

    Similar to crash/aviator game mechanics:
    - Server generates a secret seed before game starts
    - Hash of seed is shown to players before betting
    - Crash point is deterministically derived from seed
    - After crash, seed is revealed for verification
    """

    HOUSE_EDGE = Decimal("0.03")  # 3% house edge

    @staticmethod
    def generate_server_seed() -> str:
        """
        Generate cryptographically secure random server seed.

        Uses secrets module instead of random for security.
        """
        return secrets.token_hex(32)  # 64 character hex string

    @staticmethod
    def hash_server_seed(server_seed: str) -> str:
        """Hash server seed with SHA-256."""
        return hashlib.sha256(server_seed.encode()).hexdigest()

    @classmethod
    def generate_crash_point(cls, server_seed: str, nonce: int) -> Decimal:
        """
        Generate crash point using provably fair algorithm.

        Based on bustabit's algorithm:
        1. Combine server_seed and nonce
        2. Hash with SHA-256
        3. Convert to crash multiplier using inverse exponential distribution

        Returns crash point between 1.00x and MAX_MULTIPLIER
        """
        # Combine seed and nonce
        combined = f"{server_seed}:{nonce}"
        hash_result = hashlib.sha256(combined.encode()).hexdigest()

        # Convert first 13 hex characters to decimal
        hex_value = int(hash_result[:13], 16)

        # Calculate crash point with house edge
        # Using inverse exponential distribution
        e = 2 ** 52  # Use larger range for better distribution
        h = hex_value

        # Probability calculation (simplified bustabit formula)
        # instant_crash probability = house_edge
        if h % 33 == 0:  # ~3% chance of instant crash
            return Decimal("1.00")

        # Calculate multiplier from hash
        crash_point = (100 * e - h) / (e - h)
        crash_point = max(Decimal("1.00"), Decimal(str(crash_point / 100)))

        # Cap at reasonable maximum
        crash_point = min(crash_point, Decimal("10000.00"))

        return round(crash_point, 2)

    @staticmethod
    def calculate_multiplier(elapsed_time: float, crash_point: Decimal) -> Decimal:
        """
        Calculate current multiplier based on elapsed time.

        Args:
            elapsed_time: Time in seconds since game started
            crash_point: Pre-determined crash point

        Returns current multiplier (1.00 to crash_point)
        """
        # Exponential growth: multiplier = e^(growth_rate * time)
        # Calibrated for ~6% growth per 100ms
        growth_rate = 0.06

        import math
        multiplier = math.e ** (elapsed_time * growth_rate)
        multiplier = Decimal(str(round(multiplier, 2)))

        # Ensure we don't exceed crash point
        return min(multiplier, crash_point)

    @classmethod
    def verify_crash_point(
        cls,
        server_seed: str,
        nonce: int,
        claimed_crash_point: Decimal,
    ) -> bool:
        """Verify that crash point was generated fairly."""
        actual_crash_point = cls.generate_crash_point(server_seed, nonce)
        return abs(actual_crash_point - claimed_crash_point) < Decimal("0.01")

    @staticmethod
    def calculate_payout(bet_amount: Decimal, cash_out_multiplier: Decimal) -> Decimal:
        """Calculate payout for a cashed out bet."""
        return round(bet_amount * cash_out_multiplier, 9)

    @staticmethod
    def calculate_profit(bet_amount: Decimal, cash_out_multiplier: Decimal) -> Decimal:
        """Calculate profit for a cashed out bet."""
        payout = bet_amount * cash_out_multiplier
        return round(payout - bet_amount, 9)

    @classmethod
    def create_new_game(cls, nonce: int) -> Tuple[str, str, Decimal]:
        """
        Create a new game with provably fair setup.

        Returns:
            Tuple of (server_seed, server_seed_hash, crash_point)
        """
        server_seed = cls.generate_server_seed()
        server_seed_hash = cls.hash_server_seed(server_seed)
        crash_point = cls.generate_crash_point(server_seed, nonce)

        return server_seed, server_seed_hash, crash_point

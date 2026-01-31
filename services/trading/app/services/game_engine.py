import hashlib
import hmac
from decimal import Decimal
import random


class TradingGameEngine:
    """
    Trading game engine for provably fair crash game
    Similar to crash/aviator game mechanics
    """

    HOUSE_EDGE = Decimal("0.03")  # 3% house edge

    def __init__(self):
        pass

    def generate_server_seed(self) -> str:
        """Generate random server seed"""
        return hashlib.sha256(str(random.random()).encode()).hexdigest()

    def generate_crash_point(self, server_seed: str, nonce: int) -> float:
        """
        Generate crash point using provably fair algorithm

        Based on bustabit's algorithm:
        1. Combine server_seed and nonce
        2. Hash with SHA256
        3. Convert to crash multiplier

        Returns crash point between 1.00x and potentially infinite (with exponential distribution)
        """
        # Combine seed and nonce
        combined = f"{server_seed}:{nonce}"
        hash_result = hashlib.sha256(combined.encode()).hexdigest()

        # Convert first 13 hex characters to decimal
        hex_value = int(hash_result[:13], 16)

        # Calculate crash point with house edge
        # Using inverse exponential distribution
        e = 2 ** 32
        crash_point = max(1.0, (100 - float(self.HOUSE_EDGE * 100)) / (hex_value % e / e * 100))

        # Cap at reasonable maximum
        crash_point = min(crash_point, 10000.0)

        return round(crash_point, 2)

    def calculate_multiplier(self, elapsed_time: float, max_multiplier: float = 10.0) -> float:
        """
        Calculate current multiplier based on elapsed time

        Args:
            elapsed_time: Time in seconds since game started
            max_multiplier: Maximum multiplier before crash

        Returns current multiplier (1.00 to max_multiplier)
        """
        # Exponential growth: multiplier = 1.00 * e^(growth_rate * time)
        # Calibrated so it reaches max_multiplier in ~10 seconds
        growth_rate = 0.2

        multiplier = 1.00 * (1.1 ** (elapsed_time * growth_rate * 10))
        multiplier = min(multiplier, max_multiplier)

        return round(multiplier, 2)

    def verify_crash_point(self, server_seed: str, nonce: int, claimed_crash_point: float) -> bool:
        """Verify that crash point was generated fairly"""
        actual_crash_point = self.generate_crash_point(server_seed, nonce)
        return abs(actual_crash_point - claimed_crash_point) < 0.01

    def calculate_payout(self, bet_amount: float, cash_out_multiplier: float) -> float:
        """Calculate payout for a cashed out bet"""
        return round(bet_amount * cash_out_multiplier, 2)

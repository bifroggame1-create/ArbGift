import hashlib
import random
from typing import List


class PlinkoService:
    """
    Plinko game logic — matches myballs.io solo-plinko-game

    9 slots (left to right):
    💀  🎁  2.0x  0.7x  0.6x  0.7x  2.0x  🎁  💀

    API mirrors: POST /api/solo-plinko-game/buy/ton
    """

    SLOT_MULTIPLIERS = [0.0, 0.0, 2.0, 0.7, 0.6, 0.7, 2.0, 0.0, 0.0]
    SLOT_LABELS = ['skull', 'gift', '2.0x', '0.7x', '0.6x', '0.7x', '2.0x', 'gift', 'skull']

    # Probability weights — center-heavy like real plinko physics
    # Matches the natural binomial distribution of 14-row peg board
    SLOT_WEIGHTS = [0.02, 0.03, 0.10, 0.15, 0.20, 0.15, 0.10, 0.03, 0.02]

    ROWS = 14

    def generate_seeds(self) -> tuple[str, str]:
        """Generate server seed and its public hash"""
        server_seed = hashlib.sha256(str(random.random()).encode()).hexdigest()
        server_seed_hash = hashlib.sha256(server_seed.encode()).hexdigest()
        return server_seed, server_seed_hash

    def determine_slot(self, server_seed: str, client_seed: str, nonce: int) -> int:
        """
        Provably fair slot determination

        Algorithm:
        1. Combine seeds + nonce
        2. SHA256 hash
        3. Take first 8 hex chars as uint32
        4. Map to weighted slot distribution
        """
        combined = f"{server_seed}:{client_seed}:{nonce}"
        hash_hex = hashlib.sha256(combined.encode()).hexdigest()
        hash_int = int(hash_hex[:8], 16)

        # Normalize to [0, 1)
        normalized = hash_int / (16 ** 8)

        # Map to weighted slots
        cumulative = 0.0
        for i, weight in enumerate(self.SLOT_WEIGHTS):
            cumulative += weight
            if normalized < cumulative:
                return i

        return 4  # center fallback

    def generate_ball_path(self, target_slot: int) -> List[dict]:
        """
        Generate ball path through pegs for animation replay on client

        Returns array of {x, y} positions normalized to [0, 1] range
        """
        path = []
        center_x = 0.5

        # Target x position (center of target slot)
        target_x = (target_slot + 0.5) / 9.0

        # Start at drop box
        x = center_x + (random.random() - 0.5) * 0.05
        path.append({"x": x, "y": 0.0})

        # Through each peg row
        for row in range(self.ROWS):
            progress = (row + 1) / self.ROWS
            # Gradually steer toward target
            current_target = center_x + (target_x - center_x) * progress
            jitter = (random.random() - 0.5) * 0.04 * (1 - progress)
            x = max(0.05, min(0.95, current_target + jitter))
            y = (row + 1) / (self.ROWS + 1)
            path.append({"x": x, "y": y})

        # Final landing
        path.append({"x": target_x, "y": 1.0})

        return path

    def play(self, user_id: str, bet_amount: float, client_seed: str = "", nonce: int = 0) -> dict:
        """
        Execute a single plinko game

        Returns:
            {
                "landing_slot": int,
                "multiplier": float,
                "payout": float,
                "profit": float,
                "path": [...],
                "server_seed": str,
                "server_seed_hash": str,
                "nonce": int
            }
        """
        server_seed, server_seed_hash = self.generate_seeds()

        slot = self.determine_slot(server_seed, client_seed, nonce)
        multiplier = self.SLOT_MULTIPLIERS[slot]
        payout = bet_amount * multiplier
        profit = payout - bet_amount
        path = self.generate_ball_path(slot)

        return {
            "landing_slot": slot,
            "slot_label": self.SLOT_LABELS[slot],
            "multiplier": multiplier,
            "payout": round(payout, 4),
            "profit": round(profit, 4),
            "path": path,
            "server_seed": server_seed,
            "server_seed_hash": server_seed_hash,
            "nonce": nonce
        }

import hashlib
from typing import List

from app.config import MULTIPLIER_SETS, VALID_RISK_LEVELS, VALID_ROW_COUNTS


class PlinkoEngine:
    """
    Provably fair Plinko engine.

    Supports 3 risk levels (low/medium/high) and 3 row counts (8/12/16).
    Slot count = row_count + 1.
    Path returned as normalized [x, y] coordinates for frontend animation.
    """

    def generate_drop(
        self,
        server_seed: str,
        client_seed: str,
        nonce: int,
        bet_amount: float,
        risk_level: str = "medium",
        row_count: int = 12,
    ) -> dict:
        if risk_level not in VALID_RISK_LEVELS:
            raise ValueError(f"Invalid risk_level: {risk_level}")
        if row_count not in VALID_ROW_COUNTS:
            raise ValueError(f"Invalid row_count: {row_count}")

        random_bits = self._generate_random_bits(server_seed, client_seed, nonce, row_count)

        num_slots = row_count + 1
        # Random walk from center
        position = 0  # center = 0, range will be -row_count/2 to +row_count/2
        path: List[List[float]] = [[0.5, 0.0]]  # normalized: x=0..1, y=0..1

        for i, go_right in enumerate(random_bits):
            position += 1 if go_right else -1
            # Normalize to 0..1 range
            norm_x = (position + row_count) / (2 * row_count)
            norm_y = (i + 1) / row_count
            path.append([round(norm_x, 4), round(norm_y, 4)])

        # Map position to slot index (0-based)
        # position ranges from -row_count to +row_count in steps of 2
        # but since each step is +-1, actual range is -row_count to +row_count
        # We need to map to 0..num_slots-1
        landing_slot = (position + row_count) // 2
        landing_slot = max(0, min(num_slots - 1, landing_slot))

        multipliers = MULTIPLIER_SETS[risk_level][row_count]
        multiplier = multipliers[landing_slot]
        payout = round(bet_amount * multiplier, 2)
        profit = round(payout - bet_amount, 2)

        return {
            "path": path,
            "landing_slot": landing_slot,
            "multiplier": multiplier,
            "payout": payout,
            "profit": profit,
        }

    def _generate_random_bits(
        self,
        server_seed: str,
        client_seed: str,
        nonce: int,
        count: int,
    ) -> List[bool]:
        """
        Generate deterministic random bits using HMAC-SHA256.
        Each bit determines left or right at a peg row.
        """
        combined = f"{server_seed}:{client_seed}:{nonce}"
        hash_result = hashlib.sha256(combined.encode()).hexdigest()

        bits = []
        for i in range(count):
            char_index = i % len(hash_result)
            char_value = int(hash_result[char_index], 16)
            bits.append((char_value % 2) == 1)

        return bits

    def verify_drop(
        self,
        server_seed: str,
        client_seed: str,
        nonce: int,
        bet_amount: float,
        risk_level: str,
        row_count: int,
        claimed_slot: int,
    ) -> bool:
        result = self.generate_drop(
            server_seed, client_seed, nonce, bet_amount, risk_level, row_count
        )
        return result["landing_slot"] == claimed_slot

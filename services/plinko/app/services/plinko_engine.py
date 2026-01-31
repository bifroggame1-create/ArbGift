import hashlib
import random
from typing import List, Tuple


class PlinkoEngine:
    """
    Plinko game engine with provably fair ball physics simulation

    Grid: 16 rows of pegs (like original Plinko)
    Landing slots: 9 positions (0-8)
    Multipliers match myballs.io pattern
    """

    # Multipliers for each landing slot (left to right)
    # Based on myballs.io screenshot: 💀, 🎁, 2.0x, 0.7x, 0.6x, 0.7x, 2.0x, 🎁, 💀
    MULTIPLIERS = [
        0.0,   # 💀 Death
        0.0,   # 🎁 Loss
        2.0,   # 2.0x
        0.7,   # 0.7x
        0.6,   # 0.6x (center, lowest)
        0.7,   # 0.7x
        2.0,   # 2.0x
        0.0,   # 🎁 Loss
        0.0,   # 💀 Death
    ]

    ROWS = 16  # Number of peg rows
    STARTING_X = 4.5  # Center position (floating point for smooth animation)

    def __init__(self):
        pass

    def generate_server_seed(self) -> str:
        """Generate random server seed"""
        return hashlib.sha256(str(random.random()).encode()).hexdigest()

    def generate_drop(
        self,
        server_seed: str,
        client_seed: str,
        nonce: int,
        bet_amount: float
    ) -> dict:
        """
        Generate a provably fair plinko drop

        Returns:
            {
                'path': [(x, y), ...],  # Ball path coordinates
                'landing_slot': 0-8,     # Final slot index
                'multiplier': 2.0,       # Winning multiplier
                'payout': bet_amount * multiplier,
                'profit': payout - bet_amount
            }
        """
        # Generate random bits for each peg collision
        random_bits = self._generate_random_bits(server_seed, client_seed, nonce, self.ROWS)

        # Simulate ball drop physics
        x = self.STARTING_X
        path = [(x, 0)]

        for row in range(1, self.ROWS + 1):
            # Ball bounces left or right based on random bit
            direction = 1 if random_bits[row - 1] else -1
            x += direction * 0.5  # Each bounce moves 0.5 units

            path.append((x, row))

        # Determine landing slot (quantize final x position)
        # x ranges from roughly 0.5 to 8.5 after 16 rows
        landing_slot = max(0, min(8, int(round(x))))

        multiplier = self.MULTIPLIERS[landing_slot]
        payout = bet_amount * multiplier
        profit = payout - bet_amount

        return {
            'path': path,
            'landing_slot': landing_slot,
            'multiplier': multiplier,
            'payout': payout,
            'profit': profit
        }

    def _generate_random_bits(
        self,
        server_seed: str,
        client_seed: str,
        nonce: int,
        count: int
    ) -> List[bool]:
        """
        Generate deterministic random bits for peg collisions

        Args:
            server_seed: Server seed
            client_seed: Client seed
            nonce: Nonce for uniqueness
            count: Number of bits to generate

        Returns:
            List of boolean values (True = right, False = left)
        """
        combined = f"{server_seed}:{client_seed}:{nonce}"
        hash_result = hashlib.sha256(combined.encode()).hexdigest()

        bits = []
        for i in range(count):
            # Use each hex character
            char_index = i % len(hash_result)
            char_value = int(hash_result[char_index], 16)

            # Use bit parity for randomness
            bit = (char_value % 2) == 1
            bits.append(bit)

        return bits

    def verify_drop(
        self,
        server_seed: str,
        client_seed: str,
        nonce: int,
        bet_amount: float,
        claimed_result: dict
    ) -> bool:
        """Verify that a drop was generated fairly"""
        actual_result = self.generate_drop(server_seed, client_seed, nonce, bet_amount)

        return (
            actual_result['landing_slot'] == claimed_result['landing_slot'] and
            abs(actual_result['multiplier'] - claimed_result['multiplier']) < 0.01
        )

    def get_slot_label(self, slot: int) -> str:
        """Get emoji label for slot"""
        labels = ['💀', '🎁', '2.0x', '0.7x', '0.6x', '0.7x', '2.0x', '🎁', '💀']
        return labels[slot]

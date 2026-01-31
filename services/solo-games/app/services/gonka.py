import hashlib
import random


class GonkaService:
    """
    Gonka (Race) game logic — matches myballs.io solo-race-game

    3x3 grid with multipliers and ball counts.
    Ball count determines probability (weighted random).

    Lite mode grid (from myballs.io):
    X2(6balls)   X1.7(6balls)  X1.5(6balls)
    X1.2(8balls) X1(12balls)   X0.8(12balls)
    X0.5(11balls) X0.3(11balls) X0.1(28balls)

    Hard mode: higher multipliers, fewer balls for top row.

    API mirrors: POST /api/solo-race-game/buy/ton
    """

    CONFIGS = {
        "lite": [
            {"multiplier": 2.0, "balls": 6},
            {"multiplier": 1.7, "balls": 6},
            {"multiplier": 1.5, "balls": 6},
            {"multiplier": 1.2, "balls": 8},
            {"multiplier": 1.0, "balls": 12},
            {"multiplier": 0.8, "balls": 12},
            {"multiplier": 0.5, "balls": 11},
            {"multiplier": 0.3, "balls": 11},
            {"multiplier": 0.1, "balls": 28},
        ],
        "hard": [
            {"multiplier": 3.0, "balls": 4},
            {"multiplier": 2.5, "balls": 4},
            {"multiplier": 2.0, "balls": 4},
            {"multiplier": 1.5, "balls": 6},
            {"multiplier": 1.0, "balls": 10},
            {"multiplier": 0.5, "balls": 14},
            {"multiplier": 0.3, "balls": 18},
            {"multiplier": 0.1, "balls": 24},
            {"multiplier": 0.05, "balls": 40},
        ]
    }

    def generate_seeds(self) -> tuple[str, str]:
        server_seed = hashlib.sha256(str(random.random()).encode()).hexdigest()
        server_seed_hash = hashlib.sha256(server_seed.encode()).hexdigest()
        return server_seed, server_seed_hash

    def determine_cell(self, server_seed: str, client_seed: str, nonce: int, mode: str) -> int:
        """
        Provably fair cell determination using weighted ball distribution.

        More balls in a cell = higher probability of landing there.
        """
        combined = f"{server_seed}:{client_seed}:{nonce}"
        hash_hex = hashlib.sha256(combined.encode()).hexdigest()
        hash_int = int(hash_hex[:8], 16)
        normalized = hash_int / (16 ** 8)

        config = self.CONFIGS.get(mode, self.CONFIGS["lite"])
        total_balls = sum(c["balls"] for c in config)

        cumulative = 0.0
        for i, cell in enumerate(config):
            cumulative += cell["balls"] / total_balls
            if normalized < cumulative:
                return i

        return len(config) - 1

    def play(self, user_id: str, bet_amount: float, mode: str = "lite",
             client_seed: str = "", nonce: int = 0) -> dict:
        """Execute a single Gonka game"""
        server_seed, server_seed_hash = self.generate_seeds()

        cell_index = self.determine_cell(server_seed, client_seed, nonce, mode)
        config = self.CONFIGS.get(mode, self.CONFIGS["lite"])
        cell = config[cell_index]

        multiplier = cell["multiplier"]
        payout = bet_amount * multiplier
        profit = payout - bet_amount

        return {
            "cell_index": cell_index,
            "mode": mode,
            "multiplier": multiplier,
            "balls": cell["balls"],
            "payout": round(payout, 4),
            "profit": round(profit, 4),
            "server_seed": server_seed,
            "server_seed_hash": server_seed_hash,
            "nonce": nonce
        }

    def get_config(self, mode: str) -> list:
        """Get grid configuration for a mode"""
        return self.CONFIGS.get(mode, self.CONFIGS["lite"])

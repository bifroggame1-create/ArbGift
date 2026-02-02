"""
Roulette game engine with provably fair mechanics.
"""
import hashlib
import secrets
from decimal import Decimal
from typing import List, Tuple, Optional

from app.config import settings
from app.models.bet import BetType


class RouletteEngine:
    """Provably fair roulette engine."""
    
    # Color mappings
    RED_NUMBERS = set(settings.RED_NUMBERS)
    BLACK_NUMBERS = set(settings.BLACK_NUMBERS)
    GREEN_NUMBERS = set(settings.GREEN_NUMBERS)
    
    # Payout multipliers
    PAYOUTS = {
        BetType.STRAIGHT: Decimal(str(settings.PAYOUT_STRAIGHT)),
        BetType.SPLIT: Decimal(str(settings.PAYOUT_SPLIT)),
        BetType.STREET: Decimal(str(settings.PAYOUT_STREET)),
        BetType.CORNER: Decimal(str(settings.PAYOUT_CORNER)),
        BetType.LINE: Decimal(str(settings.PAYOUT_LINE)),
        BetType.COLUMN: Decimal(str(settings.PAYOUT_COLUMN)),
        BetType.DOZEN: Decimal(str(settings.PAYOUT_DOZEN)),
        BetType.RED: Decimal(str(settings.PAYOUT_RED_BLACK)),
        BetType.BLACK: Decimal(str(settings.PAYOUT_RED_BLACK)),
        BetType.ODD: Decimal(str(settings.PAYOUT_ODD_EVEN)),
        BetType.EVEN: Decimal(str(settings.PAYOUT_ODD_EVEN)),
        BetType.LOW: Decimal(str(settings.PAYOUT_HIGH_LOW)),
        BetType.HIGH: Decimal(str(settings.PAYOUT_HIGH_LOW)),
    }
    
    @staticmethod
    def generate_server_seed() -> str:
        """Generate cryptographically secure server seed."""
        return secrets.token_hex(settings.SERVER_SEED_LENGTH)
    
    @staticmethod
    def hash_seed(seed: str) -> str:
        """Hash a seed using SHA-256."""
        return hashlib.sha256(seed.encode()).hexdigest()
    
    @classmethod
    def generate_result(
        cls,
        server_seed: str,
        client_seed: str,
        nonce: int,
    ) -> int:
        """
        Generate provably fair roulette result (0-36).
        
        Algorithm:
        1. Combine server_seed + client_seed + nonce
        2. SHA-256 hash the combination
        3. Take first 8 chars as hex, convert to int
        4. Modulo 37 to get number 0-36
        """
        combined = f"{server_seed}:{client_seed}:{nonce}"
        hash_hex = hashlib.sha256(combined.encode()).hexdigest()
        
        # Take first 8 characters (32 bits) for better distribution
        hash_int = int(hash_hex[:8], 16)
        
        # Get result 0-36
        result = hash_int % 37
        
        return result
    
    @classmethod
    def get_color(cls, number: int) -> str:
        """Get color for a roulette number."""
        if number in cls.GREEN_NUMBERS:
            return "green"
        elif number in cls.RED_NUMBERS:
            return "red"
        else:
            return "black"
    
    @classmethod
    def get_payout_multiplier(cls, bet_type: BetType) -> Decimal:
        """Get payout multiplier for bet type."""
        return cls.PAYOUTS.get(bet_type, Decimal("0"))
    
    @classmethod
    def check_bet_wins(
        cls,
        bet_type: BetType,
        bet_value: str,
        winning_number: int,
    ) -> bool:
        """
        Check if a bet wins given the winning number.
        
        Args:
            bet_type: Type of bet
            bet_value: Bet value (number, color, etc.)
            winning_number: The winning roulette number (0-36)
        
        Returns:
            True if bet wins, False otherwise
        """
        winning_color = cls.get_color(winning_number)
        
        if bet_type == BetType.STRAIGHT:
            return int(bet_value) == winning_number
        
        elif bet_type == BetType.SPLIT:
            numbers = [int(n) for n in bet_value.split(",")]
            return winning_number in numbers
        
        elif bet_type == BetType.STREET:
            numbers = [int(n) for n in bet_value.split(",")]
            return winning_number in numbers
        
        elif bet_type == BetType.CORNER:
            numbers = [int(n) for n in bet_value.split(",")]
            return winning_number in numbers
        
        elif bet_type == BetType.LINE:
            numbers = [int(n) for n in bet_value.split(",")]
            return winning_number in numbers
        
        elif bet_type == BetType.COLUMN:
            column = int(bet_value)  # 1, 2, or 3
            if winning_number == 0:
                return False
            return (winning_number - 1) % 3 + 1 == column
        
        elif bet_type == BetType.DOZEN:
            dozen = int(bet_value)  # 1, 2, or 3
            if winning_number == 0:
                return False
            if dozen == 1:
                return 1 <= winning_number <= 12
            elif dozen == 2:
                return 13 <= winning_number <= 24
            else:
                return 25 <= winning_number <= 36
        
        elif bet_type == BetType.RED:
            return winning_color == "red"
        
        elif bet_type == BetType.BLACK:
            return winning_color == "black"
        
        elif bet_type == BetType.ODD:
            return winning_number != 0 and winning_number % 2 == 1
        
        elif bet_type == BetType.EVEN:
            return winning_number != 0 and winning_number % 2 == 0
        
        elif bet_type == BetType.LOW:
            return 1 <= winning_number <= 18
        
        elif bet_type == BetType.HIGH:
            return 19 <= winning_number <= 36
        
        return False
    
    @classmethod
    def calculate_profit(
        cls,
        bet_type: BetType,
        bet_amount: Decimal,
        won: bool,
    ) -> Decimal:
        """Calculate profit for a bet."""
        if not won:
            return -bet_amount
        
        multiplier = cls.get_payout_multiplier(bet_type)
        return bet_amount * multiplier
    
    @classmethod
    def verify_result(
        cls,
        server_seed: str,
        client_seed: str,
        nonce: int,
        claimed_result: int,
    ) -> bool:
        """Verify that a claimed result matches the provably fair calculation."""
        calculated_result = cls.generate_result(server_seed, client_seed, nonce)
        return calculated_result == claimed_result
    
    @classmethod
    def validate_bet(
        cls,
        bet_type: BetType,
        bet_value: str,
        bet_amount: Decimal,
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate a bet.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check bet amount
        min_bet = Decimal(str(settings.MIN_BET_TON))
        max_bet = Decimal(str(settings.MAX_BET_TON))
        
        if bet_amount < min_bet:
            return False, f"Minimum bet is {min_bet} TON"
        
        if bet_amount > max_bet:
            return False, f"Maximum bet is {max_bet} TON"
        
        # Validate bet value based on type
        try:
            if bet_type == BetType.STRAIGHT:
                num = int(bet_value)
                if not (0 <= num <= 36):
                    return False, "Invalid number (must be 0-36)"
            
            elif bet_type in (BetType.SPLIT, BetType.STREET, BetType.CORNER, BetType.LINE):
                numbers = [int(n) for n in bet_value.split(",")]
                if not all(0 <= n <= 36 for n in numbers):
                    return False, "Invalid numbers in bet"
                
                expected_count = {
                    BetType.SPLIT: 2,
                    BetType.STREET: 3,
                    BetType.CORNER: 4,
                    BetType.LINE: 6,
                }
                if len(numbers) != expected_count[bet_type]:
                    return False, f"Expected {expected_count[bet_type]} numbers"
            
            elif bet_type in (BetType.COLUMN, BetType.DOZEN):
                val = int(bet_value)
                if val not in (1, 2, 3):
                    return False, "Invalid column/dozen (must be 1, 2, or 3)"
            
            elif bet_type in (BetType.RED, BetType.BLACK, BetType.ODD, BetType.EVEN, BetType.LOW, BetType.HIGH):
                pass  # No value validation needed
            
            else:
                return False, "Unknown bet type"
        
        except (ValueError, TypeError):
            return False, "Invalid bet value format"
        
        return True, None

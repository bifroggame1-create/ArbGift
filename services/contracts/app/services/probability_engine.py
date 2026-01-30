import hashlib
import secrets
from decimal import Decimal
from typing import Tuple

from app.models.contract import RiskLevel


class ContractProbabilityEngine:
    """
    Provably fair probability engine for Contracts game.

    Implements house edge and risk-based probabilities:
    - Safe: x2 multiplier with 45% success (90% RTP with 5% house edge)
    - Normal: x8 multiplier with 11% success (88% RTP with 5% house edge)
    - Risky: x100 multiplier with 0.9% success (90% RTP with 5% house edge)
    """

    # Risk level configurations
    RISK_MULTIPLIERS = {
        RiskLevel.SAFE: Decimal("2.0"),
        RiskLevel.NORMAL: Decimal("8.0"),
        RiskLevel.RISKY: Decimal("100.0"),
    }

    # Success probabilities
    RISK_PROBABILITIES = {
        RiskLevel.SAFE: Decimal("0.45"),  # 45%
        RiskLevel.NORMAL: Decimal("0.11"),  # 11%
        RiskLevel.RISKY: Decimal("0.009"),  # 0.9%
    }

    # Minimum values per risk level (TON)
    MIN_VALUES = {
        RiskLevel.SAFE: Decimal("1.0"),
        RiskLevel.NORMAL: Decimal("5.0"),
        RiskLevel.RISKY: Decimal("20.0"),
    }

    # House edge
    HOUSE_EDGE = Decimal("0.05")  # 5%

    @classmethod
    def generate_server_seed(cls) -> str:
        """Generate cryptographically secure server seed (128 hex chars)"""
        return secrets.token_hex(64)

    @classmethod
    def hash_server_seed(cls, server_seed: str) -> str:
        """Hash server seed with SHA-256 for client verification"""
        return hashlib.sha256(server_seed.encode()).hexdigest()

    @classmethod
    def calculate_success_probability(
        cls, risk_level: RiskLevel, total_value: Decimal
    ) -> Decimal:
        """
        Calculate success probability for given risk level.

        Args:
            risk_level: The risk level chosen
            total_value: Total input value (not used in current implementation,
                        but kept for future dynamic odds)

        Returns:
            Success probability as Decimal (0.0 - 1.0)
        """
        return cls.RISK_PROBABILITIES[risk_level]

    @classmethod
    def get_multiplier(cls, risk_level: RiskLevel) -> Decimal:
        """Get payout multiplier for risk level"""
        return cls.RISK_MULTIPLIERS[risk_level]

    @classmethod
    def generate_result(
        cls, server_seed: str, client_seed: str, nonce: int, risk_level: RiskLevel
    ) -> bool:
        """
        Generate provably fair result using SHA-256 hash.

        Combines server seed, client seed, and nonce to create deterministic
        random number that can be verified by client.

        Args:
            server_seed: Secret server seed (revealed after execution)
            client_seed: Client-provided seed
            nonce: Incrementing nonce for uniqueness
            risk_level: Risk level to determine success threshold

        Returns:
            True if contract won, False if lost
        """
        # Combine seeds and nonce
        combined = f"{server_seed}:{client_seed}:{nonce}"

        # Generate SHA-256 hash
        hash_hex = hashlib.sha256(combined.encode()).hexdigest()

        # Use first 8 characters (32 bits) as random number
        random_value = int(hash_hex[:8], 16) / (16**8)

        # Get success probability
        success_prob = cls.calculate_success_probability(risk_level, Decimal("0"))

        # Return True if random value is below success probability
        return Decimal(str(random_value)) < success_prob

    @classmethod
    def validate_gift_selection(
        cls, gift_count: int, total_value: Decimal, risk_level: RiskLevel
    ) -> Tuple[bool, str]:
        """
        Validate if gift selection meets requirements for risk level.

        Args:
            gift_count: Number of gifts selected
            total_value: Total value of selected gifts in TON
            risk_level: Risk level chosen

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check gift count
        if gift_count < 2:
            return False, "Minimum 2 gifts required"

        if gift_count > 10:
            return False, "Maximum 10 gifts allowed"

        # Check minimum value for risk level
        min_value = cls.MIN_VALUES[risk_level]
        if total_value < min_value:
            return (
                False,
                f"Minimum {min_value} TON required for {risk_level.value} mode",
            )

        return True, "Valid"

    @classmethod
    def calculate_payout(cls, input_value: Decimal, risk_level: RiskLevel) -> Decimal:
        """
        Calculate payout value for winning contract.

        Args:
            input_value: Total input value in TON
            risk_level: Risk level chosen

        Returns:
            Payout value in TON
        """
        multiplier = cls.get_multiplier(risk_level)
        return input_value * multiplier

    @classmethod
    def verify_result(
        cls,
        server_seed: str,
        client_seed: str,
        nonce: int,
        risk_level: RiskLevel,
        claimed_won: bool,
    ) -> bool:
        """
        Verify that the claimed result matches the actual result.

        Allows client to independently verify fairness after server seed is revealed.

        Args:
            server_seed: Revealed server seed
            client_seed: Client seed
            nonce: Nonce used
            risk_level: Risk level used
            claimed_won: Claimed result (won/lost)

        Returns:
            True if result is valid, False otherwise
        """
        actual_won = cls.generate_result(server_seed, client_seed, nonce, risk_level)
        return actual_won == claimed_won

    @classmethod
    def get_house_edge(cls) -> Decimal:
        """Get house edge percentage"""
        return cls.HOUSE_EDGE

    @classmethod
    def calculate_expected_value(
        cls, input_value: Decimal, risk_level: RiskLevel
    ) -> Decimal:
        """
        Calculate expected value (EV) for a contract.

        Expected Value = (Probability of Win * Payout) - Input Value

        Args:
            input_value: Total input value
            risk_level: Risk level chosen

        Returns:
            Expected value (negative due to house edge)
        """
        probability = cls.calculate_success_probability(risk_level, input_value)
        payout = cls.calculate_payout(input_value, risk_level)

        expected_return = probability * payout
        expected_value = expected_return - input_value

        return expected_value

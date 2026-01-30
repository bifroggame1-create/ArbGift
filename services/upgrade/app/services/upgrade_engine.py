import hashlib
import secrets
from decimal import Decimal
from typing import Tuple, Dict


class UpgradeEngine:
    """
    Provably fair upgrade engine with dynamic probability.

    Probability is calculated based on value ratio:
    - Input value == Target value → 50% success
    - Input value < Target value → Lower success (harder upgrade)
    - Input value > Target value → Higher success (downgrade)

    Formula: probability = BASE_RATE * (input / target)
    Clamped between 1% and 95%
    """

    BASE_SUCCESS_RATE = Decimal("0.50")  # 50% for equal values
    MIN_PROBABILITY = Decimal("0.01")  # 1% minimum
    MAX_PROBABILITY = Decimal("0.95")  # 95% maximum

    @classmethod
    def generate_server_seed(cls) -> str:
        """Generate cryptographically secure server seed"""
        return secrets.token_hex(64)

    @classmethod
    def hash_server_seed(cls, server_seed: str) -> str:
        """Hash server seed with SHA-256"""
        return hashlib.sha256(server_seed.encode()).hexdigest()

    @classmethod
    def calculate_success_probability(
        cls, input_value: Decimal, target_value: Decimal
    ) -> Decimal:
        """
        Calculate dynamic success probability based on value difference.

        Examples:
        - Input: 5 TON, Target: 5 TON (1:1) → 50%
        - Input: 5 TON, Target: 10 TON (1:2) → 25%
        - Input: 10 TON, Target: 5 TON (2:1) → 95% (clamped)
        - Input: 5 TON, Target: 50 TON (1:10) → 5%
        - Input: 1 TON, Target: 100 TON (1:100) → 1% (clamped)

        Args:
            input_value: Value of input gift in TON
            target_value: Value of target gift in TON

        Returns:
            Success probability as Decimal (0.01 - 0.95)
        """
        if target_value <= Decimal("0"):
            return Decimal("0")

        # Calculate ratio
        ratio = input_value / target_value

        # Apply base rate
        probability = cls.BASE_SUCCESS_RATE * ratio

        # Clamp between min and max
        probability = max(cls.MIN_PROBABILITY, min(probability, cls.MAX_PROBABILITY))

        return probability

    @classmethod
    def generate_wheel_sectors(cls, probability: Decimal) -> Dict[str, float]:
        """
        Generate wheel sector angles for frontend visualization.

        The wheel is divided into success (green) and fail (red) sectors.
        The success sector size is proportional to the probability.

        Args:
            probability: Success probability (0.0 - 1.0)

        Returns:
            Dictionary with success_angle and fail_angle in degrees
        """
        success_degrees = float(probability * 360)
        fail_degrees = 360 - success_degrees

        return {
            "success_angle": success_degrees,
            "fail_angle": fail_degrees,
        }

    @classmethod
    def generate_result(
        cls, server_seed: str, client_seed: str, nonce: int, probability: Decimal
    ) -> Tuple[bool, Decimal]:
        """
        Generate provably fair result with wheel angle.

        Uses SHA-256 hash to generate deterministic result that can be verified.

        Args:
            server_seed: Secret server seed
            client_seed: Client-provided seed
            nonce: Incrementing nonce
            probability: Success probability

        Returns:
            Tuple of (won: bool, result_angle: Decimal)
            result_angle is where the wheel lands (0-360 degrees)
        """
        # Combine seeds and nonce
        combined = f"{server_seed}:{client_seed}:{nonce}"

        # Generate SHA-256 hash
        hash_hex = hashlib.sha256(combined.encode()).hexdigest()

        # Use first 8 characters (32 bits) as random value
        random_value = Decimal(int(hash_hex[:8], 16)) / Decimal(16**8)

        # Determine success
        won = random_value < probability

        # Calculate result angle (0-360)
        # The angle represents where the wheel needle lands
        result_angle = random_value * 360

        return won, result_angle

    @classmethod
    def verify_result(
        cls,
        server_seed: str,
        client_seed: str,
        nonce: int,
        probability: Decimal,
        claimed_won: bool,
        claimed_angle: Decimal,
    ) -> bool:
        """
        Verify upgrade result for provable fairness.

        Args:
            server_seed: Revealed server seed
            client_seed: Client seed
            nonce: Nonce used
            probability: Success probability
            claimed_won: Claimed win/loss
            claimed_angle: Claimed result angle

        Returns:
            True if result is valid, False otherwise
        """
        actual_won, actual_angle = cls.generate_result(
            server_seed, client_seed, nonce, probability
        )

        # Check if won status matches
        won_matches = actual_won == claimed_won

        # Check if angle is close (within 0.1 degrees due to float precision)
        angle_matches = abs(actual_angle - claimed_angle) < Decimal("0.1")

        return won_matches and angle_matches

    @classmethod
    def validate_upgrade(
        cls, input_value: Decimal, target_value: Decimal
    ) -> Tuple[bool, str]:
        """
        Validate if upgrade is allowed.

        Args:
            input_value: Input gift value
            target_value: Target gift value

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check if values are positive
        if input_value <= Decimal("0"):
            return False, "Input gift value must be positive"

        if target_value <= Decimal("0"):
            return False, "Target gift value must be positive"

        # Check if values are different (no point upgrading to same value)
        if input_value == target_value:
            return False, "Input and target gifts must have different values"

        # All good
        return True, "Valid"

    @classmethod
    def calculate_expected_value(
        cls, input_value: Decimal, target_value: Decimal
    ) -> Decimal:
        """
        Calculate expected value for an upgrade.

        Expected Value = (Probability * Target Value) - Input Value

        Args:
            input_value: Input gift value
            target_value: Target gift value

        Returns:
            Expected value (typically negative due to risk)
        """
        probability = cls.calculate_success_probability(input_value, target_value)
        expected_return = probability * target_value
        expected_value = expected_return - input_value

        return expected_value

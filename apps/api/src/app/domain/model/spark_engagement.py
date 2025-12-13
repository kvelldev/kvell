"""SparkEngagement Value Object.

This module defines the SparkEngagement value object for tracking
user engagement metrics on a spark.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class SparkEngagement:
    """Value object representing engagement metrics for a spark.

    Attributes:
        spark_id: The spark this engagement belongs to
        unique_user_count: Number of unique users who interacted
        fuel_count: Number of fuel actions
        reply_count: Number of replies (future feature)
        fuel_weight: Weight for fuel actions in heat score calculation
        reply_weight: Weight for reply actions in heat score calculation

    Heat Score Calculation:
        heat_score = (fuel_count * fuel_weight) + (reply_count * reply_weight)
    """

    spark_id: str
    unique_user_count: int
    fuel_count: int
    reply_count: int = 0
    fuel_weight: int = 1
    reply_weight: int = 5

    @property
    def heat_score(self) -> int:
        """Calculate heat score from weighted actions.

        Returns:
            Heat score based on fuel and reply counts with weights

        """
        return (self.fuel_count * self.fuel_weight) + (
            self.reply_count * self.reply_weight
        )

    def can_promote_to_kindling(self, threshold_uu: int = 3) -> bool:
        """Check if spark can be promoted to kindling.

        Args:
            threshold_uu: Required unique user count (default: 3)

        Returns:
            True if unique user count meets threshold

        """
        return self.unique_user_count >= threshold_uu

    def can_promote_to_bonfire(
        self,
        threshold_uu: int,
        threshold_heat_score: int = 50,
    ) -> bool:
        """Check if spark can be promoted to bonfire.

        Both conditions must be met (AND logic):
        1. Unique user count >= threshold_uu
        2. Heat score >= threshold_heat_score

        This prevents 1vs1 trolling: even if two users spam actions,
        they cannot meet the UU threshold.

        Args:
            threshold_uu: Required unique user count (dynamic, 10-50)
            threshold_heat_score: Required heat score (default: 50)

        Returns:
            True if both conditions are met

        """
        return (
            self.unique_user_count >= threshold_uu
            and self.heat_score >= threshold_heat_score
        )

"""Ignition Service.

Domain service for spark promotion logic (Spark -> Kindling -> Bonfire).
"""

from dataclasses import dataclass

from app.domain.model.spark import SparkLevel
from app.domain.model.spark_engagement import SparkEngagement


@dataclass(frozen=True)
class PromotionResult:
    """Result of promotion check.

    Attributes:
        should_promote: Whether promotion should occur
        target_level: Target level after promotion (or current level if no promotion)
        reason: Human-readable reason for the decision

    """

    should_promote: bool
    target_level: SparkLevel
    reason: str


class IgnitionService:
    """Domain service for spark promotion logic.

    This service determines whether a spark should be promoted
    based on engagement metrics and thresholds.

    Promotion Rules:
    1. Spark -> Kindling: UU >= kindling_threshold (fixed: 3)
    2. Kindling -> Bonfire: UU >= bonfire_threshold (dynamic: 10-50)
                           AND heat_score >= heat_threshold (fixed: 50)

    Anti-Troll Logic:
    - The UU requirement prevents 1vs1 spam from reaching Bonfire
    - Even with high heat_score, insufficient UU blocks promotion
    """

    def check_promotion(
        self,
        current_level: SparkLevel,
        engagement: SparkEngagement,
        kindling_threshold_uu: int,
        bonfire_threshold_uu: int,
        heat_score_threshold: int,
    ) -> PromotionResult:
        """Check if a spark should be promoted.

        Args:
            current_level: Current spark level
            engagement: Current engagement metrics
            kindling_threshold_uu: UU threshold for kindling (fixed, e.g., 3)
            bonfire_threshold_uu: UU threshold for bonfire (dynamic, 10-50)
            heat_score_threshold: Heat score threshold for bonfire (e.g., 50)

        Returns:
            PromotionResult indicating whether and how to promote

        """
        # Already at max level
        if current_level == SparkLevel.BONFIRE:
            return PromotionResult(
                should_promote=False,
                target_level=SparkLevel.BONFIRE,
                reason="Already at maximum level (bonfire)",
            )

        # Check for Bonfire promotion (from Spark or Kindling)
        if engagement.can_promote_to_bonfire(
            threshold_uu=bonfire_threshold_uu,
            threshold_heat_score=heat_score_threshold,
        ):
            return PromotionResult(
                should_promote=True,
                target_level=SparkLevel.BONFIRE,
                reason=(
                    f"Bonfire promotion: UU={engagement.unique_user_count} >= "
                    f"{bonfire_threshold_uu}, heat_score={engagement.heat_score} >= "
                    f"{heat_score_threshold}"
                ),
            )

        # Check for Kindling promotion (from Spark only)
        if current_level == SparkLevel.SPARK:
            if engagement.can_promote_to_kindling(threshold_uu=kindling_threshold_uu):
                return PromotionResult(
                    should_promote=True,
                    target_level=SparkLevel.KINDLING,
                    reason=(
                        f"Kindling promotion: UU={engagement.unique_user_count} >= "
                        f"{kindling_threshold_uu}"
                    ),
                )

        # No promotion
        return PromotionResult(
            should_promote=False,
            target_level=current_level,
            reason=self._get_no_promotion_reason(
                current_level,
                engagement,
                kindling_threshold_uu,
                bonfire_threshold_uu,
                heat_score_threshold,
            ),
        )

    def _get_no_promotion_reason(
        self,
        current_level: SparkLevel,
        engagement: SparkEngagement,
        kindling_threshold_uu: int,
        bonfire_threshold_uu: int,
        heat_score_threshold: int,
    ) -> str:
        """Generate human-readable reason for no promotion."""
        if current_level == SparkLevel.SPARK:
            return (
                f"Not enough engagement for kindling: "
                f"UU={engagement.unique_user_count} < {kindling_threshold_uu}"
            )

        # Kindling level - need both UU and heat_score for bonfire
        reasons: list[str] = []
        if engagement.unique_user_count < bonfire_threshold_uu:
            reasons.append(
                f"UU={engagement.unique_user_count} < {bonfire_threshold_uu}"
            )
        if engagement.heat_score < heat_score_threshold:
            reasons.append(
                f"heat_score={engagement.heat_score} < {heat_score_threshold}"
            )
        return f"Not enough engagement for bonfire: {', '.join(reasons)}"

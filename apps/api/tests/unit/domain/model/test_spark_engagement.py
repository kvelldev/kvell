"""Unit tests for SparkEngagement value object."""

import pytest

from app.domain.model.spark_engagement import SparkEngagement


class TestSparkEngagement:
    """Tests for SparkEngagement value object."""

    # Heat Score calculation tests

    def test_heatScore_withOnlyFuel_calculatesCorrectly(self) -> None:
        """Heat score with only fuel actions."""
        engagement = SparkEngagement(
            spark_id="spark-1",
            unique_user_count=5,
            fuel_count=10,
            reply_count=0,
        )
        # fuel_count * 1 + reply_count * 5 = 10 * 1 + 0 * 5 = 10
        assert engagement.heat_score == 10

    def test_heatScore_withOnlyReplies_calculatesCorrectly(self) -> None:
        """Heat score with only reply actions."""
        engagement = SparkEngagement(
            spark_id="spark-1",
            unique_user_count=5,
            fuel_count=0,
            reply_count=10,
        )
        # fuel_count * 1 + reply_count * 5 = 0 * 1 + 10 * 5 = 50
        assert engagement.heat_score == 50

    def test_heatScore_withBothActions_calculatesCorrectly(self) -> None:
        """Heat score with both fuel and reply actions."""
        engagement = SparkEngagement(
            spark_id="spark-1",
            unique_user_count=10,
            fuel_count=20,
            reply_count=6,
        )
        # fuel_count * 1 + reply_count * 5 = 20 * 1 + 6 * 5 = 50
        assert engagement.heat_score == 50

    def test_heatScore_withZeroActions_returnsZero(self) -> None:
        """Heat score with no actions returns zero."""
        engagement = SparkEngagement(
            spark_id="spark-1",
            unique_user_count=0,
            fuel_count=0,
            reply_count=0,
        )
        assert engagement.heat_score == 0

    # Kindling promotion tests

    def test_canPromoteToKindling_whenAboveThreshold_returnsTrue(self) -> None:
        """Can promote to kindling when UU meets threshold."""
        engagement = SparkEngagement(
            spark_id="spark-1",
            unique_user_count=3,
            fuel_count=5,
        )
        assert engagement.can_promote_to_kindling(threshold_uu=3) is True

    def test_canPromoteToKindling_whenExactlyAtThreshold_returnsTrue(self) -> None:
        """Can promote to kindling when UU equals threshold."""
        engagement = SparkEngagement(
            spark_id="spark-1",
            unique_user_count=3,
            fuel_count=5,
        )
        assert engagement.can_promote_to_kindling(threshold_uu=3) is True

    def test_canPromoteToKindling_whenBelowThreshold_returnsFalse(self) -> None:
        """Cannot promote to kindling when UU below threshold."""
        engagement = SparkEngagement(
            spark_id="spark-1",
            unique_user_count=2,
            fuel_count=100,  # High fuel but low UU
        )
        assert engagement.can_promote_to_kindling(threshold_uu=3) is False

    # Bonfire promotion tests

    def test_canPromoteToBonfire_whenBothConditionsMet_returnsTrue(self) -> None:
        """Can promote to bonfire when both UU and heat_score meet thresholds."""
        engagement = SparkEngagement(
            spark_id="spark-1",
            unique_user_count=10,
            fuel_count=50,  # heat_score = 50
        )
        assert (
            engagement.can_promote_to_bonfire(
                threshold_uu=10,
                threshold_heat_score=50,
            )
            is True
        )

    def test_canPromoteToBonfire_whenOnlyUUMet_returnsFalse(self) -> None:
        """Cannot promote when only UU threshold is met."""
        engagement = SparkEngagement(
            spark_id="spark-1",
            unique_user_count=10,
            fuel_count=10,  # heat_score = 10 < 50
        )
        assert (
            engagement.can_promote_to_bonfire(
                threshold_uu=10,
                threshold_heat_score=50,
            )
            is False
        )

    def test_canPromoteToBonfire_whenOnlyHeatScoreMet_returnsFalse(self) -> None:
        """Cannot promote when only heat_score threshold is met (Anti-troll)."""
        engagement = SparkEngagement(
            spark_id="spark-1",
            unique_user_count=2,  # Two trolls spamming
            fuel_count=100,  # heat_score = 100 > 50
        )
        assert (
            engagement.can_promote_to_bonfire(
                threshold_uu=10,
                threshold_heat_score=50,
            )
            is False
        )

    def test_canPromoteToBonfire_antiTrollLogic_twoUsersCantPromote(self) -> None:
        """Anti-troll: Two users cannot promote to bonfire regardless of actions.

        This is the core anti-troll logic. Even if 2 users spam many actions,
        they cannot meet the UU threshold (10), blocking promotion.
        """
        # Simulate two trolls with massive engagement
        engagement = SparkEngagement(
            spark_id="spark-1",
            unique_user_count=2,  # Only 2 users (1vs1)
            fuel_count=1000,  # Huge engagement
            reply_count=1000,  # heat_score = 1000 + 5000 = 6000
        )
        # Even with heat_score=6000, UU=2 blocks promotion
        assert (
            engagement.can_promote_to_bonfire(
                threshold_uu=10,
                threshold_heat_score=50,
            )
            is False
        )

    def test_canPromoteToBonfire_withDynamicThreshold_respectsValue(self) -> None:
        """Bonfire promotion respects dynamic UU threshold."""
        engagement = SparkEngagement(
            spark_id="spark-1",
            unique_user_count=30,
            fuel_count=100,  # heat_score = 100
        )

        # With threshold=10, should pass
        assert (
            engagement.can_promote_to_bonfire(threshold_uu=10, threshold_heat_score=50)
            is True
        )

        # With threshold=50 (max cap), should fail
        assert (
            engagement.can_promote_to_bonfire(threshold_uu=50, threshold_heat_score=50)
            is False
        )

    # Edge cases

    def test_engagement_withDefaultReplyCount_isZero(self) -> None:
        """Default reply_count is zero."""
        engagement = SparkEngagement(
            spark_id="spark-1",
            unique_user_count=1,
            fuel_count=1,
        )
        assert engagement.reply_count == 0

    def test_engagement_isFrozen(self) -> None:
        """SparkEngagement is immutable (frozen dataclass)."""
        engagement = SparkEngagement(
            spark_id="spark-1",
            unique_user_count=1,
            fuel_count=1,
        )
        with pytest.raises(AttributeError):
            engagement.fuel_count = 10  # type: ignore[misc]

"""Unit tests for IgnitionService domain service."""

import pytest

from app.domain.model.spark import SparkLevel
from app.domain.model.spark_engagement import SparkEngagement
from app.domain.service.ignition_service import IgnitionService, PromotionResult


class TestIgnitionService:
    """Tests for IgnitionService domain service."""

    @pytest.fixture
    def service(self) -> IgnitionService:
        """Create IgnitionService instance."""
        return IgnitionService()

    # Default thresholds for tests
    KINDLING_THRESHOLD = 3
    BONFIRE_THRESHOLD = 10
    HEAT_THRESHOLD = 50

    # Spark -> Kindling promotion tests

    def test_checkPromotion_sparkToKindling_whenUUMeetsThreshold_promotes(
        self,
        service: IgnitionService,
    ) -> None:
        """Spark promotes to kindling when UU meets threshold."""
        engagement = SparkEngagement(
            spark_id="spark-1",
            unique_user_count=3,
            fuel_count=5,
        )

        result = service.check_promotion(
            current_level=SparkLevel.SPARK,
            engagement=engagement,
            kindling_threshold_uu=self.KINDLING_THRESHOLD,
            bonfire_threshold_uu=self.BONFIRE_THRESHOLD,
            heat_score_threshold=self.HEAT_THRESHOLD,
        )

        assert result.should_promote is True
        assert result.target_level == SparkLevel.KINDLING
        assert "UU=3 >= 3" in result.reason

    def test_checkPromotion_sparkToKindling_whenUUBelowThreshold_noPromotion(
        self,
        service: IgnitionService,
    ) -> None:
        """Spark does not promote when UU below threshold."""
        engagement = SparkEngagement(
            spark_id="spark-1",
            unique_user_count=2,
            fuel_count=100,  # High fuel but low UU
        )

        result = service.check_promotion(
            current_level=SparkLevel.SPARK,
            engagement=engagement,
            kindling_threshold_uu=self.KINDLING_THRESHOLD,
            bonfire_threshold_uu=self.BONFIRE_THRESHOLD,
            heat_score_threshold=self.HEAT_THRESHOLD,
        )

        assert result.should_promote is False
        assert result.target_level == SparkLevel.SPARK
        assert "UU=2 < 3" in result.reason

    # Spark -> Bonfire direct promotion tests

    def test_checkPromotion_sparkToBonfire_whenBothConditionsMet_promotesDirectly(
        self,
        service: IgnitionService,
    ) -> None:
        """Spark can promote directly to bonfire (skipping kindling)."""
        engagement = SparkEngagement(
            spark_id="spark-1",
            unique_user_count=15,
            fuel_count=60,  # heat_score = 60
        )

        result = service.check_promotion(
            current_level=SparkLevel.SPARK,
            engagement=engagement,
            kindling_threshold_uu=self.KINDLING_THRESHOLD,
            bonfire_threshold_uu=self.BONFIRE_THRESHOLD,
            heat_score_threshold=self.HEAT_THRESHOLD,
        )

        assert result.should_promote is True
        assert result.target_level == SparkLevel.BONFIRE
        assert "UU=15 >= 10" in result.reason
        assert "heat_score=60 >= 50" in result.reason

    # Kindling -> Bonfire promotion tests

    def test_checkPromotion_kindlingToBonfire_whenConditionsMet_promotes(
        self,
        service: IgnitionService,
    ) -> None:
        """Kindling promotes to bonfire when conditions met."""
        engagement = SparkEngagement(
            spark_id="spark-1",
            unique_user_count=12,
            fuel_count=55,  # heat_score = 55
        )

        result = service.check_promotion(
            current_level=SparkLevel.KINDLING,
            engagement=engagement,
            kindling_threshold_uu=self.KINDLING_THRESHOLD,
            bonfire_threshold_uu=self.BONFIRE_THRESHOLD,
            heat_score_threshold=self.HEAT_THRESHOLD,
        )

        assert result.should_promote is True
        assert result.target_level == SparkLevel.BONFIRE

    def test_checkPromotion_kindlingToBonfire_whenOnlyUUMet_noPromotion(
        self,
        service: IgnitionService,
    ) -> None:
        """Kindling does not promote when only UU met."""
        engagement = SparkEngagement(
            spark_id="spark-1",
            unique_user_count=15,
            fuel_count=30,  # heat_score = 30 < 50
        )

        result = service.check_promotion(
            current_level=SparkLevel.KINDLING,
            engagement=engagement,
            kindling_threshold_uu=self.KINDLING_THRESHOLD,
            bonfire_threshold_uu=self.BONFIRE_THRESHOLD,
            heat_score_threshold=self.HEAT_THRESHOLD,
        )

        assert result.should_promote is False
        assert result.target_level == SparkLevel.KINDLING
        assert "heat_score=30 < 50" in result.reason

    def test_checkPromotion_kindlingToBonfire_whenOnlyHeatScoreMet_noPromotion(
        self,
        service: IgnitionService,
    ) -> None:
        """Kindling does not promote when only heat_score met (Anti-troll)."""
        engagement = SparkEngagement(
            spark_id="spark-1",
            unique_user_count=5,  # Below bonfire threshold
            fuel_count=100,  # heat_score = 100 > 50
        )

        result = service.check_promotion(
            current_level=SparkLevel.KINDLING,
            engagement=engagement,
            kindling_threshold_uu=self.KINDLING_THRESHOLD,
            bonfire_threshold_uu=self.BONFIRE_THRESHOLD,
            heat_score_threshold=self.HEAT_THRESHOLD,
        )

        assert result.should_promote is False
        assert result.target_level == SparkLevel.KINDLING
        assert "UU=5 < 10" in result.reason

    # Bonfire level (no further promotion)

    def test_checkPromotion_alreadyBonfire_noPromotion(
        self,
        service: IgnitionService,
    ) -> None:
        """Bonfire level cannot be promoted further."""
        engagement = SparkEngagement(
            spark_id="spark-1",
            unique_user_count=100,
            fuel_count=1000,
        )

        result = service.check_promotion(
            current_level=SparkLevel.BONFIRE,
            engagement=engagement,
            kindling_threshold_uu=self.KINDLING_THRESHOLD,
            bonfire_threshold_uu=self.BONFIRE_THRESHOLD,
            heat_score_threshold=self.HEAT_THRESHOLD,
        )

        assert result.should_promote is False
        assert result.target_level == SparkLevel.BONFIRE
        assert "Already at maximum level" in result.reason

    # Anti-troll logic tests

    def test_checkPromotion_antiTroll_twoUsersCantReachBonfire(
        self,
        service: IgnitionService,
    ) -> None:
        """Two users (1vs1) cannot promote to bonfire regardless of activity.

        This is the core anti-troll test. Even with massive engagement
        from 2 users, they cannot meet the UU threshold.
        """
        # Simulate two trolls spamming
        engagement = SparkEngagement(
            spark_id="spark-1",
            unique_user_count=2,
            fuel_count=10000,
            reply_count=10000,  # heat_score = 10000 + 50000 = 60000
        )

        result = service.check_promotion(
            current_level=SparkLevel.KINDLING,
            engagement=engagement,
            kindling_threshold_uu=self.KINDLING_THRESHOLD,
            bonfire_threshold_uu=self.BONFIRE_THRESHOLD,
            heat_score_threshold=self.HEAT_THRESHOLD,
        )

        assert result.should_promote is False
        assert result.target_level == SparkLevel.KINDLING
        assert "UU=2 < 10" in result.reason

    # Dynamic threshold tests

    def test_checkPromotion_withHighBonfireThreshold_requiresMoreUsers(
        self,
        service: IgnitionService,
    ) -> None:
        """Higher bonfire threshold requires more users."""
        engagement = SparkEngagement(
            spark_id="spark-1",
            unique_user_count=30,
            fuel_count=100,  # heat_score = 100
        )

        # With threshold=50 (max cap), 30 users is not enough
        result = service.check_promotion(
            current_level=SparkLevel.KINDLING,
            engagement=engagement,
            kindling_threshold_uu=self.KINDLING_THRESHOLD,
            bonfire_threshold_uu=50,  # Max cap
            heat_score_threshold=self.HEAT_THRESHOLD,
        )

        assert result.should_promote is False
        assert "UU=30 < 50" in result.reason

    def test_checkPromotion_withLowBonfireThreshold_acceptsFewerUsers(
        self,
        service: IgnitionService,
    ) -> None:
        """Lower bonfire threshold accepts fewer users."""
        engagement = SparkEngagement(
            spark_id="spark-1",
            unique_user_count=10,
            fuel_count=50,  # heat_score = 50
        )

        # With threshold=10 (min cap), 10 users is exactly enough
        result = service.check_promotion(
            current_level=SparkLevel.KINDLING,
            engagement=engagement,
            kindling_threshold_uu=self.KINDLING_THRESHOLD,
            bonfire_threshold_uu=10,  # Min cap
            heat_score_threshold=self.HEAT_THRESHOLD,
        )

        assert result.should_promote is True
        assert result.target_level == SparkLevel.BONFIRE

    # PromotionResult dataclass test

    def test_promotionResult_isFrozen(self) -> None:
        """PromotionResult is immutable."""
        result = PromotionResult(
            should_promote=True,
            target_level=SparkLevel.KINDLING,
            reason="Test reason",
        )

        with pytest.raises(AttributeError):
            result.should_promote = False  # type: ignore[misc]

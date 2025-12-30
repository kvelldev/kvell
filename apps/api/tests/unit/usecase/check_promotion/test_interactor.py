"""Unit tests for CheckPromotionInteractor.

This module tests the business logic of spark promotion checks,
specifically verifying the TTL fix for Bonfire creation.
"""

from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, Mock, patch

import pytest

from app.domain.constants import (
    BONFIRE_INITIAL_TTL_HOURS,
    FUEL_WEIGHT,
    LOG_EVENTS,
    REPLY_WEIGHT,
)
from app.domain.model.bonfire import Bonfire
from app.domain.model.spark import Spark, SparkLevel
from app.domain.model.spark_engagement import SparkEngagement
from app.domain.repository.bonfire_repository import IBonfireRepository
from app.domain.repository.spark_repository import ISparkRepository
from app.domain.repository.threshold_config_repository import IThresholdConfigRepository
from app.domain.service.ignition_service import IgnitionService, PromotionResult
from app.usecase.check_promotion.interactor import CheckPromotionInteractor
from app.usecase.check_promotion.interface import CheckPromotionInput
from app.usecase.ports.logger import ILogger
from app.usecase.ports.pubsub import IPubSubGateway


class TestCheckPromotionInteractor:
    """Test suite for CheckPromotionInteractor."""

    @pytest.fixture
    def mock_spark_repo(self) -> AsyncMock:
        return AsyncMock(spec=ISparkRepository)

    @pytest.fixture
    def mock_bonfire_repo(self) -> AsyncMock:
        return AsyncMock(spec=IBonfireRepository)

    @pytest.fixture
    def mock_threshold_config(self) -> AsyncMock:
        return AsyncMock(spec=IThresholdConfigRepository)

    @pytest.fixture
    def mock_ignition_service(self) -> Mock:
        return Mock(spec=IgnitionService)

    @pytest.fixture
    def mock_pubsub(self) -> AsyncMock:
        return AsyncMock(spec=IPubSubGateway)

    @pytest.fixture
    def mock_logger(self) -> Mock:
        return Mock(spec=ILogger)

    @pytest.fixture
    def interactor(
        self,
        mock_spark_repo,
        mock_bonfire_repo,
        mock_threshold_config,
        mock_ignition_service,
        mock_pubsub,
        mock_logger,
    ) -> CheckPromotionInteractor:
        return CheckPromotionInteractor(
            spark_repository=mock_spark_repo,
            bonfire_repository=mock_bonfire_repo,
            threshold_config=mock_threshold_config,
            ignition_service=mock_ignition_service,
            pubsub=mock_pubsub,
            logger=mock_logger,
        )

    @pytest.mark.asyncio
    async def test_execute_whenPromotedToBonfire_usesCorrectTTL(
        self,
        interactor,
        mock_spark_repo,
        mock_bonfire_repo,
        mock_threshold_config,
        mock_ignition_service,
    ) -> None:
        """Test that Bonfire is created with the correct 120h TTL."""
        # Arrange
        spark_id = "spark_123"
        input_data = CheckPromotionInput(spark_id=spark_id)
        now = datetime.now(UTC)

        spark = Spark(
            id=spark_id,
            content="Test content",
            user_hash="user_hash",
            fuel_count=100,
            field_id="sakurazaka46",
            level=SparkLevel.KINDLING,  # promoting from kindling
            created_at=now,
            decay_at=now + timedelta(hours=3),
            vanish_at=now + timedelta(days=7),
        )
        mock_spark_repo.find_by_id.return_value = spark

        engagement = SparkEngagement(
            spark_id=spark_id,
            unique_user_count=50,
            fuel_count=100,
            reply_count=5,
            fuel_weight=FUEL_WEIGHT,
            reply_weight=REPLY_WEIGHT,
        )
        mock_spark_repo.get_engagement.return_value = engagement

        mock_threshold_config.get_bonfire_threshold_uu.return_value = 10
        mock_threshold_config.get_heat_score_threshold.return_value = 50

        # Mock ignition service to return promotion decision
        mock_ignition_service.check_promotion.return_value = PromotionResult(
            should_promote=True,
            target_level=SparkLevel.BONFIRE,
            reason="High engagement",
        )

        # Act
        await interactor.execute(input_data)

        # Assert
        # Verify Bonfire.create was called (indirectly via save)
        # Note: Bonfire.create is a static method, hard to mock without patching the class.
        # Instead, we verify the Bonfire object passed to save has the correct decay_at.

        # We expect decay_at to be roughly NOW + 120 hours.
        # Since we can't control 'now' inside Bonfire.create without mocking datetime,
        # we'll check if it's within a reasonable range.

        call_args = mock_bonfire_repo.save.call_args
        assert call_args is not None
        saved_bonfire = call_args[0][0]

        assert isinstance(saved_bonfire, Bonfire)
        assert saved_bonfire.id == spark_id

        # Calculate expected decay time range
        # Note: Bonfire.create calls datetime.now(UTC) internally.
        # It should be close to 'now' + 120h.
        expected_ttl = timedelta(hours=BONFIRE_INITIAL_TTL_HOURS)
        time_diff = saved_bonfire.decay_at - (datetime.now(UTC) + expected_ttl)

        # Allow 1 second difference for execution time
        assert abs(time_diff.total_seconds()) < 1.0, \
            f"Bonfire decay_at {saved_bonfire.decay_at} is not ~120h from now"


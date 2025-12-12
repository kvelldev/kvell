"""Unit tests for AddFuelInteractor.

This module tests the business logic of adding fuel to sparks.
"""

from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, Mock

import pytest

from app.domain.constants import LOG_EVENTS
from app.domain.exception import AppError
from app.domain.model.spark import Spark
from app.domain.repository.spark_repository import ISparkRepository
from app.usecase.add_fuel.interactor import AddFuelInteractor
from app.usecase.add_fuel.interface import AddFuelInput
from app.usecase.ports.logger import ILogger


class TestAddFuelInteractor:
    """Test suite for AddFuelInteractor."""

    @pytest.fixture
    def mock_spark_repo(self) -> AsyncMock:
        """Create a mock spark repository."""
        return AsyncMock(spec=ISparkRepository)

    @pytest.fixture
    def mock_logger(self) -> Mock:
        """Create a mock logger."""
        return Mock(spec=ILogger)

    @pytest.fixture
    def interactor(
        self,
        mock_spark_repo: AsyncMock,
        mock_logger: Mock,
    ) -> AddFuelInteractor:
        """Create an AddFuelInteractor instance."""
        return AddFuelInteractor(
            spark_repository=mock_spark_repo,
            logger=mock_logger,
        )

    @pytest.fixture
    def active_spark(self) -> Spark:
        """Create an active spark for testing."""
        now = datetime.now(UTC)
        return Spark(
            id="spark_123",
            content="Test spark",
            user_hash="author_hash",
            fuel_count=10,
            created_at=now,
            decay_at=now + timedelta(minutes=10),  # Still active
            vanish_at=now + timedelta(days=7),
        )

    @pytest.fixture
    def decayed_spark(self) -> Spark:
        """Create a decayed spark for testing."""
        now = datetime.now(UTC)
        return Spark(
            id="spark_456",
            content="Old spark",
            user_hash="author_hash",
            fuel_count=5,
            created_at=now - timedelta(minutes=20),
            decay_at=now - timedelta(minutes=10),  # Already decayed
            vanish_at=now + timedelta(days=7),
        )

    @pytest.mark.asyncio
    async def test_execute_whenFirstTimeFuel_returnsSuccessAndIncrementsCount(
        self,
        interactor: AddFuelInteractor,
        mock_spark_repo: AsyncMock,
        mock_logger: Mock,
        active_spark: Spark,
    ) -> None:
        """First-time fuel add should increment count."""
        # Arrange
        input_data = AddFuelInput(spark_id="spark_123", user_hash="user_hash_B")
        mock_spark_repo.find_by_id.return_value = active_spark
        mock_spark_repo.try_add_fuel.return_value = True

        # Act
        output = await interactor.execute(input_data)

        # Assert
        assert output.success is True
        mock_spark_repo.find_by_id.assert_awaited_once_with("spark_123")
        mock_spark_repo.try_add_fuel.assert_awaited_once_with(
            "spark_123",
            "user_hash_B",
        )
        mock_logger.info.assert_any_call(
            LOG_EVENTS.FUEL_ADD_STARTED,
            "Add fuel request received",
            context={"spark_id": "spark_123", "user_hash": "user_hash_B"},
        )
        mock_logger.info.assert_any_call(
            LOG_EVENTS.FUEL_ADD_SUCCESS,
            "Fuel added successfully",
            context={"spark_id": "spark_123", "fuel_added": True},
        )

    @pytest.mark.asyncio
    async def test_execute_whenAlreadyFueled_returnsSuccessWithoutIncrement(
        self,
        interactor: AddFuelInteractor,
        mock_spark_repo: AsyncMock,
        mock_logger: Mock,
        active_spark: Spark,
    ) -> None:
        """Idempotent fuel add should return success but not increment."""
        # Arrange
        input_data = AddFuelInput(spark_id="spark_123", user_hash="user_hash_B")
        mock_spark_repo.find_by_id.return_value = active_spark
        mock_spark_repo.try_add_fuel.return_value = False  # Already fueled

        # Act
        output = await interactor.execute(input_data)

        # Assert
        assert output.success is True
        mock_spark_repo.try_add_fuel.assert_awaited_once_with(
            "spark_123",
            "user_hash_B",
        )
        mock_logger.info.assert_any_call(
            LOG_EVENTS.FUEL_ALREADY_ADDED,
            "User already fueled this spark (idempotent)",
            context={"spark_id": "spark_123", "user_hash": "user_hash_B"},
        )

    @pytest.mark.asyncio
    async def test_execute_whenSelfFuel_returnsSuccessWithoutIncrement(
        self,
        interactor: AddFuelInteractor,
        mock_spark_repo: AsyncMock,
        mock_logger: Mock,
        active_spark: Spark,
    ) -> None:
        """Self fuel should return success but not increment count."""
        # Arrange
        input_data = AddFuelInput(
            spark_id="spark_123",
            user_hash="author_hash",  # Same as spark author
        )
        mock_spark_repo.find_by_id.return_value = active_spark

        # Act
        output = await interactor.execute(input_data)

        # Assert
        assert output.success is True
        mock_spark_repo.try_add_fuel.assert_not_awaited()  # Should not try to add
        mock_logger.info.assert_any_call(
            LOG_EVENTS.FUEL_SELF_SPARK,
            "User attempted to fuel their own spark (skipped)",
            context={"spark_id": "spark_123", "user_hash": "author_hash"},
        )

    @pytest.mark.asyncio
    async def test_execute_whenSparkNotFound_raisesAppError(
        self,
        interactor: AddFuelInteractor,
        mock_spark_repo: AsyncMock,
        mock_logger: Mock,
    ) -> None:
        """Non-existent spark should raise AppError with code 1005."""
        # Arrange
        input_data = AddFuelInput(spark_id="nonexistent", user_hash="user_hash_B")
        mock_spark_repo.find_by_id.return_value = None

        # Act & Assert
        with pytest.raises(AppError) as exc_info:
            await interactor.execute(input_data)

        assert exc_info.value.internal_code == 1005
        mock_logger.warning.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_whenSparkDecayed_raisesAppError(
        self,
        interactor: AddFuelInteractor,
        mock_spark_repo: AsyncMock,
        mock_logger: Mock,
        decayed_spark: Spark,
    ) -> None:
        """Decayed spark should raise AppError with code 1001."""
        # Arrange
        input_data = AddFuelInput(spark_id="spark_456", user_hash="user_hash_B")
        mock_spark_repo.find_by_id.return_value = decayed_spark

        # Act & Assert
        with pytest.raises(AppError) as exc_info:
            await interactor.execute(input_data)

        assert exc_info.value.internal_code == 1001
        mock_logger.warning.assert_called_once()

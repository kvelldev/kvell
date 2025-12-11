"""Unit tests for StreamTimelineInteractor."""

from datetime import UTC, datetime
from typing import Any
from unittest.mock import AsyncMock, Mock

import pytest

from app.domain.model.spark import Spark
from app.usecase.dto.spark_dto import SparkOutput
from app.usecase.stream_timeline.interactor import StreamTimelineInteractor

pytestmark = pytest.mark.asyncio


class MockAsyncIterator:
    """Mock async iterator for testing."""

    def __init__(self, items: list[Any]) -> None:
        """Initialize with items to yield."""
        self.items = items
        self.index = 0

    def __aiter__(self) -> "MockAsyncIterator":
        """Return self as async iterator."""
        return self

    async def __anext__(self) -> Any:
        """Return next item or raise StopAsyncIteration."""
        if self.index >= len(self.items):
            raise StopAsyncIteration
        item = self.items[self.index]
        self.index += 1
        return item


class TestStreamTimelineInteractor:
    """Test suite for StreamTimelineInteractor."""

    @pytest.fixture
    def mock_spark_repository(self) -> AsyncMock:
        """Create mock spark repository."""
        return AsyncMock()

    @pytest.fixture
    def mock_pubsub_gateway(self) -> AsyncMock:
        """Create mock pub/sub gateway."""
        return AsyncMock()

    @pytest.fixture
    def mock_logger(self) -> Mock:
        """Create mock logger."""
        return Mock()

    @pytest.fixture
    def interactor(
        self,
        mock_spark_repository: AsyncMock,
        mock_pubsub_gateway: AsyncMock,
        mock_logger: Mock,
    ) -> StreamTimelineInteractor:
        """Create StreamTimelineInteractor instance."""
        return StreamTimelineInteractor(
            spark_repository=mock_spark_repository,
            pubsub_gateway=mock_pubsub_gateway,
            logger=mock_logger,
            active_spark_seconds=600,
            pubsub_channel="sparks:events",
        )

    async def test_execute_whenNoActiveSparks_yieldsOnlyStreamEvents(
        self,
        interactor: StreamTimelineInteractor,
        mock_spark_repository: AsyncMock,
        mock_pubsub_gateway: AsyncMock,
    ) -> None:
        """Test execute when no active sparks returns only stream events."""
        # Arrange
        # Repository returns empty async iterator
        mock_spark_repository.find_active_sparks = Mock(
            return_value=MockAsyncIterator([])
        )

        # Mock pub/sub to yield 2 sparks then stop
        items = [
            SparkOutput(
                id="stream-1",
                content="Stream spark 1",
                created_at=datetime(2025, 1, 1, 0, 0, 0, tzinfo=UTC),
                decay_at=datetime(2025, 1, 1, 0, 10, 0, tzinfo=UTC),
            ),
            SparkOutput(
                id="stream-2",
                content="Stream spark 2",
                created_at=datetime(2025, 1, 1, 0, 1, 0, tzinfo=UTC),
                decay_at=datetime(2025, 1, 1, 0, 11, 0, tzinfo=UTC),
            ),
        ]
        mock_pubsub_gateway.subscribe = Mock(return_value=MockAsyncIterator(items))

        # Act
        results: list[SparkOutput] = []
        count = 0
        async for spark in interactor.execute():
            results.append(spark)
            count += 1
            if count >= 2:  # Only collect 2 stream events
                break

        # Assert
        assert len(results) == 2
        assert results[0].id == "stream-1"
        assert results[1].id == "stream-2"
        mock_spark_repository.find_active_sparks.assert_called_once_with(seconds=600)
        mock_pubsub_gateway.subscribe.assert_called_once_with("sparks:events")

    async def test_execute_whenActiveSparksExist_yieldsSnapshotThenStream(
        self,
        interactor: StreamTimelineInteractor,
        mock_spark_repository: AsyncMock,
        mock_pubsub_gateway: AsyncMock,
    ) -> None:
        """Test execute yields snapshot sparks first, then stream events."""
        # Arrange
        snapshot_sparks = [
            Spark.create(
                spark_id="snap-1",
                content="Snapshot spark 1",
                user_hash="user-1",
                decay_after_seconds=600,
                vanish_after_days=30,
            ),
            Spark.create(
                spark_id="snap-2",
                content="Snapshot spark 2",
                user_hash="user-2",
                decay_after_seconds=600,
                vanish_after_days=30,
            ),
        ]
        # Repository returns async iterator of sparks
        mock_spark_repository.find_active_sparks = Mock(
            return_value=MockAsyncIterator(snapshot_sparks)
        )

        # Mock pub/sub to yield 1 spark then stop
        items = [
            SparkOutput(
                id="stream-1",
                content="Stream spark 1",
                created_at=datetime(2025, 1, 1, 0, 0, 0, tzinfo=UTC),
                decay_at=datetime(2025, 1, 1, 0, 10, 0, tzinfo=UTC),
            ),
        ]
        mock_pubsub_gateway.subscribe = Mock(return_value=MockAsyncIterator(items))

        # Act
        results: list[SparkOutput] = []
        count = 0
        async for spark in interactor.execute():
            results.append(spark)
            count += 1
            if count >= 3:  # Collect 2 snapshot + 1 stream
                break

        # Assert
        assert len(results) == 3
        # First 2 are snapshot (oldest first)
        assert results[0].id == "snap-1"
        assert results[0].content == "Snapshot spark 1"
        assert results[1].id == "snap-2"
        assert results[1].content == "Snapshot spark 2"
        # Last one is stream
        assert results[2].id == "stream-1"
        assert results[2].content == "Stream spark 1"

    async def test_execute_whenSnapshotReturnsMultipleSparks_yieldsInAscendingOrder(
        self,
        interactor: StreamTimelineInteractor,
        mock_spark_repository: AsyncMock,
        mock_pubsub_gateway: AsyncMock,
    ) -> None:
        """Test that snapshot sparks are yielded in ascending order (oldest first)."""
        # Arrange
        snapshot_sparks = [
            Spark.create(
                spark_id=f"snap-{i}",
                content=f"Spark {i}",
                user_hash=f"user-{i}",
                decay_after_seconds=600,
                vanish_after_days=30,
            )
            for i in range(5)
        ]
        # Repository returns async iterator of sparks
        mock_spark_repository.find_active_sparks = Mock(
            return_value=MockAsyncIterator(snapshot_sparks)
        )

        # Mock pub/sub (won't actually iterate)
        mock_pubsub_gateway.subscribe = Mock(return_value=MockAsyncIterator([]))

        # Act
        results: list[SparkOutput] = []
        count = 0
        async for spark in interactor.execute():
            results.append(spark)
            count += 1
            if count >= 5:  # Only collect snapshot
                break

        # Assert
        assert len(results) == 5
        for i in range(5):
            assert results[i].id == f"snap-{i}"
            assert results[i].content == f"Spark {i}"

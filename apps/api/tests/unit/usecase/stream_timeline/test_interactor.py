"""Unit tests for StreamTimelineInteractor."""


from typing import Any
from unittest.mock import AsyncMock, Mock

import pytest

from app.domain.model.spark import Spark

from app.usecase.dto.timeline_event import SparkPostedEvent, TimelineEvent
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
            {
                "type": "spark_posted",
                "data": {
                    "id": "stream-1",
                    "content": "Stream spark 1",
                    "user_hash": "abc12345",
                    "created_at": "2025-01-01T00:00:00Z",
                    "decay_at": "2025-01-01T00:10:00Z",
                    "field_id": "test_field",
                }
            },
            {
                "type": "spark_posted",
                "data": {
                    "id": "stream-2",
                    "content": "Stream spark 2",
                    "user_hash": "def67890",
                    "created_at": "2025-01-01T00:01:00Z",
                    "decay_at": "2025-01-01T00:11:00Z",
                    "field_id": "test_field",
                }
            },
        ]
        mock_pubsub_gateway.subscribe_raw = Mock(return_value=MockAsyncIterator(items))

        # Act
        results: list[TimelineEvent] = []
        count = 0
        async for event in interactor.execute(field_id="test_field"):
            results.append(event)
            count += 1
            if count >= 2:  # Only collect 2 stream events
                break

        # Assert
        assert len(results) == 2
        assert isinstance(results[0], SparkPostedEvent)
        assert results[0].data.id == "stream-1"
        assert isinstance(results[1], SparkPostedEvent)
        assert results[1].data.id == "stream-2"

        mock_spark_repository.find_active_sparks.assert_called_once_with(
            field_id="test_field", seconds=600
        )
        mock_pubsub_gateway.subscribe_raw.assert_called_once_with(["timeline:test_field"])

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
                field_id="test_field",
            ),
            Spark.create(
                spark_id="snap-2",
                content="Snapshot spark 2",
                user_hash="user-2",
                decay_after_seconds=600,
                vanish_after_days=30,
                field_id="test_field",
            ),
        ]
        # Repository returns async iterator of sparks
        mock_spark_repository.find_active_sparks = Mock(
            return_value=MockAsyncIterator(snapshot_sparks)
        )

        # Mock pub/sub to yield 1 spark then stop
        items = [
            {
                "type": "spark_posted",
                "data": {
                    "id": "stream-1",
                    "content": "Stream spark 1",
                    "user_hash": "stream01",
                    "created_at": "2025-01-01T00:00:00Z",
                    "decay_at": "2025-01-01T00:10:00Z",
                    "field_id": "test_field",
                }
            },
        ]
        mock_pubsub_gateway.subscribe_raw = Mock(return_value=MockAsyncIterator(items))

        # Act
        results: list[TimelineEvent] = []
        count = 0
        async for event in interactor.execute(field_id="test_field"):
            results.append(event)
            count += 1
            if count >= 3:  # Collect 2 snapshot + 1 stream
                break

        # Assert
        assert len(results) == 3
        # First 2 are snapshot (oldest first)
        assert isinstance(results[0], SparkPostedEvent)
        assert results[0].data.id == "snap-1"

        assert isinstance(results[1], SparkPostedEvent)
        assert results[1].data.id == "snap-2"

        # Last one is stream
        assert isinstance(results[2], SparkPostedEvent)
        assert results[2].data.id == "stream-1"

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
                field_id="test_field",
            )
            for i in range(5)
        ]
        # Repository returns async iterator of sparks
        mock_spark_repository.find_active_sparks = Mock(
            return_value=MockAsyncIterator(snapshot_sparks)
        )

        # Mock pub/sub (won't actually iterate)
        mock_pubsub_gateway.subscribe_raw = Mock(return_value=MockAsyncIterator([]))

        # Act
        results: list[TimelineEvent] = []
        count = 0
        async for event in interactor.execute(field_id="test_field"):
            results.append(event)
            count += 1
            if count >= 5:  # Only collect snapshot
                break

        # Assert
        assert len(results) == 5
        for i in range(5):
            event = results[i]
            assert isinstance(event, SparkPostedEvent)
            assert event.data.id == f"snap-{i}"

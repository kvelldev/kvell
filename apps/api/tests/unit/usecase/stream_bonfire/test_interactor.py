"""Unit tests for StreamBonfireInteractor."""

from datetime import UTC, datetime
from typing import Any
from unittest.mock import AsyncMock, Mock

import pytest

from app.domain.model.bonfire import Bonfire
from app.domain.model.spark import Spark
from app.usecase.dto.spark_dto import SparkOutput
from app.usecase.stream_bonfire.interface import BonfireEvent, BonfireEventType
from app.usecase.stream_bonfire.interactor import StreamBonfireInteractor

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


class TestStreamBonfireInteractor:
    """Test suite for StreamBonfireInteractor."""

    @pytest.fixture
    def mock_spark_repository(self) -> AsyncMock:
        """Create mock spark repository."""
        return AsyncMock()

    @pytest.fixture
    def mock_bonfire_repository(self) -> AsyncMock:
        """Create mock bonfire repository."""
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
        mock_bonfire_repository: AsyncMock,
        mock_pubsub_gateway: AsyncMock,
        mock_logger: Mock,
    ) -> StreamBonfireInteractor:
        """Create StreamBonfireInteractor instance."""
        return StreamBonfireInteractor(
            spark_repository=mock_spark_repository,
            bonfire_repository=mock_bonfire_repository,
            pubsub_gateway=mock_pubsub_gateway,
            logger=mock_logger,
        )

    @pytest.fixture
    def mock_bonfire(self) -> Bonfire:
        """Create mock bonfire for testing."""
        return Bonfire.create(
            spark_id="bonfire-001",
            content="Parent bonfire content",
            unique_user_count=10,
            heat_score=100,
            initial_decay_hours=3,
            field_id="sakurazaka46",
        )

    async def test_execute_whenBonfireNotFound_raisesAppError(
        self,
        interactor: StreamBonfireInteractor,
        mock_bonfire_repository: AsyncMock,
    ) -> None:
        """Test execute raises AppError when bonfire not found."""
        # Arrange
        mock_bonfire_repository.find_by_id.return_value = None

        # Act & Assert
        from app.domain.exception import AppError

        with pytest.raises(AppError) as exc_info:
            async for _ in interactor.execute("nonexistent-bonfire"):
                pass

        assert exc_info.value.internal_code == 1005

    async def test_execute_whenNoReplies_yieldsOnlyStreamEvents(
        self,
        interactor: StreamBonfireInteractor,
        mock_spark_repository: AsyncMock,
        mock_bonfire_repository: AsyncMock,
        mock_pubsub_gateway: AsyncMock,
        mock_bonfire: Bonfire,
    ) -> None:
        """Test execute when no replies returns only stream events."""
        # Arrange
        mock_bonfire_repository.find_by_id.return_value = mock_bonfire
        mock_spark_repository.find_replies_by_bonfire_id = Mock(
            return_value=MockAsyncIterator([])
        )

        # Mock pub/sub to yield 1 spark
        stream_items = [
            {
                "type": "spark",
                "id": "stream-reply-1",
                "content": "Stream reply 1",
                "parent_bonfire_id": "bonfire-001",
                "created_at": datetime(2025, 1, 1, 0, 0, 0, tzinfo=UTC).isoformat(),
                "decay_at": datetime(2025, 1, 1, 3, 0, 0, tzinfo=UTC).isoformat(),
                "field_id": "sakurazaka46",
                "user_hash": "mockuserhash123",
            },
        ]
        mock_pubsub_gateway.subscribe_raw = Mock(
            return_value=MockAsyncIterator(stream_items)
        )

        # Act
        results: list[SparkOutput | BonfireEvent] = []
        count = 0
        async for msg in interactor.execute("bonfire-001"):
            results.append(msg)
            count += 1
            if count >= 1:
                break

        # Assert
        assert len(results) == 1
        assert isinstance(results[0], SparkOutput)
        assert results[0].id == "stream-reply-1"
        mock_spark_repository.find_replies_by_bonfire_id.assert_called_once_with(
            bonfire_id="bonfire-001"
        )

    async def test_execute_whenRepliesExist_yieldsSnapshotThenStream(
        self,
        interactor: StreamBonfireInteractor,
        mock_spark_repository: AsyncMock,
        mock_bonfire_repository: AsyncMock,
        mock_pubsub_gateway: AsyncMock,
        mock_bonfire: Bonfire,
    ) -> None:
        """Test execute yields snapshot replies first, then stream events."""
        # Arrange
        mock_bonfire_repository.find_by_id.return_value = mock_bonfire

        snapshot_sparks = [
            Spark.create(
                spark_id="snap-reply-1",
                content="Snapshot reply 1",
                user_hash="user-1",
                decay_after_seconds=600,
                vanish_after_days=30,
                parent_bonfire_id="bonfire-001",
                field_id="sakurazaka46",
            ),
            Spark.create(
                spark_id="snap-reply-2",
                content="Snapshot reply 2",
                user_hash="user-2",
                decay_after_seconds=600,
                vanish_after_days=30,
                parent_bonfire_id="bonfire-001",
                field_id="sakurazaka46",
            ),
        ]
        mock_spark_repository.find_replies_by_bonfire_id = Mock(
            return_value=MockAsyncIterator(snapshot_sparks)
        )

        # Mock pub/sub to yield 1 spark
        stream_items = [
            {
                "type": "spark",
                "id": "stream-reply-1",
                "content": "Stream reply 1",
                "parent_bonfire_id": "bonfire-001",
                "created_at": datetime(2025, 1, 1, 0, 0, 0, tzinfo=UTC).isoformat(),
                "decay_at": datetime(2025, 1, 1, 3, 0, 0, tzinfo=UTC).isoformat(),
                "field_id": "sakurazaka46",
                "user_hash": "mockuserhash123",
            },
        ]
        mock_pubsub_gateway.subscribe_raw = Mock(
            return_value=MockAsyncIterator(stream_items)
        )

        # Act
        results: list[SparkOutput | BonfireEvent] = []
        count = 0
        async for msg in interactor.execute("bonfire-001"):
            results.append(msg)
            count += 1
            if count >= 3:
                break

        # Assert
        assert len(results) == 3
        # First 2 are snapshot (SparkOutput)
        assert isinstance(results[0], SparkOutput)
        assert results[0].id == "snap-reply-1"
        assert isinstance(results[1], SparkOutput)
        assert results[1].id == "snap-reply-2"
        # Last is stream (SparkOutput)
        assert isinstance(results[2], SparkOutput)
        assert results[2].id == "stream-reply-1"

    async def test_execute_whenBonfireDecayEvent_yieldsBonfireEvent(
        self,
        interactor: StreamBonfireInteractor,
        mock_spark_repository: AsyncMock,
        mock_bonfire_repository: AsyncMock,
        mock_pubsub_gateway: AsyncMock,
        mock_bonfire: Bonfire,
    ) -> None:
        """Test execute yields BonfireEvent when decay event is received."""
        # Arrange
        mock_bonfire_repository.find_by_id.return_value = mock_bonfire
        mock_spark_repository.find_replies_by_bonfire_id = Mock(
            return_value=MockAsyncIterator([])
        )

        # Mock pub/sub to yield a decay event
        stream_items = [
            {
                "type": "bonfire_decayed",
                "bonfire_id": "bonfire-001",
                "message": "Bonfire has decayed",
            },
        ]
        mock_pubsub_gateway.subscribe_raw = Mock(
            return_value=MockAsyncIterator(stream_items)
        )

        # Act
        results: list[SparkOutput | BonfireEvent] = []
        count = 0
        async for msg in interactor.execute("bonfire-001"):
            results.append(msg)
            count += 1
            if count >= 1:
                break

        # Assert
        assert len(results) == 1
        assert isinstance(results[0], BonfireEvent)
        assert results[0].event_type == BonfireEventType.DECAYED
        assert results[0].bonfire_id == "bonfire-001"

    async def test_execute_subscribesToCorrectChannel(
        self,
        interactor: StreamBonfireInteractor,
        mock_spark_repository: AsyncMock,
        mock_bonfire_repository: AsyncMock,
        mock_pubsub_gateway: AsyncMock,
        mock_bonfire: Bonfire,
    ) -> None:
        """Test execute subscribes to bonfire-specific channel."""
        # Arrange
        mock_bonfire_repository.find_by_id.return_value = mock_bonfire
        mock_spark_repository.find_replies_by_bonfire_id = Mock(
            return_value=MockAsyncIterator([])
        )
        # Provide at least one item so iteration can proceed
        stream_items = [
            {
                "type": "spark",
                "id": "stream-1",
                "content": "Stream content",
                "parent_bonfire_id": "bonfire-001",
                "created_at": datetime(2025, 1, 1, 0, 0, 0, tzinfo=UTC).isoformat(),
                "decay_at": datetime(2025, 1, 1, 3, 0, 0, tzinfo=UTC).isoformat(),
                "field_id": "sakurazaka46",
                "user_hash": "mockuserhash123",
            },
        ]
        mock_pubsub_gateway.subscribe_raw = Mock(
            return_value=MockAsyncIterator(stream_items)
        )

        # Act
        async for _ in interactor.execute("bonfire-001"):
            break  # Get first item then break

        # Assert
        mock_pubsub_gateway.subscribe_raw.assert_called_once_with("bonfire:bonfire-001")

    async def test_execute_whenBonfireExtendedEvent_yieldsBonfireEvent(
        self,
        interactor: StreamBonfireInteractor,
        mock_spark_repository: AsyncMock,
        mock_bonfire_repository: AsyncMock,
        mock_pubsub_gateway: AsyncMock,
        mock_bonfire: Bonfire,
    ) -> None:
        """Test execute yields BonfireEvent when extended event is received."""
        # Arrange
        mock_bonfire_repository.find_by_id.return_value = mock_bonfire
        mock_spark_repository.find_replies_by_bonfire_id = Mock(
            return_value=MockAsyncIterator([])
        )

        # Mock pub/sub to yield an extended event
        stream_items = [
            {
                "type": "bonfire_extended",
                "bonfire_id": "bonfire-001",
                "message": "Bonfire has been extended",
            },
        ]
        mock_pubsub_gateway.subscribe_raw = Mock(
            return_value=MockAsyncIterator(stream_items)
        )

        # Act
        results: list[SparkOutput | BonfireEvent] = []
        count = 0
        async for msg in interactor.execute("bonfire-001"):
            results.append(msg)
            count += 1
            if count >= 1:
                break

        # Assert
        assert len(results) == 1
        assert isinstance(results[0], BonfireEvent)
        assert results[0].event_type == BonfireEventType.EXTENDED
        assert results[0].bonfire_id == "bonfire-001"

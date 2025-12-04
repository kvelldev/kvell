"""Unit tests for HealthCheckInteractor."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest

from app.domain.model.health_message import HealthMessage
from app.domain.repository.health_repository import IHealthRepository
from app.usecase.dto.health_dto import HealthOutput, SaveHealthInput
from app.usecase.health_check.interactor import HealthCheckInteractor
from app.usecase.ports.logger import ILogger


class TestHealthCheckInteractor:
    """Test cases for HealthCheckInteractor."""

    @pytest.fixture
    def mock_repository(self) -> AsyncMock:
        """Create a mock health repository."""
        return AsyncMock(spec=IHealthRepository)

    @pytest.fixture
    def mock_logger(self) -> AsyncMock:
        """Create a mock logger."""
        return AsyncMock(spec=ILogger)

    @pytest.fixture
    def interactor(
        self, mock_repository: AsyncMock, mock_logger: AsyncMock
    ) -> HealthCheckInteractor:
        """Create a HealthCheckInteractor with mocked dependencies."""
        return HealthCheckInteractor(
            health_repository=mock_repository, logger=mock_logger
        )

    @pytest.mark.asyncio
    async def test_saveMessage_whenCalled_createsEntityAndSaves(
        self,
        interactor: HealthCheckInteractor,
        mock_repository: AsyncMock,
    ) -> None:
        """
        Action: saveMessage
        Condition: whenCalled (valid input)
        Result: createsEntityAndSaves (creates HealthMessage and calls repository)
        """
        # Arrange
        input_data = SaveHealthInput(message="Test health message")
        test_timestamp = datetime(2025, 1, 1, 12, 0, 0, tzinfo=UTC)

        saved_message = HealthMessage(
            id="generated-id-123",
            message="Test health message",
            created_at=test_timestamp,
        )
        mock_repository.save.return_value = saved_message

        # Act
        result = await interactor.save_message(input_data)

        # Assert
        mock_repository.save.assert_called_once()
        call_args = mock_repository.save.call_args[0][0]
        assert isinstance(call_args, HealthMessage)
        assert call_args.message == "Test health message"

        assert isinstance(result, HealthOutput)
        assert result.id == "generated-id-123"
        assert result.message == "Test health message"
        assert result.created_at == test_timestamp.isoformat()

    @pytest.mark.asyncio
    async def test_saveMessage_whenCalledTwice_generatesUniqueIds(
        self,
        interactor: HealthCheckInteractor,
        mock_repository: AsyncMock,
    ) -> None:
        """
        Action: saveMessage
        Condition: whenCalledTwice (same input, multiple calls)
        Result: generatesUniqueIds (each call generates different UUID)
        """
        # Arrange
        input_data = SaveHealthInput(message="Test message")

        async def mock_save(message: HealthMessage) -> HealthMessage:
            return message

        mock_repository.save.side_effect = mock_save

        # Act
        result1 = await interactor.save_message(input_data)
        result2 = await interactor.save_message(input_data)

        # Assert
        assert result1.id != result2.id
        assert len(result1.id) > 0
        assert len(result2.id) > 0

    @pytest.mark.asyncio
    async def test_saveMessage_whenMessageIsEmpty_savesSuccessfully(
        self,
        interactor: HealthCheckInteractor,
        mock_repository: AsyncMock,
    ) -> None:
        """
        Action: saveMessage
        Condition: whenMessageIsEmpty (empty string)
        Result: savesSuccessfully (processes empty message)
        """
        # Arrange
        input_data = SaveHealthInput(message="")
        test_timestamp = datetime(2025, 1, 1, 12, 0, 0, tzinfo=UTC)

        saved_message = HealthMessage(
            id="test-id",
            message="",
            created_at=test_timestamp,
        )
        mock_repository.save.return_value = saved_message

        # Act
        result = await interactor.save_message(input_data)

        # Assert
        assert result.message == ""
        mock_repository.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_saveMessage_whenMessageIsLong_savesSuccessfully(
        self,
        interactor: HealthCheckInteractor,
        mock_repository: AsyncMock,
    ) -> None:
        """
        Action: saveMessage
        Condition: whenMessageIsLong (10000 characters)
        Result: savesSuccessfully (handles long message)
        """
        # Arrange
        long_message = "a" * 10000
        input_data = SaveHealthInput(message=long_message)
        test_timestamp = datetime(2025, 1, 1, 12, 0, 0, tzinfo=UTC)

        saved_message = HealthMessage(
            id="test-id",
            message=long_message,
            created_at=test_timestamp,
        )
        mock_repository.save.return_value = saved_message

        # Act
        result = await interactor.save_message(input_data)

        # Assert
        assert result.message == long_message
        assert len(result.message) == 10000

    @pytest.mark.asyncio
    async def test_saveMessage_whenMessageHasSpecialChars_savesSuccessfully(
        self,
        interactor: HealthCheckInteractor,
        mock_repository: AsyncMock,
    ) -> None:
        """
        Action: saveMessage
        Condition: whenMessageHasSpecialChars (Japanese, emoji, HTML)
        Result: savesSuccessfully (handles special characters)
        """
        # Arrange
        special_message = "Test 日本語 🔥 <script>alert('xss')</script>"
        input_data = SaveHealthInput(message=special_message)
        test_timestamp = datetime(2025, 1, 1, 12, 0, 0, tzinfo=UTC)

        saved_message = HealthMessage(
            id="test-id",
            message=special_message,
            created_at=test_timestamp,
        )
        mock_repository.save.return_value = saved_message

        # Act
        result = await interactor.save_message(input_data)

        # Assert
        assert result.message == special_message

    @pytest.mark.asyncio
    async def test_saveMessage_whenCalled_returnsIsoTimestamp(
        self,
        interactor: HealthCheckInteractor,
        mock_repository: AsyncMock,
    ) -> None:
        """
        Action: saveMessage
        Condition: whenCalled (any valid input)
        Result: returnsIsoTimestamp (timestamp in ISO 8601 format)
        """
        # Arrange
        input_data = SaveHealthInput(message="Test message")
        test_timestamp = datetime(2025, 11, 29, 15, 30, 45, 123456, tzinfo=UTC)

        saved_message = HealthMessage(
            id="test-id",
            message="Test message",
            created_at=test_timestamp,
        )
        mock_repository.save.return_value = saved_message

        # Act
        result = await interactor.save_message(input_data)

        # Assert
        assert result.created_at == "2025-11-29T15:30:45.123456+00:00"

    @pytest.mark.asyncio
    async def test_getLatest_whenMessageExists_returnsOutput(
        self,
        interactor: HealthCheckInteractor,
        mock_repository: AsyncMock,
    ) -> None:
        """
        Action: getLatest
        Condition: whenMessageExists (repository returns a message)
        Result: returnsOutput (HealthOutput with message data)
        """
        # Arrange
        test_timestamp = datetime(2025, 1, 1, 12, 0, 0, tzinfo=UTC)
        latest_message = HealthMessage(
            id="latest-id",
            message="Latest message",
            created_at=test_timestamp,
        )
        mock_repository.find_latest.return_value = latest_message

        # Act
        result = await interactor.get_latest_message()

        # Assert
        mock_repository.find_latest.assert_called_once()
        assert result is not None
        assert isinstance(result, HealthOutput)
        assert result.id == "latest-id"
        assert result.message == "Latest message"
        assert result.created_at == test_timestamp.isoformat()

    @pytest.mark.asyncio
    async def test_getLatest_whenMessageNotExists_returnsNone(
        self,
        interactor: HealthCheckInteractor,
        mock_repository: AsyncMock,
    ) -> None:
        """
        Action: getLatest
        Condition: whenMessageNotExists (repository returns None)
        Result: returnsNone (None is returned)
        """
        # Arrange
        mock_repository.find_latest.return_value = None

        # Act
        result = await interactor.get_latest_message()

        # Assert
        mock_repository.find_latest.assert_called_once()
        assert result is None

    @pytest.mark.asyncio
    async def test_getLatest_whenCalled_callsRepositoryCorrectly(
        self,
        interactor: HealthCheckInteractor,
        mock_repository: AsyncMock,
    ) -> None:
        """
        Action: getLatest
        Condition: whenCalled
        Result: callsRepositoryCorrectly (calls find_latest without parameters)
        """
        # Arrange
        mock_repository.find_latest.return_value = None

        # Act
        await interactor.get_latest_message()

        # Assert
        mock_repository.find_latest.assert_called_once_with()

    @pytest.mark.asyncio
    async def test_saveMessage_whenRepositoryThrows_propagatesException(
        self,
        interactor: HealthCheckInteractor,
        mock_repository: AsyncMock,
    ) -> None:
        """
        Action: saveMessage
        Condition: whenRepositoryThrows (repository raises RuntimeError)
        Result: propagatesException (exception is propagated)
        """
        # Arrange
        input_data = SaveHealthInput(message="Test message")
        mock_repository.save.side_effect = RuntimeError("Database error")

        # Act & Assert
        with pytest.raises(RuntimeError, match="Database error"):
            await interactor.save_message(input_data)

    @pytest.mark.asyncio
    async def test_getLatest_whenRepositoryThrows_propagatesException(
        self,
        interactor: HealthCheckInteractor,
        mock_repository: AsyncMock,
    ) -> None:
        """
        Action: getLatest
        Condition: whenRepositoryThrows (repository raises RuntimeError)
        Result: propagatesException (exception is propagated)
        """
        # Arrange
        mock_repository.find_latest.side_effect = RuntimeError("Database error")

        # Act & Assert
        with pytest.raises(RuntimeError, match="Database error"):
            await interactor.get_latest_message()

    @pytest.mark.asyncio
    async def test_saveMessage_whenMultipleCalls_operationsAreIndependent(
        self,
        interactor: HealthCheckInteractor,
        mock_repository: AsyncMock,
    ) -> None:
        """
        Action: saveMessage
        Condition: whenMultipleCalls (two save operations)
        Result: operationsAreIndependent (each operation is isolated)
        """
        # Arrange
        input1 = SaveHealthInput(message="Message 1")
        input2 = SaveHealthInput(message="Message 2")

        async def mock_save(message: HealthMessage) -> HealthMessage:
            return message

        mock_repository.save.side_effect = mock_save

        # Act
        result1 = await interactor.save_message(input1)
        result2 = await interactor.save_message(input2)

        # Assert
        assert result1.message == "Message 1"
        assert result2.message == "Message 2"
        assert result1.id != result2.id
        assert mock_repository.save.call_count == 2

"""Unit tests for HealthMessage entity."""

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from app.domain.model.health_message import HealthMessage


class TestHealthMessage:
    """Test cases for HealthMessage entity."""

    def test_createHealthMessage_whenDataIsValid_createsSuccessfully(self) -> None:
        """
        Action: createHealthMessage
        Condition: whenDataIsValid (all required fields provided)
        Result: createsSuccessfully (instance created with correct values)
        """
        # Arrange
        test_id = "test-id-123"
        test_message = "System is healthy"
        test_timestamp = datetime(2025, 1, 1, 12, 0, 0, tzinfo=UTC)

        # Act
        health_message = HealthMessage(
            id=test_id,
            message=test_message,
            created_at=test_timestamp,
        )

        # Assert
        assert health_message.id == test_id
        assert health_message.message == test_message
        assert health_message.created_at == test_timestamp

    def test_createHealthMessage_whenTimestampOmitted_generatesDefault(self) -> None:
        """
        Action: createHealthMessage
        Condition: whenTimestampOmitted (created_at not provided)
        Result: generatesDefault (auto-generates UTC timestamp)
        """
        # Arrange
        test_id = "test-id-456"
        test_message = "Auto timestamp test"
        before_creation = datetime.now(UTC)

        # Act
        health_message = HealthMessage(
            id=test_id,
            message=test_message,
        )

        # Assert
        after_creation = datetime.now(UTC)
        assert health_message.id == test_id
        assert health_message.message == test_message
        assert before_creation <= health_message.created_at <= after_creation
        assert health_message.created_at.tzinfo == UTC

    def test_healthMessage_whenFieldModified_raisesError(self) -> None:
        """
        Action: healthMessage (immutability check)
        Condition: whenFieldModified (attempt to change field after creation)
        Result: raisesError (ValidationError due to frozen=True)
        """
        # Arrange
        health_message = HealthMessage(
            id="test-id",
            message="Test message",
        )

        # Act & Assert
        with pytest.raises(ValidationError):
            health_message.message = "Changed message"

    def test_createHealthMessage_whenRequiredFieldsMissing_raisesError(self) -> None:
        """
        Action: createHealthMessage
        Condition: whenRequiredFieldsMissing (id or message missing)
        Result: raisesError (ValidationError)
        """
        # Act & Assert - missing id
        with pytest.raises(ValidationError) as exc_info:
            HealthMessage(message="Test message")
        assert "id" in str(exc_info.value)

        # Act & Assert - missing message
        with pytest.raises(ValidationError) as exc_info:
            HealthMessage(id="test-id")
        assert "message" in str(exc_info.value)

    def test_healthMessage_whenCreated_hasCorrectTypes(self) -> None:
        """
        Action: healthMessage
        Condition: whenCreated (instance created)
        Result: hasCorrectTypes (id=str, message=str, created_at=datetime)
        """
        # Arrange
        test_id = "test-id"
        test_message = "Test message"

        # Act
        health_message = HealthMessage(
            id=test_id,
            message=test_message,
        )

        # Assert
        assert isinstance(health_message.id, str)
        assert isinstance(health_message.message, str)
        assert isinstance(health_message.created_at, datetime)

    def test_createHealthMessage_whenMessageIsEmpty_createsSuccessfully(self) -> None:
        """
        Action: createHealthMessage
        Condition: whenMessageIsEmpty (empty string)
        Result: createsSuccessfully (accepts empty message)
        """
        # Arrange
        test_id = "test-id"
        empty_message = ""

        # Act
        health_message = HealthMessage(
            id=test_id,
            message=empty_message,
        )

        # Assert
        assert health_message.message == ""

    def test_createHealthMessage_whenMessageIsLong_createsSuccessfully(self) -> None:
        """
        Action: createHealthMessage
        Condition: whenMessageIsLong (10000 characters)
        Result: createsSuccessfully (handles long message)
        """
        # Arrange
        test_id = "test-id"
        long_message = "a" * 10000

        # Act
        health_message = HealthMessage(
            id=test_id,
            message=long_message,
        )

        # Assert
        assert health_message.message == long_message
        assert len(health_message.message) == 10000

    def test_createHealthMessage_whenMessageHasSpecialChars_createsSuccessfully(self) -> None:
        """
        Action: createHealthMessage
        Condition: whenMessageHasSpecialChars (Japanese, emoji, HTML)
        Result: createsSuccessfully (handles special characters)
        """
        # Arrange
        test_id = "test-id"
        special_message = "Test 日本語 🔥 <script>alert('xss')</script>"

        # Act
        health_message = HealthMessage(
            id=test_id,
            message=special_message,
        )

        # Assert
        assert health_message.message == special_message

    def test_healthMessage_whenSameData_isEqual(self) -> None:
        """
        Action: healthMessage (equality check)
        Condition: whenSameData (two instances with identical fields)
        Result: isEqual (instances are equal)
        """
        # Arrange
        test_timestamp = datetime(2025, 1, 1, 12, 0, 0, tzinfo=UTC)
        message1 = HealthMessage(
            id="test-id",
            message="Test message",
            created_at=test_timestamp,
        )
        message2 = HealthMessage(
            id="test-id",
            message="Test message",
            created_at=test_timestamp,
        )

        # Assert
        assert message1 == message2

    def test_healthMessage_whenDifferentData_isNotEqual(self) -> None:
        """
        Action: healthMessage (inequality check)
        Condition: whenDifferentData (different id values)
        Result: isNotEqual (instances are not equal)
        """
        # Arrange
        test_timestamp = datetime(2025, 1, 1, 12, 0, 0, tzinfo=UTC)
        message1 = HealthMessage(
            id="test-id-1",
            message="Test message",
            created_at=test_timestamp,
        )
        message2 = HealthMessage(
            id="test-id-2",
            message="Test message",
            created_at=test_timestamp,
        )

        # Assert
        assert message1 != message2

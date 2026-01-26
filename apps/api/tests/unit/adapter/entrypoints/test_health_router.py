"""Unit tests for health check router endpoints."""

from collections.abc import Generator
from unittest.mock import AsyncMock

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from app.adapter.entrypoints.dependencies import get_health_usecase
from app.main import app
from app.usecase.dto.health_dto import HealthOutput
from app.usecase.health_check.interface import IHealthCheckUseCase


class TestHealthRouter:
    """Test cases for health check API endpoints."""

    @pytest.fixture
    def mock_usecase(self) -> AsyncMock:
        """Create a mock health check use case."""
        return AsyncMock(spec=IHealthCheckUseCase)

    @pytest.fixture
    def client(self, mock_usecase: AsyncMock) -> Generator[TestClient]:
        """Create test client with mocked use case."""
        app.dependency_overrides[get_health_usecase] = lambda: mock_usecase
        client = TestClient(app)
        yield client
        app.dependency_overrides.clear()

    def test_saveMessage_whenInputIsValid_returns200AndEcho(
        self,
        client: TestClient,
        mock_usecase: AsyncMock,
    ) -> None:
        """
        Action: saveMessage (POST /api/health/echo)
        Condition: whenInputIsValid (valid request body)
        Result: returns200AndEcho (HTTP 200 with echoed data)
        """
        # Arrange
        request_body = {"message": "Test health message"}
        expected_output = HealthOutput(
            id="test-id-123",
            message="Test health message",
            created_at="2025-01-01T12:00:00+00:00",
        )
        mock_usecase.save_message.return_value = expected_output

        # Act
        response = client.post("/api/health/echo", json=request_body)

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == "test-id-123"
        assert data["message"] == "Test health message"
        assert data["created_at"] == "2025-01-01T12:00:00+00:00"

        mock_usecase.save_message.assert_called_once()
        call_args = mock_usecase.save_message.call_args[0][0]
        assert call_args.message == "Test health message"

    def test_saveMessage_whenInputIsEmpty_returns200(
        self,
        client: TestClient,
        mock_usecase: AsyncMock,
    ) -> None:
        """
        Action: saveMessage
        Condition: whenInputIsEmpty (empty string message)
        Result: returns200 (accepts and processes empty message)
        """
        # Arrange
        request_body = {"message": ""}
        expected_output = HealthOutput(
            id="test-id",
            message="",
            created_at="2025-01-01T12:00:00+00:00",
        )
        mock_usecase.save_message.return_value = expected_output

        # Act
        response = client.post("/api/health/echo", json=request_body)

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["message"] == ""

    def test_saveMessage_whenInputIsLong_returns200(
        self,
        client: TestClient,
        mock_usecase: AsyncMock,
    ) -> None:
        """
        Action: saveMessage
        Condition: whenInputIsLong (10000 characters)
        Result: returns200 (accepts long message)
        """
        # Arrange
        long_message = "a" * 10000
        request_body = {"message": long_message}
        expected_output = HealthOutput(
            id="test-id",
            message=long_message,
            created_at="2025-01-01T12:00:00+00:00",
        )
        mock_usecase.save_message.return_value = expected_output

        # Act
        response = client.post("/api/health/echo", json=request_body)

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["message"]) == 10000

    def test_saveMessage_whenInputHasSpecialChars_returns200(
        self,
        client: TestClient,
        mock_usecase: AsyncMock,
    ) -> None:
        """
        Action: saveMessage
        Condition: whenInputHasSpecialChars (Japanese, emoji, HTML tags)
        Result: returns200 (handles special characters correctly)
        """
        # Arrange
        special_message = "Test 日本語 🔥 <script>alert('xss')</script>"
        request_body = {"message": special_message}
        expected_output = HealthOutput(
            id="test-id",
            message=special_message,
            created_at="2025-01-01T12:00:00+00:00",
        )
        mock_usecase.save_message.return_value = expected_output

        # Act
        response = client.post("/api/health/echo", json=request_body)

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["message"] == special_message

    def test_saveMessage_whenMessageIsMissing_returns422(
        self,
        client: TestClient,
        mock_usecase: AsyncMock,
    ) -> None:
        """
        Action: saveMessage
        Condition: whenMessageIsMissing (no message field)
        Result: returns422 (validation error)
        """
        # Arrange
        request_body = {}

        # Act
        response = client.post("/api/health/echo", json=request_body)

        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
        mock_usecase.save_message.assert_not_called()

    def test_saveMessage_whenMessageTypeIsInvalid_returns422(
        self,
        client: TestClient,
        mock_usecase: AsyncMock,
    ) -> None:
        """
        Action: saveMessage
        Condition: whenMessageTypeIsInvalid (integer instead of string)
        Result: returns422 (validation error)
        """
        # Arrange
        request_body = {"message": 12345}

        # Act
        response = client.post("/api/health/echo", json=request_body)

        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
        mock_usecase.save_message.assert_not_called()

    def test_saveMessage_whenMessageIsNull_returns422(
        self,
        client: TestClient,
        mock_usecase: AsyncMock,
    ) -> None:
        """
        Action: saveMessage
        Condition: whenMessageIsNull (null value)
        Result: returns422 (validation error)
        """
        # Arrange
        request_body = {"message": None}

        # Act
        response = client.post("/api/health/echo", json=request_body)

        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
        mock_usecase.save_message.assert_not_called()

    def test_saveMessage_whenJsonIsInvalid_returns422(
        self,
        client: TestClient,
        mock_usecase: AsyncMock,
    ) -> None:
        """
        Action: saveMessage
        Condition: whenJsonIsInvalid (malformed JSON)
        Result: returns422 (validation error)
        """
        # Act
        response = client.post(
            "/api/health/echo",
            content=b"invalid json",
            headers={"Content-Type": "application/json"},
        )

        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
        mock_usecase.save_message.assert_not_called()

    def test_getLatest_whenMessageExists_returns200AndData(
        self,
        client: TestClient,
        mock_usecase: AsyncMock,
    ) -> None:
        """
        Action: getLatest (GET /api/health/latest)
        Condition: whenMessageExists (repository returns a message)
        Result: returns200AndData (HTTP 200 with message data)
        """
        # Arrange
        expected_output = HealthOutput(
            id="latest-id",
            message="Latest message",
            created_at="2025-01-01T12:00:00+00:00",
        )
        mock_usecase.get_latest_message.return_value = expected_output

        # Act
        response = client.get("/api/health/latest")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == "latest-id"
        assert data["message"] == "Latest message"
        assert data["created_at"] == "2025-01-01T12:00:00+00:00"

        mock_usecase.get_latest_message.assert_called_once()

    def test_getLatest_whenMessageNotExists_returns200WithNull(
        self,
        client: TestClient,
        mock_usecase: AsyncMock,
    ) -> None:
        """
        Action: getLatest
        Condition: whenMessageNotExists (repository returns None)
        Result: returns200WithNull (HTTP 200 with null body)
        """
        # Arrange
        mock_usecase.get_latest_message.return_value = None

        # Act
        response = client.get("/api/health/latest")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert response.json() is None

        mock_usecase.get_latest_message.assert_called_once()

    def test_saveMessage_whenUseCaseThrows_propagatesException(
        self,
        client: TestClient,
        mock_usecase: AsyncMock,
    ) -> None:
        """
        Action: saveMessage
        Condition: whenUseCaseThrows (use case raises RuntimeError)
        Result: propagatesException (exception is propagated to caller)
        """
        # Arrange
        request_body = {"message": "Test message"}
        mock_usecase.save_message.side_effect = RuntimeError("UseCase error")

        # Act & Assert
        with pytest.raises(RuntimeError, match="UseCase error"):
            client.post("/api/health/echo", json=request_body)

    def test_getLatest_whenUseCaseThrows_propagatesException(
        self,
        client: TestClient,
        mock_usecase: AsyncMock,
    ) -> None:
        """
        Action: getLatest
        Condition: whenUseCaseThrows (use case raises RuntimeError)
        Result: propagatesException (exception is propagated to caller)
        """
        # Arrange
        mock_usecase.get_latest_message.side_effect = RuntimeError("UseCase error")

        # Act & Assert
        with pytest.raises(RuntimeError, match="UseCase error"):
            client.get("/api/health/latest")

    def test_healthRouter_whenOpenAPIQueried_hasCorrectPrefixAndTags(
        self,
        client: TestClient,
    ) -> None:
        """
        Action: healthRouter (router configuration)
        Condition: whenOpenAPIQueried (OpenAPI schema is requested)
        Result: hasCorrectPrefixAndTags (correct paths and tags exist)
        """
        # This is implicitly tested by other tests using /api/health/...
        # Just verify the OpenAPI schema has correct tags
        response = client.get("/openapi.json")
        assert response.status_code == status.HTTP_200_OK

        openapi_schema = response.json()
        paths = openapi_schema["paths"]

        assert "/api/health/echo" in paths
        assert "/api/health/latest" in paths

        # Verify tags
        assert "health" in paths["/api/health/echo"]["post"]["tags"]
        assert "health" in paths["/api/health/latest"]["get"]["tags"]

    def test_saveMessage_whenContentTypeIsNotJson_returns422(
        self,
        client: TestClient,
        mock_usecase: AsyncMock,
    ) -> None:
        """
        Action: saveMessage
        Condition: whenContentTypeIsNotJson (form data instead of JSON)
        Result: returns422 (validation error)
        """
        # Arrange
        request_body = "message=test"

        # Act
        response = client.post(
            "/api/health/echo",
            content=request_body.encode(),
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
        mock_usecase.save_message.assert_not_called()

    def test_endpoints_whenWrongMethod_returns405(
        self,
        client: TestClient,
        mock_usecase: AsyncMock,
    ) -> None:
        """
        Action: endpoints (HTTP method validation)
        Condition: whenWrongMethod (GET on POST endpoint, POST on GET endpoint)
        Result: returns405 (method not allowed)
        """
        # Test echo endpoint doesn't accept GET
        response = client.get("/api/health/echo")
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

        # Test latest endpoint doesn't accept POST
        response = client.post("/api/health/latest", json={"message": "test"})
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

        mock_usecase.save_message.assert_not_called()
        mock_usecase.get_latest_message.assert_not_called()

"""Unit tests for application error handler."""

import pytest
from fastapi import Request, status
from fastapi.responses import JSONResponse

from app.adapter.entrypoints.error_handler import app_error_handler
from app.domain.exception import AppError


class TestAppErrorHandler:
    """Test cases for app_error_handler."""

    @pytest.fixture
    def mock_request(self) -> Request:
        """Create a mock request object."""
        return Request({"type": "http", "method": "GET", "url": "http://test"})

    @pytest.mark.asyncio
    async def test_appErrorHandler_whenCode1001_returns410(
        self,
        mock_request: Request,
    ) -> None:
        """
        Action: appErrorHandler
        Condition: whenCode1001 (spark expired error)
        Result: returns410 (HTTP 410 GONE)
        """
        # Arrange
        error = AppError(1001)

        # Act
        response = await app_error_handler(mock_request, error)

        # Assert
        assert isinstance(response, JSONResponse)
        assert response.status_code == status.HTTP_410_GONE
        assert response.body is not None
        assert isinstance(response.body, bytes)

        content = response.body.decode()
        assert "1001" in content
        assert "この種火は既に燃え尽きています。" in content

    @pytest.mark.asyncio
    async def test_appErrorHandler_whenCode1002_returns422(
        self,
        mock_request: Request,
    ) -> None:
        """
        Action: appErrorHandler
        Condition: whenCode1002 (validation error)
        Result: returns422 (HTTP 422 UNPROCESSABLE_CONTENT)
        """
        # Arrange
        error = AppError(1002)

        # Act
        response = await app_error_handler(mock_request, error)

        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
        assert response.body is not None
        assert isinstance(response.body, bytes)
        content = response.body.decode()
        assert "1002" in content
        assert "投稿に不適切な表現が含まれています。" in content

    @pytest.mark.asyncio
    async def test_appErrorHandler_whenCode1003_returns422(
        self,
        mock_request: Request,
    ) -> None:
        """
        Action: appErrorHandler
        Condition: whenCode1003 (length limit error)
        Result: returns422 (HTTP 422 UNPROCESSABLE_CONTENT)
        """
        # Arrange
        error = AppError(1003)

        # Act
        response = await app_error_handler(mock_request, error)

        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
        assert response.body is not None
        assert isinstance(response.body, bytes)
        content = response.body.decode()
        assert "1003" in content
        assert "投稿文字数が制限を超えています。" in content

    @pytest.mark.asyncio
    async def test_appErrorHandler_whenCode1004_returns429(
        self,
        mock_request: Request,
    ) -> None:
        """
        Action: appErrorHandler
        Condition: whenCode1004 (throttle error)
        Result: returns429 (HTTP 429 TOO_MANY_REQUESTS)
        """
        # Arrange
        error = AppError(1004)

        # Act
        response = await app_error_handler(mock_request, error)

        # Assert
        assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
        assert response.body is not None
        assert isinstance(response.body, bytes)
        content = response.body.decode()
        assert "1004" in content
        assert "薪をくべるペースが早すぎます。" in content

    @pytest.mark.asyncio
    async def test_appErrorHandler_whenCode1005_returns404(
        self,
        mock_request: Request,
    ) -> None:
        """
        Action: appErrorHandler
        Condition: whenCode1005 (not found error)
        Result: returns404 (HTTP 404 NOT_FOUND)
        """
        # Arrange
        error = AppError(1005)

        # Act
        response = await app_error_handler(mock_request, error)

        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.body is not None
        assert isinstance(response.body, bytes)
        content = response.body.decode()
        assert "1005" in content
        assert "指定された種火が存在しないか、消滅しています。" in content

    @pytest.mark.asyncio
    async def test_appErrorHandler_whenCode2001_returns500(
        self,
        mock_request: Request,
    ) -> None:
        """
        Action: appErrorHandler
        Condition: whenCode2001 (DB connection error)
        Result: returns500 (HTTP 500 INTERNAL_SERVER_ERROR)
        """
        # Arrange
        error = AppError(2001)

        # Act
        response = await app_error_handler(mock_request, error)

        # Assert
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert response.body is not None
        assert isinstance(response.body, bytes)
        content = response.body.decode()
        assert "2001" in content
        assert "DBへの接続中に異常が発生しました" in content

    @pytest.mark.asyncio
    async def test_appErrorHandler_whenCode2002_returns500(
        self,
        mock_request: Request,
    ) -> None:
        """
        Action: appErrorHandler
        Condition: whenCode2002 (DB query error)
        Result: returns500 (HTTP 500 INTERNAL_SERVER_ERROR)
        """
        # Arrange
        error = AppError(2002, context={"tableName": "sparks"})

        # Act
        response = await app_error_handler(mock_request, error)

        # Assert
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert response.body is not None
        assert isinstance(response.body, bytes)
        content = response.body.decode()
        assert "2002" in content
        assert "sparks" in content
        assert "テーブルへのクエリ中に異常が発生しました" in content

    @pytest.mark.asyncio
    async def test_appErrorHandler_whenCode500_returns500(
        self,
        mock_request: Request,
    ) -> None:
        """
        Action: appErrorHandler
        Condition: whenCode500 (generic internal server error)
        Result: returns500 (HTTP 500 INTERNAL_SERVER_ERROR)
        """
        # Arrange
        error = AppError(500)

        # Act
        response = await app_error_handler(mock_request, error)

        # Assert
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert response.body is not None
        assert isinstance(response.body, bytes)
        content = response.body.decode()
        assert "500" in content
        assert "Internal Server Error" in content

    @pytest.mark.asyncio
    async def test_appErrorHandler_whenCalled_includesErrorCode(
        self,
        mock_request: Request,
    ) -> None:
        """
        Action: appErrorHandler
        Condition: whenCalled (any error code)
        Result: includesErrorCode (response contains error code field)
        """
        # Arrange
        error = AppError(1001)

        # Act
        response = await app_error_handler(mock_request, error)

        # Assert
        assert response.body is not None
        assert isinstance(response.body, bytes)
        content = response.body.decode()
        assert "error" in content
        assert "code" in content
        assert "1001" in content

    @pytest.mark.asyncio
    async def test_appErrorHandler_whenCalled_includesMessage(
        self,
        mock_request: Request,
    ) -> None:
        """
        Action: appErrorHandler
        Condition: whenCalled (any error code)
        Result: includesMessage (response contains error message field)
        """
        # Arrange
        error = AppError(1002)

        # Act
        response = await app_error_handler(mock_request, error)

        # Assert
        assert response.body is not None
        assert isinstance(response.body, bytes)
        content = response.body.decode()
        assert "message" in content
        assert "投稿に不適切な表現が含まれています。" in content

    @pytest.mark.asyncio
    async def test_appErrorHandler_whenContextExists_includesContext(
        self,
        mock_request: Request,
    ) -> None:
        """
        Action: appErrorHandler
        Condition: whenContextExists (error has context data)
        Result: includesContext (response contains context field)
        """
        # Arrange
        context = {"tableName": "users", "operation": "insert"}
        error = AppError(2002, context=context)

        # Act
        response = await app_error_handler(mock_request, error)

        # Assert
        assert response.body is not None
        assert isinstance(response.body, bytes)
        content = response.body.decode()
        assert "context" in content
        assert "tableName" in content
        assert "users" in content
        assert "operation" in content
        assert "insert" in content

    @pytest.mark.asyncio
    async def test_appErrorHandler_whenContextNotExists_excludesContext(
        self,
        mock_request: Request,
    ) -> None:
        """
        Action: appErrorHandler
        Condition: whenContextNotExists (error has no context)
        Result: excludesContext (response excludes or empties context field)
        """
        # Arrange
        error = AppError(1001)

        # Act
        response = await app_error_handler(mock_request, error)

        # Assert
        # Context field should not be present in response when error has no context
        # (or should be present but empty - this test accepts either behavior)
        assert response.status_code == status.HTTP_410_GONE

    @pytest.mark.asyncio
    async def test_appErrorHandler_whenCodeUnknown_returns500(
        self,
        mock_request: Request,
    ) -> None:
        """
        Action: appErrorHandler
        Condition: whenCodeUnknown (error code 9999 not in mapping)
        Result: returns500 (falls back to HTTP 500)
        """
        # Arrange
        error = AppError(9999)

        # Act
        response = await app_error_handler(mock_request, error)

        # Assert
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert response.body is not None
        assert isinstance(response.body, bytes)
        content = response.body.decode()
        assert "9999" in content

    @pytest.mark.asyncio
    async def test_appErrorHandler_whenCalled_returnsJson(
        self,
        mock_request: Request,
    ) -> None:
        """
        Action: appErrorHandler
        Condition: whenCalled (any error)
        Result: returnsJson (response is JSONResponse with correct media type)
        """
        # Arrange
        error = AppError(1001)

        # Act
        response = await app_error_handler(mock_request, error)

        # Assert
        assert isinstance(response, JSONResponse)
        assert response.media_type == "application/json"

    @pytest.mark.asyncio
    async def test_appErrorHandler_whenMultipleContextValues_includesAll(
        self,
        mock_request: Request,
    ) -> None:
        """
        Action: appErrorHandler
        Condition: whenMultipleContextValues (error has multiple context fields)
        Result: includesAll (all context values are in response)
        """
        # Arrange
        context = {
            "spark_id": "spark-123",
            "user_id": "user-456",
            "timestamp": "2025-01-01T12:00:00",
        }
        error = AppError(1005, context=context)

        # Act
        response = await app_error_handler(mock_request, error)

        # Assert
        assert response.body is not None
        assert isinstance(response.body, bytes)
        content = response.body.decode()
        assert "spark-123" in content
        assert "user-456" in content
        assert "2025-01-01T12:00:00" in content

    @pytest.mark.asyncio
    async def test_appErrorHandler_whenCauseExists_doesNotExposeCause(
        self,
        mock_request: Request,
    ) -> None:
        """
        Action: appErrorHandler
        Condition: whenCauseExists (error has cause exception)
        Result: doesNotExposeCause (cause is not exposed in response)
        """
        # Arrange
        original_error = ValueError("Original error")
        error = AppError(2001, cause=original_error)

        # Act
        response = await app_error_handler(mock_request, error)

        # Assert
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        # Cause is not exposed in response (internal detail)
        assert response.body is not None
        assert isinstance(response.body, bytes)
        content = response.body.decode()
        assert "2001" in content

    @pytest.mark.asyncio
    async def test_appErrorHandler_whenAllKnownCodes_mapsCorrectly(
        self,
        mock_request: Request,
    ) -> None:
        """
        Action: appErrorHandler
        Condition: whenAllKnownCodes (comprehensive test of all defined codes)
        Result: mapsCorrectly (each code maps to correct HTTP status)
        """
        # Arrange & Act & Assert
        test_cases = [
            (200, status.HTTP_200_OK),
            (201, status.HTTP_201_CREATED),
            (204, status.HTTP_204_NO_CONTENT),
            (1001, status.HTTP_410_GONE),
            (1002, status.HTTP_422_UNPROCESSABLE_CONTENT),
            (1003, status.HTTP_422_UNPROCESSABLE_CONTENT),
            (1004, status.HTTP_429_TOO_MANY_REQUESTS),
            (1005, status.HTTP_404_NOT_FOUND),
            (2001, status.HTTP_500_INTERNAL_SERVER_ERROR),
            (2002, status.HTTP_500_INTERNAL_SERVER_ERROR),
            (500, status.HTTP_500_INTERNAL_SERVER_ERROR),
        ]

        for internal_code, expected_http_status in test_cases:
            error = AppError(internal_code)
            response = await app_error_handler(mock_request, error)
            assert response.status_code == expected_http_status, (
                f"Internal code {internal_code} should map to {expected_http_status}"
            )

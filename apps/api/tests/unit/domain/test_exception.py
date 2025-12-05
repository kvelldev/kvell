"""Unit tests for domain exceptions."""

import pytest

from app.domain.constants import INTERNAL_STATUSES
from app.domain.exception import AppError


class TestAppError:
    """Test cases for AppError exception."""

    def test_createAppError_whenCodeOnly_createsSuccessfully(self) -> None:
        """
        Action: createAppError
        Condition: whenCodeOnly (only internal code provided)
        Result: createsSuccessfully (error created with code and default context)
        """
        # Arrange
        internal_code = 1001

        # Act
        error = AppError(internal_code)

        # Assert
        assert error.internal_code == internal_code
        assert error.context == {}
        assert error.cause is None
        assert str(error) == INTERNAL_STATUSES[internal_code]

    def test_createAppError_whenContextProvided_includesContext(self) -> None:
        """
        Action: createAppError
        Condition: whenContextProvided (context dict provided)
        Result: includesContext (error stores and displays context)
        """
        # Arrange
        internal_code = 2002
        context = {"tableName": "users"}

        # Act
        error = AppError(internal_code, context=context)

        # Assert
        assert error.internal_code == internal_code
        assert error.context == context
        assert "users" in str(error)
        assert "テーブルへのクエリ中に異常が発生しました" in str(error)

    def test_createAppError_whenCauseProvided_storesCause(self) -> None:
        """
        Action: createAppError
        Condition: whenCauseProvided (original exception provided)
        Result: storesCause (error stores cause exception)
        """
        # Arrange
        internal_code = 500
        original_exception = ValueError("Original error")

        # Act
        error = AppError(internal_code, cause=original_exception)

        # Assert
        assert error.internal_code == internal_code
        assert error.cause == original_exception
        assert isinstance(error.cause, ValueError)

    def test_createAppError_whenAllParameters_createsSuccessfully(self) -> None:
        """
        Action: createAppError
        Condition: whenAllParameters (code, context, and cause provided)
        Result: createsSuccessfully (all parameters stored correctly)
        """
        # Arrange
        internal_code = 1002
        context = {"word": "禁止ワード"}
        cause = RuntimeError("Validation failed")

        # Act
        error = AppError(internal_code, context=context, cause=cause)

        # Assert
        assert error.internal_code == internal_code
        assert error.context == context
        assert error.cause == cause

    def test_appErrorStr_whenContextExists_includesContext(self) -> None:
        """
        Action: appErrorStr (string representation)
        Condition: whenContextExists (error has context)
        Result: includesContext (str includes context in output)
        """
        # Arrange
        internal_code = 1001
        context = {"spark_id": "123"}

        # Act
        error = AppError(internal_code, context=context)

        # Assert
        error_str = str(error)
        assert "この種火は既に燃え尽きています。" in error_str
        assert "context" in error_str
        assert "123" in error_str

    def test_appErrorStr_whenContextNotExists_excludesContext(self) -> None:
        """
        Action: appErrorStr
        Condition: whenContextNotExists (error has no context)
        Result: excludesContext (str is just the status message)
        """
        # Arrange
        internal_code = 1003

        # Act
        error = AppError(internal_code)

        # Assert
        error_str = str(error)
        assert error_str == INTERNAL_STATUSES[internal_code]
        assert "context" not in error_str

    def test_appErrorStr_whenCodeUnknown_usesDefault(self) -> None:
        """
        Action: appErrorStr
        Condition: whenCodeUnknown (code not in INTERNAL_STATUSES)
        Result: usesDefault (falls back to 500 message)
        """
        # Arrange
        unknown_code = 9999

        # Act
        error = AppError(unknown_code)

        # Assert
        assert error.internal_code == unknown_code
        assert str(error) == INTERNAL_STATUSES[500]

    def test_appErrorStr_whenMessageHasPlaceholders_replacesWithContext(self) -> None:
        """
        Action: appErrorStr
        Condition: whenMessageHasPlaceholders (message contains {tableName})
        Result: replacesWithContext (placeholders filled from context)
        """
        # Arrange
        internal_code = 2002
        context = {"tableName": "sparks"}

        # Act
        error = AppError(internal_code, context=context)

        # Assert
        assert "sparks" in str(error)
        assert "{tableName}" not in str(error)

    def test_appError_whenContextPartial_doesNotRaise(self) -> None:
        """
        Action: appError
        Condition: whenContextPartial (context missing expected keys)
        Result: doesNotRaise (gracefully handles missing keys)
        """
        # Arrange
        internal_code = 2002
        context = {"other_key": "value"}

        # Act
        error = AppError(internal_code, context=context)

        # Assert
        # Should not raise an error, just not replace the placeholder
        assert error.internal_code == internal_code
        assert error.context == context

    def test_appError_whenCreated_isException(self) -> None:
        """
        Action: appError
        Condition: whenCreated
        Result: isException (inherits from Exception class)
        """
        # Arrange
        error = AppError(1001)

        # Assert
        assert isinstance(error, Exception)

    def test_appError_whenRaised_canBeCaught(self) -> None:
        """
        Action: appError
        Condition: whenRaised (exception is raised)
        Result: canBeCaught (can be caught with except AppError)
        """
        # Arrange
        internal_code = 1004

        # Act & Assert
        with pytest.raises(AppError) as exc_info:
            raise AppError(internal_code)

        assert exc_info.value.internal_code == internal_code

    def test_appError_whenDifferentCodes_hasCorrectMessages(self) -> None:
        """
        Action: appError
        Condition: whenDifferentCodes (comprehensive test of all codes)
        Result: hasCorrectMessages (each code maps to correct message)
        """
        # Arrange & Act & Assert
        test_cases = [
            (200, "OK"),
            (1001, "この種火は既に燃え尽きています。"),
            (1002, "投稿に不適切な表現が含まれています。"),
            (1003, "投稿文字数が制限を超えています。"),
            (1004, "薪をくべるペースが早すぎます。"),
            (1005, "指定された種火が存在しないか、消滅しています。"),
            (2001, "DBへの接続中に異常が発生しました"),
            (500, "Internal Server Error"),
        ]

        for code, expected_message in test_cases:
            error = AppError(code)
            assert error.internal_code == code
            assert str(error) == expected_message

    def test_appError_whenContextMutated_reflectsChanges(self) -> None:
        """
        Action: appError
        Condition: whenContextMutated (original context dict is modified)
        Result: reflectsChanges (documents current behavior - not defensive copy)
        """
        # Arrange
        context = {"key": "value"}
        error = AppError(1001, context=context)

        # Act - modify original context
        context["key"] = "modified"

        # Assert - error context should not be affected (defensive copy is not required by spec)
        # This test documents current behavior
        assert error.context["key"] == "modified"

    def test_createAppError_whenContextEmpty_doesNotShowContext(self) -> None:
        """
        Action: createAppError
        Condition: whenContextEmpty (empty dict provided)
        Result: doesNotShowContext (context not shown in str output)
        """
        # Arrange
        error = AppError(1001, context={})

        # Assert
        assert error.context == {}
        assert "context" not in str(error)

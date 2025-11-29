"""Unit tests for JsonLogger."""

import json
from io import StringIO
from unittest.mock import MagicMock, patch

import pytest

from app.adapter.infra.logger import JsonLogger


class TestJsonLogger:
    """Test cases for JsonLogger."""

    @pytest.fixture
    def logger(self) -> JsonLogger:
        """Create a JsonLogger instance."""
        return JsonLogger(service_name="test-service")

    @pytest.fixture
    def mock_stdout(self) -> StringIO:
        """Create a mock stdout buffer."""
        return StringIO()

    def test_loggerInit_whenServiceNameProvided_setsServiceName(self, logger: JsonLogger) -> None:
        """
        Action: loggerInit
        Condition: whenServiceNameProvided (service_name="test-service")
        Result: setsServiceName (logger has correct service name)
        """
        assert logger.service_name == "test-service"
        assert logger._logger is not None

    def test_loggerInit_whenServiceNameOmitted_usesDefault(self) -> None:
        """
        Action: loggerInit
        Condition: whenServiceNameOmitted (no service_name parameter)
        Result: usesDefault (defaults to "kvell-api")
        """
        logger = JsonLogger()
        assert logger.service_name == "kvell-api"

    def test_info_whenCalled_outputsJsonWithCorrectFields(
        self, logger: JsonLogger, mock_stdout: StringIO
    ) -> None:
        """
        Action: info
        Condition: whenCalled (event_id and message provided)
        Result: outputsJsonWithCorrectFields (level, service, event_id, message, timestamp, context)
        """
        with patch("sys.stdout", mock_stdout):
            logger.info("TEST_001", "Test info message")

        output = mock_stdout.getvalue()
        log_entry = json.loads(output.strip())

        assert log_entry["level"] == "INFO"
        assert log_entry["service"] == "test-service"
        assert log_entry["event_id"] == "TEST_001"
        assert log_entry["message"] == "Test info message"
        assert "timestamp" in log_entry
        assert log_entry["context"] == {}

    def test_info_whenContextProvided_includesContext(
        self, logger: JsonLogger, mock_stdout: StringIO
    ) -> None:
        """
        Action: info
        Condition: whenContextProvided (context dict provided)
        Result: includesContext (context appears in JSON output)
        """
        context = {"user_id": "123", "action": "login"}

        with patch("sys.stdout", mock_stdout):
            logger.info("TEST_002", "User logged in", context=context)

        output = mock_stdout.getvalue()
        log_entry = json.loads(output.strip())

        assert log_entry["level"] == "INFO"
        assert log_entry["event_id"] == "TEST_002"
        assert log_entry["message"] == "User logged in"
        assert log_entry["context"] == context
        assert log_entry["context"]["user_id"] == "123"
        assert log_entry["context"]["action"] == "login"

    def test_warn_whenCalled_outputsWarnLevel(
        self, logger: JsonLogger, mock_stdout: StringIO
    ) -> None:
        """
        Action: warn
        Condition: whenCalled (warning logged)
        Result: outputsWarnLevel (level="WARN" in JSON)
        """
        with patch("sys.stdout", mock_stdout):
            logger.warn("WARN_001", "Warning message")

        output = mock_stdout.getvalue()
        log_entry = json.loads(output.strip())

        assert log_entry["level"] == "WARN"
        assert log_entry["event_id"] == "WARN_001"
        assert log_entry["message"] == "Warning message"

    def test_warn_whenContextProvided_includesContext(
        self, logger: JsonLogger, mock_stdout: StringIO
    ) -> None:
        """
        Action: warn
        Condition: whenContextProvided (context dict provided)
        Result: includesContext (context appears in JSON output)
        """
        context = {"resource": "disk", "usage": "90%"}

        with patch("sys.stdout", mock_stdout):
            logger.warn("WARN_002", "High disk usage", context=context)

        output = mock_stdout.getvalue()
        log_entry = json.loads(output.strip())

        assert log_entry["level"] == "WARN"
        assert log_entry["context"] == context

    def test_error_whenExceptionProvided_includesErrorInfo(
        self, logger: JsonLogger, mock_stdout: StringIO
    ) -> None:
        """
        Action: error
        Condition: whenExceptionProvided (error parameter is Exception)
        Result: includesErrorInfo (error.type and error.message in JSON)
        """
        test_error = ValueError("Test error")

        with patch("sentry_sdk.capture_exception"), patch(
            "sentry_sdk.push_scope"
        ), patch("sys.stdout", mock_stdout):
            logger.error("ERROR_001", "An error occurred", error=test_error)

        output = mock_stdout.getvalue()
        log_entry = json.loads(output.strip())

        assert log_entry["level"] == "ERROR"
        assert log_entry["event_id"] == "ERROR_001"
        assert log_entry["message"] == "An error occurred"
        assert "error" in log_entry
        assert log_entry["error"]["type"] == "ValueError"
        assert log_entry["error"]["message"] == "Test error"

    def test_error_whenContextProvided_includesContext(
        self, logger: JsonLogger, mock_stdout: StringIO
    ) -> None:
        """
        Action: error
        Condition: whenContextProvided (both error and context provided)
        Result: includesContext (context appears in JSON)
        """
        test_error = RuntimeError("Database connection failed")
        context = {"db_host": "localhost", "db_port": 5432}

        with patch("sentry_sdk.capture_exception"), patch(
            "sentry_sdk.push_scope"
        ), patch("sys.stdout", mock_stdout):
            logger.error(
                "ERROR_002",
                "Database error",
                error=test_error,
                context=context,
            )

        output = mock_stdout.getvalue()
        log_entry = json.loads(output.strip())

        assert log_entry["level"] == "ERROR"
        assert log_entry["context"] == context
        assert log_entry["error"]["type"] == "RuntimeError"

    def test_error_whenNoException_sendsMessageToSentry(
        self, logger: JsonLogger, mock_stdout: StringIO
    ) -> None:
        """
        Action: error
        Condition: whenNoException (error parameter not provided)
        Result: sendsMessageToSentry (capture_message called instead of capture_exception)
        """
        with patch("sentry_sdk.capture_message") as mock_capture_message, patch(
            "sentry_sdk.push_scope"
        ), patch("sys.stdout", mock_stdout):
            logger.error("ERROR_003", "Something went wrong")

        output = mock_stdout.getvalue()
        log_entry = json.loads(output.strip())

        assert log_entry["level"] == "ERROR"
        assert log_entry["event_id"] == "ERROR_003"
        assert "error" not in log_entry
        mock_capture_message.assert_called_once_with("Something went wrong")

    def test_error_whenExceptionProvided_sendsToSentry(
        self, logger: JsonLogger, mock_stdout: StringIO
    ) -> None:
        """
        Action: error
        Condition: whenExceptionProvided (error parameter is Exception)
        Result: sendsToSentry (sentry_sdk.capture_exception called)
        """
        test_error = ValueError("Test error for Sentry")

        with patch("sentry_sdk.capture_exception") as mock_capture, patch(
            "sentry_sdk.push_scope"
        ) as mock_scope, patch("sys.stdout", mock_stdout):
            logger.error("ERROR_004", "Error message", error=test_error)

        mock_capture.assert_called_once_with(test_error)
        mock_scope.assert_called_once()

    def test_error_whenContextProvided_sendsContextToSentry(
        self, logger: JsonLogger, mock_stdout: StringIO
    ) -> None:
        """
        Action: error
        Condition: whenContextProvided (context dict provided)
        Result: sendsContextToSentry (set_tag and set_context called)
        """
        test_error = RuntimeError("Test error")
        context = {"key": "value"}

        mock_scope_instance = MagicMock()

        with patch(
            "sentry_sdk.push_scope", return_value=mock_scope_instance
        ) as mock_push_scope, patch("sentry_sdk.capture_exception"), patch(
            "sys.stdout", mock_stdout
        ):
            mock_push_scope.return_value.__enter__ = MagicMock(
                return_value=mock_scope_instance
            )
            mock_push_scope.return_value.__exit__ = MagicMock(return_value=False)

            logger.error("ERROR_005", "Error with context", error=test_error, context=context)

        mock_scope_instance.set_tag.assert_called_once_with("event_id", "ERROR_005")
        mock_scope_instance.set_context.assert_called_once_with("app_context", context)

    def test_logEntry_whenGenerated_containsIsoTimestamp(
        self, logger: JsonLogger, mock_stdout: StringIO
    ) -> None:
        """
        Action: logEntry
        Condition: whenGenerated (any log method called)
        Result: containsIsoTimestamp (timestamp field in ISO 8601 format)
        """
        with patch("sys.stdout", mock_stdout):
            logger.info("TEST_003", "Test message")

        output = mock_stdout.getvalue()
        log_entry = json.loads(output.strip())

        assert "timestamp" in log_entry
        # Verify it's in ISO format (contains 'T' separator)
        assert "T" in log_entry["timestamp"]

    def test_logEntry_whenGenerated_isSingleLineJson(
        self, logger: JsonLogger, mock_stdout: StringIO
    ) -> None:
        """
        Action: logEntry
        Condition: whenGenerated
        Result: isSingleLineJson (output is exactly one line of valid JSON)
        """
        with patch("sys.stdout", mock_stdout):
            logger.info("TEST_004", "Test message")

        output = mock_stdout.getvalue()
        lines = output.strip().split("\n")

        # Should be exactly one line
        assert len(lines) == 1
        # Should be valid JSON
        json.loads(lines[0])

    def test_log_whenJapaneseChars_handlesCorrectly(
        self, logger: JsonLogger, mock_stdout: StringIO
    ) -> None:
        """
        Action: log (info method)
        Condition: whenJapaneseChars (message and context contain Japanese)
        Result: handlesCorrectly (Japanese characters properly encoded in JSON)
        """
        with patch("sys.stdout", mock_stdout):
            logger.info("TEST_005", "テストメッセージ", context={"名前": "太郎"})

        output = mock_stdout.getvalue()
        log_entry = json.loads(output.strip())

        assert log_entry["message"] == "テストメッセージ"
        assert log_entry["context"]["名前"] == "太郎"

    def test_log_whenSpecialChars_escapesCorrectly(
        self, logger: JsonLogger, mock_stdout: StringIO
    ) -> None:
        """
        Action: log (info method)
        Condition: whenSpecialChars (message contains <>&'")
        Result: escapesCorrectly (special characters properly escaped in JSON)
        """
        message = "Test with special chars: <>&'\""
        context = {"data": 'value with "quotes"'}

        with patch("sys.stdout", mock_stdout):
            logger.info("TEST_006", message, context=context)

        output = mock_stdout.getvalue()
        log_entry = json.loads(output.strip())

        assert log_entry["message"] == message
        assert log_entry["context"]["data"] == 'value with "quotes"'

    def test_log_whenMultipleCalls_producesMultipleLines(
        self, logger: JsonLogger, mock_stdout: StringIO
    ) -> None:
        """
        Action: log (multiple calls)
        Condition: whenMultipleCalls (info, warn, error called sequentially)
        Result: producesMultipleLines (each call produces separate JSON line)
        """
        with patch("sys.stdout", mock_stdout):
            logger.info("TEST_007", "First message")
            logger.warn("TEST_008", "Second message")
            logger.error("TEST_009", "Third message")

        output = mock_stdout.getvalue()
        lines = [line for line in output.split("\n") if line.strip()]

        assert len(lines) == 3

        first_entry = json.loads(lines[0])
        second_entry = json.loads(lines[1])
        third_entry = json.loads(lines[2])

        assert first_entry["level"] == "INFO"
        assert second_entry["level"] == "WARN"
        assert third_entry["level"] == "ERROR"

    def test_info_whenContextEmpty_includesEmptyContext(
        self, logger: JsonLogger, mock_stdout: StringIO
    ) -> None:
        """
        Action: info
        Condition: whenContextEmpty (context={})
        Result: includesEmptyContext (context field is empty dict in JSON)
        """
        with patch("sys.stdout", mock_stdout):
            logger.info("TEST_010", "Test message", context={})

        output = mock_stdout.getvalue()
        log_entry = json.loads(output.strip())

        assert log_entry["context"] == {}

    def test_info_whenContextNone_defaultsToEmpty(
        self, logger: JsonLogger, mock_stdout: StringIO
    ) -> None:
        """
        Action: info
        Condition: whenContextNone (context=None)
        Result: defaultsToEmpty (context field becomes empty dict)
        """
        with patch("sys.stdout", mock_stdout):
            logger.info("TEST_011", "Test message", context=None)

        output = mock_stdout.getvalue()
        log_entry = json.loads(output.strip())

        assert log_entry["context"] == {}

    def test_error_whenComplexException_extractsTypeAndMessage(
        self, logger: JsonLogger, mock_stdout: StringIO
    ) -> None:
        """
        Action: error
        Condition: whenComplexException (KeyError with traceback)
        Result: extractsTypeAndMessage (error.type and error.message in JSON)
        """
        try:
            raise KeyError("missing_key")
        except KeyError as e:
            with patch("sentry_sdk.capture_exception"), patch(
                "sentry_sdk.push_scope"
            ), patch("sys.stdout", mock_stdout):
                logger.error("ERROR_010", "Key error occurred", error=e)

        output = mock_stdout.getvalue()
        log_entry = json.loads(output.strip())

        assert log_entry["error"]["type"] == "KeyError"
        assert "missing_key" in log_entry["error"]["message"]

    def test_logger_whenAllLevels_includesServiceName(
        self, logger: JsonLogger, mock_stdout: StringIO
    ) -> None:
        """
        Action: logger (all log levels)
        Condition: whenAllLevels (info, warn, error)
        Result: includesServiceName (service field in all JSON outputs)
        """
        with patch("sys.stdout", mock_stdout):
            logger.info("TEST_012", "Info")
            logger.warn("TEST_013", "Warn")

        with patch("sentry_sdk.capture_exception"), patch(
            "sentry_sdk.push_scope"
        ), patch("sys.stdout", mock_stdout):
            logger.error("TEST_014", "Error")

        output = mock_stdout.getvalue()
        lines = [line for line in output.split("\n") if line.strip()]

        for line in lines:
            log_entry = json.loads(line)
            assert log_entry["service"] == "test-service"

    def test_log_whenContextNested_preservesStructure(
        self, logger: JsonLogger, mock_stdout: StringIO
    ) -> None:
        """
        Action: log (info method)
        Condition: whenContextNested (nested dict structure in context)
        Result: preservesStructure (nested structure preserved in JSON output)
        """
        context = {
            "user": {"id": "123", "name": "Test User"},
            "request": {"method": "POST", "path": "/api/test"},
        }

        with patch("sys.stdout", mock_stdout):
            logger.info("TEST_015", "Nested context test", context=context)

        output = mock_stdout.getvalue()
        log_entry = json.loads(output.strip())

        assert log_entry["context"]["user"]["id"] == "123"
        assert log_entry["context"]["request"]["method"] == "POST"

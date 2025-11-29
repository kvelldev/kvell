"""JSON structured logger implementation.

This module provides a JSON-based logger that outputs structured logs
for CloudWatch and sends errors to Sentry.
"""

import json
import logging
import sys
from datetime import UTC, datetime
from typing import Any

import sentry_sdk

from app.usecase.ports.logger import ILogger


class JsonLogger(ILogger):
    """JSON structured logger implementation."""

    def __init__(self, service_name: str = "kvell-api") -> None:
        """Initialize the logger.

        Args:
            service_name: Name of the service for logging context

        """
        self.service_name = service_name
        # Setup standard library logger (format disabled for JSON output)
        self._logger = logging.getLogger(service_name)
        self._logger.setLevel(logging.INFO)
        handler = logging.StreamHandler(sys.stdout)
        self._logger.addHandler(handler)

    def _log(
        self,
        level: str,
        event_id: str,
        message: str,
        context: dict[str, Any] | None = None,
        error: Exception | None = None,
    ) -> None:
        # 構造化ログの構築
        log_entry: dict[str, Any] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": level,
            "service": self.service_name,
            "event_id": event_id,
            "message": message,
            "context": context or {},
        }

        if error:
            log_entry["error"] = {"type": type(error).__name__, "message": str(error)}

        # Output as single-line JSON for CloudWatch Logs parsing
        sys.stdout.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

    def info(
        self, event_id: str, message: str, context: dict[str, Any] | None = None
    ) -> None:
        """Log informational message.

        Args:
            event_id: Event identifier
            message: Log message
            context: Additional context data

        """
        self._log("INFO", event_id, message, context)

    def warn(
        self, event_id: str, message: str, context: dict[str, Any] | None = None
    ) -> None:
        """Log warning message.

        Args:
            event_id: Event identifier
            message: Log message
            context: Additional context data

        """
        self._log("WARN", event_id, message, context)

    def error(
        self,
        event_id: str,
        message: str,
        error: Exception | None = None,
        context: dict[str, Any] | None = None,
    ) -> None:
        """Log error message and send to Sentry.

        Args:
            event_id: Event identifier
            message: Log message
            error: Exception object if available
            context: Additional context data

        """
        # 1. Output to CloudWatch
        self._log("ERROR", event_id, message, context, error)

        # 2. Send to Sentry (if initialized)
        #    Explicitly capture_exception to attach context information
        with sentry_sdk.push_scope() as scope:
            scope.set_tag("event_id", event_id)
            if context:
                scope.set_context("app_context", context)
            sentry_sdk.capture_exception(
                error
            ) if error else sentry_sdk.capture_message(message)

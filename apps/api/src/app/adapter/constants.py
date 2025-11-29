"""HTTP status code mapping constants and log event IDs.

Maps internal status codes to HTTP status codes.
Defines event IDs for structured logging.
"""

from typing import Final

from fastapi import status

from app.domain.constants import InternalStatusCode

HttpStatusCode = int

INTERNAL_TO_HTTP_MAP: Final[dict[InternalStatusCode, HttpStatusCode]] = {
    # Success
    200: status.HTTP_200_OK,
    201: status.HTTP_201_CREATED,
    204: status.HTTP_204_NO_CONTENT,
    # Domain Logic Errors -> 4xx Errors
    1001: status.HTTP_410_GONE,
    1002: status.HTTP_422_UNPROCESSABLE_CONTENT,
    1003: status.HTTP_422_UNPROCESSABLE_CONTENT,
    1004: status.HTTP_429_TOO_MANY_REQUESTS,
    1005: status.HTTP_404_NOT_FOUND,
    # Infrastructure Errors -> 500 Internal Server Error
    2001: status.HTTP_500_INTERNAL_SERVER_ERROR,
    2002: status.HTTP_500_INTERNAL_SERVER_ERROR,
    # Fallback
    500: status.HTTP_500_INTERNAL_SERVER_ERROR,
}


class LogEvents:
    """Log event ID constants for structured logging.

    All log calls should use these event IDs instead of raw strings.
    """

    # Health check events
    HEALTH_CHECK_STARTED: Final[str] = "HEALTH_001"
    HEALTH_CHECK_SUCCESS: Final[str] = "HEALTH_002"
    HEALTH_CHECK_FAILED: Final[str] = "HEALTH_003"
    HEALTH_MESSAGE_SAVED: Final[str] = "HEALTH_004"
    HEALTH_MESSAGE_RETRIEVED: Final[str] = "HEALTH_005"

    # Database events
    DB_CONNECTION_SUCCESS: Final[str] = "DB_001"
    DB_CONNECTION_FAILED: Final[str] = "DB_002"
    DB_QUERY_ERROR: Final[str] = "DB_003"

    # Application lifecycle events
    APP_STARTUP: Final[str] = "APP_001"
    APP_SHUTDOWN: Final[str] = "APP_002"

    # Error events
    UNHANDLED_ERROR: Final[str] = "ERROR_001"
    VALIDATION_ERROR: Final[str] = "ERROR_002"


# Singleton instance
LOG_EVENTS = LogEvents()

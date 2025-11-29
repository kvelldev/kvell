"""Log event ID definitions.

Defines event IDs for structured logging.
All log calls should use these event IDs instead of raw strings.
"""

from typing import Final


class LogEvents:
    """Log event ID constants for structured logging."""

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

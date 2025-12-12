"""Internal status code definitions and log event IDs.

Defines internal status codes and their corresponding messages.
Defines event IDs for structured logging.
"""

from typing import Final

INTERNAL_STATUSES: Final[dict[int, str]] = {
    # Success
    200: "OK",
    201: "Created",
    204: "No Content",
    # Domain Errors (Client side origin / Business Logic)
    1001: "この種火は既に燃え尽きています。",  # Gone (Life expired)
    1002: "投稿に不適切な表現が含まれています。",  # NG Words (Validation)
    1003: "投稿文字数が制限を超えています。",  # Length Limit (Validation)
    1004: "薪をくべるペースが早すぎます。",  # Throttling (Rate Limit)
    1005: "指定された種火が存在しないか、消滅しています。",  # Not Found
    # Error caused by Server side (System Error)
    2001: "DBへの接続中に異常が発生しました",
    2002: "{tableName}テーブルへのクエリ中に異常が発生しました",
    500: "Internal Server Error",
}

InternalStatusCode = int


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

    # Spark events
    SPARK_POST_STARTED: Final[str] = "SPARK_001"
    SPARK_POST_SUCCESS: Final[str] = "SPARK_002"
    SPARK_POST_FAILED: Final[str] = "SPARK_003"
    SPARK_VALIDATION_FAILED: Final[str] = "SPARK_004"
    SPARK_RATE_LIMIT_EXCEEDED: Final[str] = "SPARK_005"
    SPARK_NG_WORD_DETECTED: Final[str] = "SPARK_006"

    # Fuel events
    FUEL_ADD_STARTED: Final[str] = "FUEL_001"
    FUEL_ADD_SUCCESS: Final[str] = "FUEL_002"
    FUEL_ALREADY_ADDED: Final[str] = "FUEL_003"
    FUEL_SELF_SPARK: Final[str] = "FUEL_004"
    FUEL_SPARK_NOT_FOUND: Final[str] = "FUEL_005"
    FUEL_SPARK_DECAYED: Final[str] = "FUEL_006"
    FUEL_RETRY_ATTEMPT: Final[str] = "FUEL_007"
    FUEL_RETRY_EXHAUSTED: Final[str] = "FUEL_008"

    # Timeline streaming events
    TIMELINE_SNAPSHOT_LOADED: Final[str] = "TIMELINE_001"
    TIMELINE_STREAM_STARTED: Final[str] = "TIMELINE_002"
    TIMELINE_STREAM_MESSAGE: Final[str] = "TIMELINE_003"

    # WebSocket events
    WEBSOCKET_CONNECTED: Final[str] = "WS_001"
    WEBSOCKET_DISCONNECTED: Final[str] = "WS_002"
    WEBSOCKET_ERROR: Final[str] = "WS_003"

    # PubSub events
    PUBSUB_PUBLISH_SUCCESS: Final[str] = "PUBSUB_001"
    PUBSUB_PUBLISH_ERROR: Final[str] = "PUBSUB_002"
    PUBSUB_SUBSCRIBE_SUCCESS: Final[str] = "PUBSUB_003"
    PUBSUB_MESSAGE_RECEIVED: Final[str] = "PUBSUB_004"
    PUBSUB_DESERIALIZATION_ERROR: Final[str] = "PUBSUB_005"
    PUBSUB_SUBSCRIBE_ERROR: Final[str] = "PUBSUB_006"
    PUBSUB_UNSUBSCRIBE_SUCCESS: Final[str] = "PUBSUB_007"

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

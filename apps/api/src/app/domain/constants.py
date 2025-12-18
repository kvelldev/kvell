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


# =============================================================================
# Promotion Configuration Constants
# =============================================================================

# -----------------------------------------------------------------------------
# Fixed Values (Specification-defined, not dynamically adjustable)
# -----------------------------------------------------------------------------
KINDLING_THRESHOLD_UU: Final[int] = 3  # Fixed: 3 unique users for kindling
KINDLING_DECAY_HOURS: Final[int] = 3  # TTL extension when promoted to kindling
BONFIRE_INITIAL_TTL_HOURS: Final[int] = 24  # Initial TTL for new bonfire
BONFIRE_FUEL_EXTENSION_MINUTES: Final[int] = 10  # TTL extension per fuel
BONFIRE_REPLY_EXTENSION_HOURS: Final[int] = 3  # TTL extension per reply
FUEL_WEIGHT: Final[int] = 1  # Weight for fuel in heat score
REPLY_WEIGHT: Final[int] = 5  # Weight for reply in heat score

# -----------------------------------------------------------------------------
# Fallback Values (Used when Redis is unavailable)
# -----------------------------------------------------------------------------
FALLBACK_BONFIRE_THRESHOLD_UU: Final[int] = 10  # DAU-based, fallback=10
FALLBACK_HEAT_SCORE_THRESHOLD: Final[int] = 0  # 0 until reply feature


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
    PUBSUB_BUFFER_OVERFLOW: Final[str] = "PUBSUB_008"

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

    # Bonfire/Promotion events
    PROMOTION_CHECK_STARTED: Final[str] = "PROMO_001"
    PROMOTION_TO_KINDLING: Final[str] = "PROMO_002"
    PROMOTION_TO_BONFIRE: Final[str] = "PROMO_003"
    PROMOTION_NOT_NEEDED: Final[str] = "PROMO_004"
    BONFIRE_CREATED: Final[str] = "BONFIRE_001"
    BONFIRE_EXTENDED: Final[str] = "BONFIRE_002"
    BONFIRE_DECAYED: Final[str] = "BONFIRE_003"
    BONFIRE_NOT_FOUND: Final[str] = "BONFIRE_004"

    # Threshold config events
    THRESHOLD_FETCH_SUCCESS: Final[str] = "THRESH_001"
    THRESHOLD_FETCH_FALLBACK: Final[str] = "THRESH_002"


# Singleton instance
LOG_EVENTS = LogEvents()

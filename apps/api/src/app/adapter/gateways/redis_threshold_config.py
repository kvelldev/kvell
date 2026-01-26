"""Redis implementation of Threshold Config Repository.

This module implements dynamic threshold retrieval from Redis.
Fixed configuration values should be imported from domain.constants.
"""

from redis.asyncio import Redis
from redis.exceptions import RedisError

from app.domain.constants import (
    FALLBACK_BONFIRE_THRESHOLD_UU,
    FALLBACK_HEAT_SCORE_THRESHOLD,
    LOG_EVENTS,
)
from app.domain.repository.threshold_config_repository import IThresholdConfigRepository
from app.usecase.ports.logger import ILogger


class RedisThresholdConfigRepository(IThresholdConfigRepository):
    """Redis implementation of threshold config repository.

    Only dynamic thresholds are retrieved from Redis.
    Fixed values should be imported directly from domain.constants.

    Redis Keys:
    - config:threshold:bonfire_uu - DAU-based bonfire UU threshold
    - config:threshold:heat_score - Heat score threshold (future use)
    """

    # Redis key constants
    KEY_BONFIRE_UU = "config:threshold:bonfire_uu"
    KEY_HEAT_SCORE = "config:threshold:heat_score"

    def __init__(self, redis: Redis, logger: ILogger) -> None:  # type: ignore[type-arg]
        """Initialize the repository.

        Args:
            redis: Redis client instance
            logger: Logger for structured logging

        """
        self.redis = redis
        self.logger = logger

    async def get_bonfire_threshold_uu(self) -> int:
        """Get the current bonfire promotion threshold (unique users).

        This value is dynamically calculated based on DAU by a daily batch.
        Falls back to FALLBACK_BONFIRE_THRESHOLD_UU if Redis unavailable.

        Returns:
            Unique user threshold for bonfire promotion (10-50)

        """
        return await self._get_int_value(
            self.KEY_BONFIRE_UU,
            FALLBACK_BONFIRE_THRESHOLD_UU,
        )

    async def get_heat_score_threshold(self) -> int:
        """Get the heat score threshold for bonfire promotion.

        Currently returns 0 (until reply feature is implemented).
        May become dynamic in the future.

        Returns:
            Heat score threshold (currently 0)

        """
        return await self._get_int_value(
            self.KEY_HEAT_SCORE,
            FALLBACK_HEAT_SCORE_THRESHOLD,
        )

    async def _get_int_value(self, key: str, default: int) -> int:
        """Get integer value from Redis with fallback.

        Args:
            key: Redis key
            default: Fallback value if key missing or Redis unavailable

        Returns:
            Integer value from Redis or default

        """
        try:
            value = await self.redis.get(key)

            if value is None:
                self.logger.info(
                    LOG_EVENTS.THRESHOLD_FETCH_FALLBACK,
                    f"Threshold key not found, using fallback: {key}",
                    context={"key": key, "default": default},
                )
                return default

            self.logger.info(
                LOG_EVENTS.THRESHOLD_FETCH_SUCCESS,
                f"Threshold fetched from Redis: {key}",
                context={"key": key, "value": int(value)},
            )
            return int(value)

        except (RedisError, ValueError) as e:
            self.logger.warning(
                LOG_EVENTS.THRESHOLD_FETCH_FALLBACK,
                f"Failed to fetch threshold, using fallback: {key}",
                context={
                    "key": key,
                    "default": default,
                    "error": str(e),
                },
            )
            return default

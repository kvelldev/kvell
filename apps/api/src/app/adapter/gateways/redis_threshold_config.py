"""Redis implementation of Threshold Config Repository.

This module implements threshold configuration retrieval from Redis.
"""

from redis.asyncio import Redis
from redis.exceptions import RedisError

from app.domain.constants import LOG_EVENTS
from app.domain.repository.threshold_config_repository import IThresholdConfigRepository
from app.usecase.ports.logger import ILogger


class RedisThresholdConfigRepository(IThresholdConfigRepository):
    """Redis implementation of threshold config repository.

    Thresholds are stored in Redis and updated by a daily batch process.
    This implementation provides fallback values when Redis is unavailable.

    Redis Keys:
    - config:threshold:bonfire_uu - Dynamic bonfire UU threshold
    - config:threshold:kindling_uu - Kindling UU threshold (usually fixed)
    - config:threshold:heat_score - Heat score threshold
    - config:decay:kindling_hours - Kindling TTL extension hours
    - config:decay:bonfire_fuel_minutes - Bonfire fuel extension minutes
    - config:decay:bonfire_reply_hours - Bonfire reply extension hours
    """

    # Redis key constants
    KEY_BONFIRE_UU = "config:threshold:bonfire_uu"
    KEY_KINDLING_UU = "config:threshold:kindling_uu"
    KEY_HEAT_SCORE = "config:threshold:heat_score"
    KEY_KINDLING_DECAY_HOURS = "config:decay:kindling_hours"
    KEY_BONFIRE_FUEL_MINUTES = "config:decay:bonfire_fuel_minutes"
    KEY_BONFIRE_REPLY_HOURS = "config:decay:bonfire_reply_hours"
    KEY_FUEL_WEIGHT = "config:weight:fuel"
    KEY_REPLY_WEIGHT = "config:weight:reply"

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

        This value is dynamically calculated based on DAU.
        Falls back to DEFAULT_BONFIRE_THRESHOLD_UU if Redis unavailable.

        Returns:
            Unique user threshold for bonfire promotion (10-50)

        """
        return await self._get_int_value(
            self.KEY_BONFIRE_UU,
            self.DEFAULT_BONFIRE_THRESHOLD_UU,
        )

    async def get_kindling_threshold_uu(self) -> int:
        """Get the kindling promotion threshold (unique users).

        This is typically a fixed value (not DAU-dependent).

        Returns:
            Unique user threshold for kindling (default: 3)

        """
        return await self._get_int_value(
            self.KEY_KINDLING_UU,
            self.DEFAULT_KINDLING_THRESHOLD_UU,
        )

    async def get_heat_score_threshold(self) -> int:
        """Get the heat score threshold for bonfire promotion.

        Returns:
            Heat score threshold (default: 50)

        """
        return await self._get_int_value(
            self.KEY_HEAT_SCORE,
            self.DEFAULT_HEAT_SCORE_THRESHOLD,
        )

    async def get_kindling_decay_hours(self) -> int:
        """Get the TTL extension hours for kindling.

        Returns:
            Hours to extend TTL when promoted to kindling (default: 3)

        """
        return await self._get_int_value(
            self.KEY_KINDLING_DECAY_HOURS,
            self.DEFAULT_KINDLING_DECAY_HOURS,
        )

    async def get_bonfire_fuel_extension_minutes(self) -> int:
        """Get the TTL extension minutes for fuel on bonfire.

        Returns:
            Minutes to extend TTL when fuel is added (default: 10)

        """
        return await self._get_int_value(
            self.KEY_BONFIRE_FUEL_MINUTES,
            self.DEFAULT_BONFIRE_FUEL_EXTENSION_MINUTES,
        )

    async def get_bonfire_reply_extension_hours(self) -> int:
        """Get the TTL extension hours for reply on bonfire.

        Returns:
            Hours to extend TTL when reply is added (default: 3)

        """
        return await self._get_int_value(
            self.KEY_BONFIRE_REPLY_HOURS,
            self.DEFAULT_BONFIRE_REPLY_EXTENSION_HOURS,
        )

    async def get_fuel_weight(self) -> int:
        """Get the weight for fuel actions in heat score calculation.

        Returns:
            Weight for fuel actions (default: 1)

        """
        return await self._get_int_value(
            self.KEY_FUEL_WEIGHT,
            self.DEFAULT_FUEL_WEIGHT,
        )

    async def get_reply_weight(self) -> int:
        """Get the weight for reply actions in heat score calculation.

        Returns:
            Weight for reply actions (default: 5)

        """
        return await self._get_int_value(
            self.KEY_REPLY_WEIGHT,
            self.DEFAULT_REPLY_WEIGHT,
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
                    f"Threshold key not found, using default: {key}",
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

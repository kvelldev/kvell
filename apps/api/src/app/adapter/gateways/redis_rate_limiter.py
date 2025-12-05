"""Redis implementation of Rate Limiter.

This module implements rate limiting using Redis Fixed Window Counter algorithm.
"""

from redis.asyncio import Redis

from app.domain.service.rate_limiter import IRateLimiter


class RedisRateLimiter(IRateLimiter):
    """Redis-based rate limiter using Fixed Window Counter algorithm."""

    def __init__(self, redis: Redis) -> None:  # type: ignore[type-arg]
        """Initialize the rate limiter.

        Args:
            redis: Redis client instance

        """
        self.redis = redis

    async def check_and_increment(
        self,
        user_hash: str,
        limit: int,
        window_seconds: int,
    ) -> bool:
        """Check if user is within rate limit and increment counter.

        Uses Redis atomic operations (INCR + EXPIRE) to ensure consistency.

        Args:
            user_hash: User identifier for rate limiting
            limit: Maximum allowed count within window
            window_seconds: Time window in seconds

        Returns:
            True if within limit (incremented), False if exceeded

        """
        key = f"ratelimit:spark:{user_hash}"

        # Atomic increment
        current = await self.redis.incr(key)

        # Set expiration on first increment
        if current == 1:
            await self.redis.expire(key, window_seconds)

        # Check if within limit
        return current <= limit

    async def get_current_count(self, user_hash: str) -> int:
        """Get current count for user.

        Args:
            user_hash: User identifier

        Returns:
            Current count (0 if no record exists)

        """
        key = f"ratelimit:spark:{user_hash}"
        count = await self.redis.get(key)

        if count is None:
            return 0

        return int(count)

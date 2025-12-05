"""Redis configuration and connection management.

This module manages Redis connection using redis-py.
"""

from redis.asyncio import Redis

from app.adapter.infra.settings import settings


class RedisClient:
    """Redis client connection manager."""

    client: Redis | None = None

    @classmethod
    async def connect(cls) -> None:
        """Establish connection to Redis."""
        # Parse redis_uri manually to avoid from_url type issues
        # Format: redis://host:port
        uri = settings.redis_uri.replace("redis://", "")
        if ":" in uri:
            host, port_str = uri.split(":", 1)
            port = int(port_str)
        else:
            host = uri
            port = 6379

        cls.client = Redis(host=host, port=port, decode_responses=True)

    @classmethod
    async def disconnect(cls) -> None:
        """Close connection to Redis."""
        if cls.client:
            await cls.client.aclose()

    @classmethod
    def get_client(cls) -> Redis:  # type: ignore[type-arg]
        """Get the Redis client instance.

        Returns:
            Redis client instance

        Raises:
            RuntimeError: If Redis is not connected

        """
        if cls.client is None:
            msg = "Redis not connected. Call connect() first."
            raise RuntimeError(msg)
        return cls.client

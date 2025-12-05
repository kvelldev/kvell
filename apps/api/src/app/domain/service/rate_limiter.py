"""Rate Limiter Interface.

This module defines the interface for rate limiting functionality.
"""

from abc import ABC, abstractmethod


class IRateLimiter(ABC):
    """Interface for rate limiting operations."""

    @abstractmethod
    async def check_and_increment(
        self,
        user_hash: str,
        limit: int,
        window_seconds: int,
    ) -> bool:
        """Check if user is within rate limit and increment counter.

        Args:
            user_hash: User identifier for rate limiting
            limit: Maximum allowed count within window
            window_seconds: Time window in seconds

        Returns:
            True if within limit (incremented), False if exceeded

        """

    @abstractmethod
    async def get_current_count(self, user_hash: str) -> int:
        """Get current count for user.

        Args:
            user_hash: User identifier

        Returns:
            Current count (0 if no record exists)

        """

"""Spark Repository Interface.

This module defines the output port for spark persistence.
"""

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator

from app.domain.model.spark import Spark


class ISparkRepository(ABC):
    """Repository interface for spark operations."""

    @abstractmethod
    async def save(self, spark: Spark) -> Spark:
        """Save a spark.

        Args:
            spark: The spark to save

        Returns:
            The saved spark

        """

    @abstractmethod
    async def find_by_id(self, spark_id: str) -> Spark | None:
        """Find a spark by ID.

        Args:
            spark_id: The spark ID to search for

        Returns:
            The spark if found, None otherwise

        """

    @abstractmethod
    async def find_active_sparks(self, seconds: int) -> AsyncIterator[Spark]:
        """Find all active sparks created within the specified seconds.

        Args:
            seconds: Number of seconds to look back from now

        Yields:
            Active sparks sorted by created_at in ascending order (oldest first)

        """
        if False:  # pragma: no cover
            yield  # type: ignore[misc,unreachable]
        raise NotImplementedError

    @abstractmethod
    async def try_add_fuel(self, spark_id: str, user_hash: str) -> bool:
        """Atomically add fuel to a spark if the user hasn't fueled it yet.

        This method ensures idempotency by checking if the user has already
        added fuel to this spark. If not, it increments the fuel_count and
        records the user's action.

        Args:
            spark_id: The spark ID to add fuel to
            user_hash: The user hash attempting to add fuel

        Returns:
            True if fuel was added (first time), False if user already fueled

        """

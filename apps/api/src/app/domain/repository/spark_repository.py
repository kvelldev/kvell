"""Spark Repository Interface.

This module defines the output port for spark persistence.
"""

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from datetime import datetime

from app.domain.model.spark import Spark, SparkLevel
from app.domain.model.spark_engagement import SparkEngagement


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
    async def find_active_sparks(
        self,
        seconds: int,
        limit: int = 1000,
    ) -> AsyncIterator[Spark]:
        """Find all active sparks created within the specified seconds.

        Args:
            seconds: Number of seconds to look back from now
            limit: Maximum number of sparks to return (default 1000)

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

    @abstractmethod
    async def get_engagement(
        self,
        spark_id: str,
        fuel_weight: int = 1,
        reply_weight: int = 5,
    ) -> SparkEngagement | None:
        """Get engagement metrics for a spark.

        Calculates unique user count and fuel count from fuel history.

        Args:
            spark_id: The spark ID to get engagement for
            fuel_weight: Weight for fuel actions in heat score calculation
            reply_weight: Weight for reply actions in heat score calculation

        Returns:
            SparkEngagement if spark exists, None otherwise

        """

    @abstractmethod
    async def update_level(self, spark_id: str, level: SparkLevel) -> bool:
        """Update spark's promotion level.

        Args:
            spark_id: The spark ID to update
            level: New spark level

        Returns:
            True if updated successfully, False if spark not found

        """

    @abstractmethod
    async def update_decay_at(
        self,
        spark_id: str,
        new_decay_at: datetime,
    ) -> bool:
        """Update spark's decay_at timestamp.

        Used when promoting to kindling (TTL extension).

        Args:
            spark_id: The spark ID to update
            new_decay_at: New decay timestamp

        Returns:
            True if updated successfully, False if spark not found

        """

    @abstractmethod
    async def find_replies_by_bonfire_id(
        self,
        bonfire_id: str,
        limit: int = 1000,
    ) -> AsyncIterator[Spark]:
        """Find all replies for a specific bonfire.

        Args:
            bonfire_id: The parent bonfire ID
            limit: Maximum number of replies to return (default 1000)

        Yields:
            Reply sparks sorted by created_at in ascending order (oldest first)

        """
        if False:  # pragma: no cover
            yield  # type: ignore[misc,unreachable]
        raise NotImplementedError

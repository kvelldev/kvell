"""Spark Repository Interface.

This module defines the output port for spark persistence.
"""

from abc import ABC, abstractmethod

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

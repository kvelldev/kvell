"""Bonfire Repository Interface.

This module defines the output port for bonfire persistence.
"""

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from datetime import datetime

from app.domain.model.bonfire import Bonfire


class IBonfireRepository(ABC):
    """Repository interface for bonfire operations."""

    @abstractmethod
    async def save(self, bonfire: Bonfire) -> Bonfire:
        """Save a bonfire.

        Args:
            bonfire: The bonfire to save

        Returns:
            The saved bonfire

        """

    @abstractmethod
    async def find_by_id(self, bonfire_id: str) -> Bonfire | None:
        """Find a bonfire by ID.

        Args:
            bonfire_id: The bonfire ID to search for

        Returns:
            The bonfire if found, None otherwise

        """

    @abstractmethod
    async def find_by_spark_id(self, spark_id: str) -> Bonfire | None:
        """Find a bonfire by its original spark ID.

        Args:
            spark_id: The original spark ID

        Returns:
            The bonfire if found, None otherwise

        """

    @abstractmethod
    async def find_active_bonfires(self) -> AsyncIterator[Bonfire]:
        """Find all active (non-decayed) bonfires.

        Yields:
            Active bonfires sorted by created_at descending (newest first)

        """
        if False:  # pragma: no cover
            yield  # type: ignore[misc,unreachable]
        raise NotImplementedError

    @abstractmethod
    async def update_decay_at(
        self,
        bonfire_id: str,
        new_decay_at: datetime,
    ) -> bool:
        """Update bonfire's decay_at timestamp.

        Uses atomic update to prevent race conditions.

        Args:
            bonfire_id: The bonfire ID to update
            new_decay_at: New decay timestamp

        Returns:
            True if updated successfully, False if bonfire not found

        """

    @abstractmethod
    async def delete_by_id(self, bonfire_id: str) -> bool:
        """Delete a bonfire by ID.

        Used when bonfire decays.

        Args:
            bonfire_id: The bonfire ID to delete

        Returns:
            True if deleted successfully, False if not found

        """

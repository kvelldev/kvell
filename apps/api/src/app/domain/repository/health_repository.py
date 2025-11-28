"""Health Repository Interface.

This module defines the output port for health message persistence.
"""

from abc import ABC, abstractmethod

from domain.model.health_message import HealthMessage


class IHealthRepository(ABC):
    """Repository interface for health messages."""

    @abstractmethod
    async def save(self, message: HealthMessage) -> HealthMessage:
        """Save a health message.

        Args:
            message: The health message to save

        Returns:
            The saved health message

        """

    @abstractmethod
    async def find_latest(self) -> HealthMessage | None:
        """Find the latest health message.

        Returns:
            The latest health message, or None if not found

        """

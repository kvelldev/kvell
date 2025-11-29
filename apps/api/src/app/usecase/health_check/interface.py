"""Health Check UseCase Interface.

This module defines the input port for health check operations.
"""

from abc import ABC, abstractmethod

from app.usecase.dto.health_dto import HealthOutput, SaveHealthInput


class IHealthCheckUseCase(ABC):
    """UseCase interface for health check operations."""

    @abstractmethod
    async def save_message(self, input_data: SaveHealthInput) -> HealthOutput:
        """Save a health check message.

        Args:
            input_data: Input data containing the message

        Returns:
            The saved message details

        """

    @abstractmethod
    async def get_latest_message(self) -> HealthOutput | None:
        """Get the latest health check message.

        Returns:
            The latest message, or None if not found

        """

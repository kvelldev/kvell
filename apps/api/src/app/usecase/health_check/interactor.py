"""Health Check UseCase Implementation.

This module implements the health check use case logic.
"""

import uuid

from domain.model.health_message import HealthMessage
from domain.repository.health_repository import IHealthRepository

from usecase.dto.health_dto import HealthOutput, SaveHealthInput
from usecase.health_check.interface import IHealthCheckUseCase


class HealthCheckInteractor(IHealthCheckUseCase):
    """Interactor for health check operations."""

    def __init__(self, health_repository: IHealthRepository) -> None:
        """Initialize the interactor.

        Args:
            health_repository: Repository for health message persistence

        """
        self.health_repository = health_repository

    async def save_message(self, input_data: SaveHealthInput) -> HealthOutput:
        """Save a health check message.

        Args:
            input_data: Input data containing the message

        Returns:
            The saved message details

        """
        # Create entity
        health_message = HealthMessage(
            id=str(uuid.uuid4()),
            message=input_data.message,
        )

        # Save via repository
        saved_message = await self.health_repository.save(health_message)

        # Map to output DTO
        return HealthOutput(
            id=saved_message.id,
            message=saved_message.message,
            created_at=saved_message.created_at.isoformat(),
        )

    async def get_latest_message(self) -> HealthOutput | None:
        """Get the latest health check message.

        Returns:
            The latest message, or None if not found

        """
        message = await self.health_repository.find_latest()

        if message is None:
            return None

        return HealthOutput(
            id=message.id,
            message=message.message,
            created_at=message.created_at.isoformat(),
        )

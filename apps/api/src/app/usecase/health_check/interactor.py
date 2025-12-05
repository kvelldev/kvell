"""Health Check UseCase Implementation.

This module implements the health check use case logic.
"""

import uuid

from app.domain.constants import LOG_EVENTS
from app.domain.model.health_message import HealthMessage
from app.domain.repository.health_repository import IHealthRepository
from app.usecase.dto.health_dto import HealthOutput, SaveHealthInput
from app.usecase.health_check.interface import IHealthCheckUseCase
from app.usecase.ports.logger import ILogger


class HealthCheckInteractor(IHealthCheckUseCase):
    """Interactor for health check operations."""

    def __init__(self, health_repository: IHealthRepository, logger: ILogger) -> None:
        """Initialize the interactor.

        Args:
            health_repository: Repository for health message persistence
            logger: Logger for structured logging

        """
        self.health_repository = health_repository
        self.logger = logger

    async def save_message(self, input_data: SaveHealthInput) -> HealthOutput:
        """Save a health check message.

        Args:
            input_data: Input data containing the message

        Returns:
            The saved message details

        """
        self.logger.info(
            LOG_EVENTS.HEALTH_MESSAGE_SAVED,
            "Creating health message entity",
            context={"message": input_data.message},
        )

        # Create entity
        health_message = HealthMessage(
            id=str(uuid.uuid4()),
            message=input_data.message,
        )

        # Save via repository
        saved_message = await self.health_repository.save(health_message)

        self.logger.info(
            LOG_EVENTS.HEALTH_MESSAGE_SAVED,
            "Health message saved successfully",
            context={"message_id": saved_message.id},
        )

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
        self.logger.info(
            LOG_EVENTS.HEALTH_MESSAGE_RETRIEVED,
            "Fetching latest health message",
        )

        message = await self.health_repository.find_latest()

        if message is None:
            self.logger.info(
                LOG_EVENTS.HEALTH_MESSAGE_RETRIEVED,
                "No health message found",
            )
            return None

        self.logger.info(
            LOG_EVENTS.HEALTH_MESSAGE_RETRIEVED,
            "Latest health message retrieved",
            context={"message_id": message.id},
        )

        return HealthOutput(
            id=message.id,
            message=message.message,
            created_at=message.created_at.isoformat(),
        )

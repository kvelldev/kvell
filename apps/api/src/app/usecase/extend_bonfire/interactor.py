"""Extend Bonfire Interactor.

This module implements the business logic for extending bonfire TTL.
"""

from datetime import UTC, datetime

from app.domain.constants import (
    BONFIRE_FUEL_EXTENSION_MINUTES,
    BONFIRE_REPLY_EXTENSION_HOURS,
    LOG_EVENTS,
)
from app.domain.exception import AppError
from app.domain.repository.bonfire_repository import IBonfireRepository
from app.usecase.extend_bonfire.interface import (
    ExtendBonfireInput,
    ExtendBonfireOutput,
    ExtensionType,
    IExtendBonfireUseCase,
)
from app.usecase.ports.logger import ILogger
from app.usecase.ports.pubsub import IPubSubGateway


class ExtendBonfireInteractor(IExtendBonfireUseCase):
    """Interactor for extending bonfire TTL."""

    def __init__(
        self,
        bonfire_repository: IBonfireRepository,
        pubsub: IPubSubGateway,
        logger: ILogger,
    ) -> None:
        """Initialize the interactor.

        Args:
            bonfire_repository: Repository for bonfire operations
            pubsub: PubSub gateway for broadcasting events
            logger: Logger for structured logging

        """
        self.bonfire_repository = bonfire_repository
        self.pubsub = pubsub
        self.logger = logger

    async def execute(self, input_data: ExtendBonfireInput) -> ExtendBonfireOutput:
        """Extend bonfire TTL.

        Extension Rules:
        - Fuel: Adds fixed minutes to current decay_at
        - Reply: Sets decay_at to now + extension_hours if remaining TTL is shorter

        Args:
            input_data: Input containing bonfire_id and extension_type

        Returns:
            Output indicating extension result

        Raises:
            AppError: If bonfire not found (1005)

        """
        # 1. Find the bonfire
        bonfire = await self.bonfire_repository.find_by_id(input_data.bonfire_id)
        if bonfire is None:
            self.logger.warning(
                LOG_EVENTS.BONFIRE_NOT_FOUND,
                "Bonfire not found for extension",
                context={"bonfire_id": input_data.bonfire_id},
            )
            raise AppError(internal_code=1005)

        previous_decay_at = bonfire.decay_at

        # 2. Calculate new decay_at based on extension type
        if input_data.extension_type == ExtensionType.FUEL:
            extended_bonfire = bonfire.extend_by_fuel(BONFIRE_FUEL_EXTENSION_MINUTES)
        else:  # REPLY
            extended_bonfire = bonfire.extend_by_reply(BONFIRE_REPLY_EXTENSION_HOURS)

        new_decay_at = extended_bonfire.decay_at
        was_extended = new_decay_at != previous_decay_at

        # 3. Update in repository if extended
        if was_extended:
            await self.bonfire_repository.update_decay_at(
                input_data.bonfire_id,
                new_decay_at,
            )

            self.logger.info(
                LOG_EVENTS.BONFIRE_EXTENDED,
                "Bonfire TTL extended",
                context={
                    "bonfire_id": input_data.bonfire_id,
                    "extension_type": input_data.extension_type.value,
                    "previous_decay_at": previous_decay_at.isoformat(),
                    "new_decay_at": new_decay_at.isoformat(),
                },
            )

            # 4. Broadcast extension event
            await self._broadcast_extension(
                bonfire_id=input_data.bonfire_id,
                new_decay_at=new_decay_at,
            )
        else:
            self.logger.info(
                LOG_EVENTS.BONFIRE_EXTENDED,
                "Bonfire TTL not extended (remaining TTL longer)",
                context={
                    "bonfire_id": input_data.bonfire_id,
                    "extension_type": input_data.extension_type.value,
                },
            )

        return ExtendBonfireOutput(
            bonfire_id=input_data.bonfire_id,
            extended=was_extended,
            previous_decay_at=previous_decay_at,
            new_decay_at=new_decay_at,
        )

    async def _broadcast_extension(
        self,
        bonfire_id: str,
        new_decay_at: datetime,
    ) -> None:
        """Broadcast bonfire extension event via PubSub.

        Args:
            bonfire_id: ID of the extended bonfire
            new_decay_at: New decay timestamp

        """
        event_data = {
            "type": "bonfire_extended",
            "bonfire_id": bonfire_id,
            "new_decay_at": new_decay_at.isoformat(),
            "timestamp": datetime.now(UTC).isoformat(),
        }

        await self.pubsub.publish("bonfire_events", event_data)

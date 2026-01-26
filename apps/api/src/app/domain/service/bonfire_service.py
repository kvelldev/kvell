"""Bonfire Domain Service.

This module provides domain operations for bonfires that can be used
by multiple use cases (e.g., AddFuel, Reply).
"""

from datetime import UTC, datetime

from app.domain.constants import (
    BONFIRE_FUEL_EXTENSION_MINUTES,
    BONFIRE_REPLY_EXTENSION_HOURS,
)
from app.domain.model.bonfire import Bonfire
from app.domain.repository.bonfire_repository import IBonfireRepository


class BonfireService:
    """Domain service for bonfire operations.

    This service encapsulates bonfire extension logic that is shared
    across multiple use cases (e.g., add_fuel, reply).
    """

    def __init__(
        self,
        bonfire_repository: IBonfireRepository,
    ) -> None:
        """Initialize the service.

        Args:
            bonfire_repository: Repository for bonfire operations

        """
        self.bonfire_repository = bonfire_repository

    async def extend_by_fuel(self, bonfire: Bonfire) -> tuple[Bonfire, bool]:
        """Extend bonfire TTL by fuel action.

        Args:
            bonfire: The bonfire to extend

        Returns:
            Tuple of (extended bonfire, whether extension occurred)

        """
        extended_bonfire = bonfire.extend_by_fuel(BONFIRE_FUEL_EXTENSION_MINUTES)
        was_extended = extended_bonfire.decay_at != bonfire.decay_at

        if was_extended:
            await self.bonfire_repository.update_decay_at(
                bonfire.id,
                extended_bonfire.decay_at,
            )

        return extended_bonfire, was_extended

    async def extend_by_reply(
        self,
        bonfire: Bonfire,
        current_time: datetime | None = None,
    ) -> tuple[Bonfire, bool]:
        """Extend bonfire TTL by reply action.

        Args:
            bonfire: The bonfire to extend
            current_time: Current time for calculation (defaults to now)

        Returns:
            Tuple of (extended bonfire, whether extension occurred)

        """
        if current_time is None:
            current_time = datetime.now(UTC)

        extended_bonfire = bonfire.extend_by_reply(
            BONFIRE_REPLY_EXTENSION_HOURS,
            current_time,
        )
        was_extended = extended_bonfire.decay_at != bonfire.decay_at

        if was_extended:
            await self.bonfire_repository.update_decay_at(
                bonfire.id,
                extended_bonfire.decay_at,
            )

        return extended_bonfire, was_extended

    async def find_by_spark_id(self, spark_id: str) -> Bonfire | None:
        """Find bonfire by original spark ID.

        Args:
            spark_id: ID of the original spark

        Returns:
            Bonfire if found, None otherwise

        """
        return await self.bonfire_repository.find_by_spark_id(spark_id)

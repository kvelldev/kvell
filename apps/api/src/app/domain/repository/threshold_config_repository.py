"""Threshold Config Repository Interface.

This module defines the output port for dynamic threshold retrieval from Redis.
Fixed configuration values are defined in domain.constants module.
"""

from abc import ABC, abstractmethod


class IThresholdConfigRepository(ABC):
    """Repository interface for dynamic threshold configuration.

    Only values that need dynamic adjustment (via Redis) are retrieved here.
    Fixed specification values should be imported from domain.constants.

    Dynamic values (retrieved via this repository):
    - Bonfire UU threshold: DAU-based calculation, updated by daily batch
    - Heat score threshold: May be adjusted in future (currently 0)

    Fixed values (use constants.py directly):
    - KINDLING_THRESHOLD_UU, KINDLING_DECAY_HOURS
    - BONFIRE_FUEL_EXTENSION_MINUTES, BONFIRE_REPLY_EXTENSION_HOURS
    - FUEL_WEIGHT, REPLY_WEIGHT
    """

    @abstractmethod
    async def get_bonfire_threshold_uu(self) -> int:
        """Get the current bonfire promotion threshold (unique users).

        This value is dynamically calculated based on DAU.
        Formula: Clamp(floor(DAU_7day_avg * 0.05), 10, 50)

        Returns:
            Unique user threshold for bonfire promotion (10-50)

        """

    @abstractmethod
    async def get_heat_score_threshold(self) -> int:
        """Get the heat score threshold for bonfire promotion.

        Currently fixed at 0 (until reply feature is implemented).
        May become dynamic in the future.

        Returns:
            Heat score threshold (currently 0)

        """

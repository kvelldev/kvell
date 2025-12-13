"""Threshold Config Repository Interface.

This module defines the output port for threshold configuration retrieval.
"""

from abc import ABC, abstractmethod


class IThresholdConfigRepository(ABC):
    """Repository interface for threshold configuration.

    Thresholds are stored in Redis and updated daily by a batch process.
    This interface provides fallback values when Redis is unavailable.
    """

    # Fallback values (used when Redis is unavailable)
    DEFAULT_BONFIRE_THRESHOLD_UU: int = 10
    DEFAULT_KINDLING_THRESHOLD_UU: int = 3
    DEFAULT_HEAT_SCORE_THRESHOLD: int = 50

    # Extension durations
    DEFAULT_KINDLING_DECAY_HOURS: int = 3
    DEFAULT_BONFIRE_FUEL_EXTENSION_MINUTES: int = 10
    DEFAULT_BONFIRE_REPLY_EXTENSION_HOURS: int = 3

    # Heat score weights
    DEFAULT_FUEL_WEIGHT: int = 1
    DEFAULT_REPLY_WEIGHT: int = 5

    @abstractmethod
    async def get_bonfire_threshold_uu(self) -> int:
        """Get the current bonfire promotion threshold (unique users).

        This value is dynamically calculated based on DAU.
        Formula: Clamp(floor(DAU_7day_avg * 0.05), 10, 50)

        Returns:
            Unique user threshold for bonfire promotion (10-50)

        """

    @abstractmethod
    async def get_kindling_threshold_uu(self) -> int:
        """Get the kindling promotion threshold (unique users).

        This is a fixed value (not DAU-dependent).

        Returns:
            Unique user threshold for kindling (default: 3)

        """

    @abstractmethod
    async def get_heat_score_threshold(self) -> int:
        """Get the heat score threshold for bonfire promotion.

        Returns:
            Heat score threshold (default: 50)

        """

    @abstractmethod
    async def get_kindling_decay_hours(self) -> int:
        """Get the TTL extension hours for kindling.

        Returns:
            Hours to extend TTL when promoted to kindling (default: 3)

        """

    @abstractmethod
    async def get_bonfire_fuel_extension_minutes(self) -> int:
        """Get the TTL extension minutes for fuel on bonfire.

        Returns:
            Minutes to extend TTL when fuel is added (default: 10)

        """

    @abstractmethod
    async def get_bonfire_reply_extension_hours(self) -> int:
        """Get the TTL extension hours for reply on bonfire.

        Returns:
            Hours to extend TTL when reply is added (default: 3)

        """

    @abstractmethod
    async def get_fuel_weight(self) -> int:
        """Get the weight for fuel actions in heat score calculation.

        Returns:
            Weight for fuel actions (default: 1)

        """

    @abstractmethod
    async def get_reply_weight(self) -> int:
        """Get the weight for reply actions in heat score calculation.

        Returns:
            Weight for reply actions (default: 5)

        """

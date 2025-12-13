"""Extend Bonfire UseCase Interface.

This module defines the interface and DTOs for extending bonfire TTL.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class ExtensionType(str, Enum):
    """Type of action that triggers extension."""

    FUEL = "fuel"  # Extends by fixed minutes from current decay_at
    REPLY = "reply"  # Extends from now if remaining TTL is shorter


class ExtendBonfireInput(BaseModel):
    """Input for extend bonfire use case."""

    bonfire_id: str = Field(..., description="ID of the bonfire to extend")
    extension_type: ExtensionType = Field(
        ...,
        description="Type of action triggering the extension",
    )


class ExtendBonfireOutput(BaseModel):
    """Output of extend bonfire use case."""

    bonfire_id: str = Field(..., description="ID of the bonfire")
    extended: bool = Field(..., description="Whether TTL was extended")
    previous_decay_at: datetime = Field(..., description="Previous decay timestamp")
    new_decay_at: datetime = Field(..., description="New decay timestamp")


class IExtendBonfireUseCase(ABC):
    """Interface for extend bonfire use case.

    Extends bonfire TTL based on user actions (fuel or reply).

    Extension Rules:
    - Fuel: Adds fixed minutes to current decay_at
    - Reply: Sets decay_at to now + extension_hours if remaining TTL is shorter
    """

    @abstractmethod
    async def execute(self, input_data: ExtendBonfireInput) -> ExtendBonfireOutput:
        """Extend bonfire TTL.

        Args:
            input_data: Input containing bonfire_id and extension_type

        Returns:
            Output indicating extension result

        Raises:
            AppError: If bonfire not found (1005)

        """

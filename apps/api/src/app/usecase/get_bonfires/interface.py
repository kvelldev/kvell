"""Get Active Bonfires UseCase Interface.

This module defines the interface and DTOs for retrieving active bonfires.
"""

from abc import ABC, abstractmethod
from datetime import datetime

from pydantic import BaseModel, Field


class BonfireDTO(BaseModel):
    """Data transfer object for bonfire."""

    id: str = Field(..., description="Bonfire ID")
    spark_id: str = Field(..., description="Original spark ID")
    content: str = Field(..., description="Bonfire content")
    unique_user_count: int = Field(..., description="Number of unique users")
    heat_score: int = Field(..., description="Heat score")
    created_at: datetime = Field(..., description="Creation timestamp")
    decay_at: datetime = Field(..., description="Decay timestamp")


class GetActiveBonfiresOutput(BaseModel):
    """Output of get active bonfires use case."""

    bonfires: list["BonfireDTO"] = Field(
        default_factory=lambda: [],
        description="List of active bonfires",
    )
    count: int = Field(default=0, description="Number of active bonfires")


class IGetActiveBonfiresUseCase(ABC):
    """Interface for get active bonfires use case.

    Returns all currently active (non-decayed) bonfires.
    """

    @abstractmethod
    async def execute(self) -> GetActiveBonfiresOutput:
        """Get all active bonfires.

        Returns:
            Output containing list of active bonfires

        """

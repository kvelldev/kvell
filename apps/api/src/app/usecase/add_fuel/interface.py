"""Add Fuel UseCase Interface.

This module defines the input port for adding fuel to a spark.
"""

from abc import ABC, abstractmethod

from pydantic import BaseModel, Field

from app.domain.model.spark import SparkLevel


class AddFuelInput(BaseModel):
    """Input DTO for adding fuel to a spark."""

    spark_id: str = Field(..., description="The spark ID to add fuel to")
    user_hash: str = Field(..., description="The user hash adding fuel")


class AddFuelOutput(BaseModel):
    """Output DTO for add fuel operation.

    Note: This intentionally does NOT include fuel_count to prevent
    displaying quantitative metrics to users (per project requirements).
    """

    success: bool = Field(
        default=True,
        description="Always true - indicates the action was acknowledged",
    )
    promoted: bool = Field(
        default=False,
        description="Whether this action triggered a promotion",
    )
    previous_level: SparkLevel | None = Field(
        default=None,
        description="Level before this action (if promoted)",
    )
    current_level: SparkLevel | None = Field(
        default=None,
        description="Level after this action (if promoted)",
    )
    bonfire_created: bool = Field(
        default=False,
        description="Whether a new bonfire was created by this action",
    )


class IAddFuelUseCase(ABC):
    """UseCase interface for adding fuel to a spark."""

    @abstractmethod
    async def execute(self, input_data: AddFuelInput) -> AddFuelOutput:
        """Add fuel to a spark.

        Args:
            input_data: Input data containing spark_id and user_hash

        Returns:
            Output indicating success (without revealing fuel count)

        Raises:
            AppError: If spark not found (1005) or already decayed (1001)

        """

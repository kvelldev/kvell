"""Check Promotion UseCase Interface.

This module defines the interface and DTOs for spark promotion checking.
"""

from abc import ABC, abstractmethod

from pydantic import BaseModel, Field

from app.domain.model.spark import SparkLevel


class CheckPromotionInput(BaseModel):
    """Input for check promotion use case."""

    spark_id: str = Field(..., description="ID of the spark to check")


class CheckPromotionOutput(BaseModel):
    """Output of check promotion use case."""

    spark_id: str = Field(..., description="ID of the spark")
    promoted: bool = Field(..., description="Whether promotion occurred")
    previous_level: SparkLevel = Field(..., description="Level before check")
    current_level: SparkLevel = Field(..., description="Level after check")
    bonfire_created: bool = Field(
        default=False,
        description="Whether a new bonfire was created",
    )


class ICheckPromotionUseCase(ABC):
    """Interface for check promotion use case.

    This use case checks if a spark should be promoted based on
    engagement metrics and executes the promotion if conditions are met.

    Called after add_fuel to trigger promotion logic.
    """

    @abstractmethod
    async def execute(self, input_data: CheckPromotionInput) -> CheckPromotionOutput:
        """Check and execute spark promotion.

        Args:
            input_data: Input containing spark_id

        Returns:
            Output indicating promotion result

        Raises:
            AppError: If spark not found (1005)

        """

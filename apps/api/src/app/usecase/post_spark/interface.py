"""Post Spark UseCase Interface.

This module defines the input port for posting spark operations.
"""

from abc import ABC, abstractmethod

from app.usecase.dto.spark_dto import PostSparkInput, SparkOutput


class IPostSparkUseCase(ABC):
    """UseCase interface for posting a spark."""

    @abstractmethod
    async def execute(
        self,
        input_data: PostSparkInput,
        ip_address: str,
    ) -> SparkOutput:
        """Execute the post spark use case.

        Args:
            input_data: Input data containing spark content
            ip_address: Client IP address for user identification

        Returns:
            The created spark details

        Raises:
            AppError: If validation fails or rate limit is exceeded

        """

"""Stream Timeline UseCase Interface.

This module defines the input port for timeline streaming.
"""

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator

from app.usecase.dto.spark_dto import SparkOutput


class IStreamTimelineUseCase(ABC):
    """Interface for streaming timeline use case."""

    @abstractmethod
    async def execute(self) -> AsyncIterator[SparkOutput]:
        """Stream timeline updates (Snapshot + Stream).

        First yields active sparks from the database (Snapshot),
        then yields new sparks from the pub/sub channel (Stream).

        Yields:
            SparkOutput messages from both snapshot and stream

        """
        # This is an async generator method
        # Implementations should yield SparkOutput messages
        if False:  # pragma: no cover
            yield  # type: ignore[misc,unreachable]
        raise NotImplementedError

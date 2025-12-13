"""PubSub Gateway Port.

This module defines the port interface for publish-subscribe messaging.
"""

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from typing import Any

from app.usecase.dto.spark_dto import SparkOutput

# Generic message type for non-spark events
PubSubMessage = dict[str, Any]


class IPubSubGateway(ABC):
    """Interface for publish-subscribe messaging operations."""

    @abstractmethod
    async def publish(
        self,
        channel: str,
        message: SparkOutput | PubSubMessage,
    ) -> None:
        """Publish a message to a channel.

        Args:
            channel: The channel name to publish to
            message: The message to publish (SparkOutput or generic dict)

        """

    @abstractmethod
    async def subscribe(self, channel: str) -> AsyncIterator[SparkOutput]:
        """Subscribe to a channel and yield messages as they arrive.

        Args:
            channel: The channel name to subscribe to

        Yields:
            SparkOutput messages from the channel

        """
        # This is an async generator method
        # Implementations should yield SparkOutput messages
        if False:  # pragma: no cover
            yield  # type: ignore[misc,unreachable]
        raise NotImplementedError

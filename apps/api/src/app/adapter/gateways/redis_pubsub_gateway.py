"""Redis PubSub Gateway Implementation.

This module implements the pub/sub gateway using Redis.
"""

import json
from collections.abc import AsyncIterator

from redis.asyncio import Redis

from app.domain.constants import LOG_EVENTS
from app.usecase.dto.spark_dto import SparkOutput
from app.usecase.ports.logger import ILogger
from app.usecase.ports.pubsub import IPubSubGateway


class RedisPubSubGateway(IPubSubGateway):
    """Redis implementation of pub/sub gateway."""

    def __init__(self, redis: Redis, logger: ILogger) -> None:  # type: ignore[type-arg]
        """Initialize the gateway.

        Args:
            redis: Redis client instance
            logger: Logger for structured logging

        """
        self.redis = redis
        self.logger = logger

    async def publish(self, channel: str, message: SparkOutput) -> None:
        """Publish a message to a channel.

        Args:
            channel: The channel name to publish to
            message: The spark output to publish

        """
        try:
            # Serialize Pydantic model to JSON string
            json_message = message.model_dump_json()

            # Publish to Redis
            await self.redis.publish(channel, json_message)  # type: ignore[misc]

            self.logger.info(
                LOG_EVENTS.PUBSUB_PUBLISH_SUCCESS,
                "Message published to Redis channel",
                context={
                    "channel": channel,
                    "spark_id": message.id,
                },
            )

        except Exception as e:
            self.logger.exception(
                LOG_EVENTS.PUBSUB_PUBLISH_ERROR,
                "Failed to publish message to Redis channel",
                error=e,
                context={
                    "channel": channel,
                    "spark_id": message.id,
                },
            )
            raise

    async def subscribe(self, channel: str) -> AsyncIterator[SparkOutput]:
        """Subscribe to a channel and yield messages as they arrive.

        Args:
            channel: The channel name to subscribe to

        Yields:
            SparkOutput messages from the channel

        """
        pubsub = self.redis.pubsub()  # type: ignore[misc]

        try:
            await pubsub.subscribe(channel)  # type: ignore[misc]

            self.logger.info(
                LOG_EVENTS.PUBSUB_SUBSCRIBE_SUCCESS,
                "Subscribed to Redis channel",
                context={"channel": channel},
            )

            # Iterate over messages from the channel
            async for message in pubsub.listen():  # type: ignore[misc]
                # Skip subscription confirmation messages
                if message["type"] != "message":
                    continue

                try:
                    # Deserialize JSON string to Pydantic model
                    data = message["data"]  # type: ignore[index]
                    if isinstance(data, bytes):
                        data = data.decode("utf-8")

                    spark_dict = json.loads(data)  # type: ignore[arg-type]
                    spark_output = SparkOutput(**spark_dict)

                    self.logger.info(
                        LOG_EVENTS.PUBSUB_MESSAGE_RECEIVED,
                        "Received message from Redis channel",
                        context={
                            "channel": channel,
                            "spark_id": spark_output.id,
                        },
                    )

                    yield spark_output

                except (json.JSONDecodeError, TypeError, KeyError) as e:
                    self.logger.exception(
                        LOG_EVENTS.PUBSUB_DESERIALIZATION_ERROR,
                        "Failed to deserialize message from Redis channel",
                        error=e,
                        context={
                            "channel": channel,
                            "raw_data": str(message.get("data", "")),  # type: ignore[call-overload]
                        },
                    )
                    # Skip malformed messages and continue listening
                    continue

        except Exception as e:
            self.logger.exception(
                LOG_EVENTS.PUBSUB_SUBSCRIBE_ERROR,
                "Error during Redis subscription",
                error=e,
                context={"channel": channel},
            )
            raise

        finally:
            # Clean up subscription
            await pubsub.unsubscribe(channel)  # type: ignore[misc]
            await pubsub.aclose()

            self.logger.info(
                LOG_EVENTS.PUBSUB_UNSUBSCRIBE_SUCCESS,
                "Unsubscribed from Redis channel",
                context={"channel": channel},
            )

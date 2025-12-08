"""Stream Timeline UseCase Implementation.

This module implements the business logic for streaming timeline updates.
"""

import asyncio
import contextlib
from collections.abc import AsyncIterator

from app.domain.constants import LOG_EVENTS
from app.domain.repository.spark_repository import ISparkRepository
from app.usecase.dto.spark_dto import SparkOutput
from app.usecase.ports.logger import ILogger
from app.usecase.ports.pubsub import IPubSubGateway
from app.usecase.stream_timeline.interface import IStreamTimelineUseCase


class StreamTimelineInteractor(IStreamTimelineUseCase):
    """Interactor for streaming timeline updates."""

    def __init__(
        self,
        spark_repository: ISparkRepository,
        pubsub_gateway: IPubSubGateway,
        logger: ILogger,
        active_spark_seconds: int,
        pubsub_channel: str,
    ) -> None:
        """Initialize the interactor.

        Args:
            spark_repository: Repository for spark persistence
            pubsub_gateway: Gateway for pub/sub messaging
            logger: Logger for structured logging
            active_spark_seconds: Seconds to look back for active sparks
            pubsub_channel: Redis pub/sub channel name

        """
        self.spark_repository = spark_repository
        self.pubsub_gateway = pubsub_gateway
        self.logger = logger
        self.active_spark_seconds = active_spark_seconds
        self.pubsub_channel = pubsub_channel

    async def execute(self) -> AsyncIterator[SparkOutput]:
        """Stream timeline updates (Snapshot + Stream).

        Prevents race conditions by:
        1. Starting PubSub subscription first (buffering new messages)
        2. Fetching DB snapshot
        3. Yielding snapshot data
        4. Yielding buffered + real-time stream (with deduplication)

        Yields:
            SparkOutput messages from both snapshot and stream

        """
        # Queue for buffering PubSub messages during DB fetch
        buffer: asyncio.Queue[SparkOutput] = asyncio.Queue()

        # Background task to subscribe to PubSub
        async def pubsub_listener() -> None:
            """Listen to PubSub and buffer messages."""
            self.logger.info(
                LOG_EVENTS.TIMELINE_STREAM_STARTED,
                "Starting timeline stream subscription",
                context={"channel": self.pubsub_channel},
            )
            async for spark_output in self.pubsub_gateway.subscribe(
                self.pubsub_channel
            ):
                self.logger.info(
                    LOG_EVENTS.TIMELINE_STREAM_MESSAGE,
                    "Received message from pub/sub",
                    context={"spark_id": spark_output.id},
                )
                await buffer.put(spark_output)

        # Phase 1: Start PubSub subscription in background
        pubsub_task = asyncio.create_task(pubsub_listener())

        try:
            # Phase 2: Fetch active sparks from DB (while PubSub is buffering)
            snapshot_ids: set[str] = set()
            snapshot_count = 0

            async for spark in self.spark_repository.find_active_sparks(
                seconds=self.active_spark_seconds,
            ):
                snapshot_ids.add(spark.id)
                snapshot_count += 1
                yield SparkOutput(
                    id=spark.id,
                    content=spark.content,
                    created_at=spark.created_at,
                    decay_at=spark.decay_at,
                )

            self.logger.info(
                LOG_EVENTS.TIMELINE_SNAPSHOT_LOADED,
                "Loaded active sparks snapshot",
                context={"count": snapshot_count},
            )

            # Phase 3: Yield buffered messages (deduplicated)
            # Drain the buffer and yield non-duplicate messages
            while not buffer.empty():
                buffered_spark = await buffer.get()
                if buffered_spark.id not in snapshot_ids:
                    snapshot_ids.add(buffered_spark.id)
                    yield buffered_spark

            # Phase 4: Continue yielding real-time stream (deduplicated)
            while True:
                stream_spark = await buffer.get()
                if stream_spark.id not in snapshot_ids:
                    snapshot_ids.add(stream_spark.id)
                    yield stream_spark

        finally:
            # Clean up: cancel the background task
            pubsub_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await pubsub_task

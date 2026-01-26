"""Stream Timeline UseCase Implementation.

This module implements the business logic for streaming timeline updates.
"""

import asyncio
import contextlib
from collections.abc import AsyncIterator

from app.domain.constants import LOG_EVENTS, PUBSUB_BUFFER_SIZE
from app.domain.repository.spark_repository import ISparkRepository
from app.usecase.dto.spark_dto import SparkOutput
from app.usecase.dto.timeline_event import SparkPostedEvent, SparkUpdatedEvent, TimelineEvent
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
    ) -> None:
        """Initialize the interactor.

        Args:
            spark_repository: Repository for spark persistence
            pubsub_gateway: Gateway for pub/sub messaging
            logger: Logger for structured logging
            active_spark_seconds: Seconds to look back for active sparks

        """
        self.spark_repository = spark_repository
        self.pubsub_gateway = pubsub_gateway
        self.logger = logger
        self.active_spark_seconds = active_spark_seconds

    async def execute(self, field_id: str) -> AsyncIterator[TimelineEvent]:
        """Stream timeline updates (Snapshot + Stream).

        Prevents race conditions by:
        1. Starting PubSub subscription first (buffering new messages)
        2. Fetching DB snapshot
        3. Yielding snapshot data as SparkPostedEvents
        4. Yielding buffered + real-time stream (with processing)

        Yields:
            TimelineEvent messages from both snapshot and stream

        """
        # Queue for buffering PubSub messages during DB fetch
        # Use bounded queue to prevent memory leaks (Active User Load Protection)
        buffer: asyncio.Queue[TimelineEvent] = asyncio.Queue(maxsize=PUBSUB_BUFFER_SIZE)

        # Background task to subscribe to PubSub
        async def pubsub_listener() -> None:
            """Listen to PubSub and buffer messages."""
            # Dynamic channel for the field
            channel = f"timeline:{field_id}"

            self.logger.info(
                LOG_EVENTS.TIMELINE_STREAM_STARTED,
                "Starting timeline stream subscription",
                context={"channel": channel},
            )

            # Using subscribe_raw to handle multiple message types (posted/updated)
            async for raw_msg in self.pubsub_gateway.subscribe_raw([channel]):
                msg_type = raw_msg.get("type")

                # DEBUG Log
                self.logger.info(
                    "DEBUG_TIMELINE_STREAM",
                    "Received raw message",
                    context={"msg_type": msg_type, "keys": list(raw_msg.keys())}
                )

                try:
                    event: TimelineEvent | None = None

                    if msg_type == "spark_updated":
                        event = SparkUpdatedEvent(**raw_msg)
                    elif msg_type == "spark_posted":
                        if "data" in raw_msg:
                             # Expected format: { "type": "spark_posted", "data": { ... } }
                             spark_output = SparkOutput(**raw_msg["data"])
                             event = SparkPostedEvent(data=spark_output)
                        else:
                             # Maybe the message IS the SparkOutput data but with a type field?
                             # Let's assume standard format first.
                             pass
                    else:
                        # Fallback for legacy messages or implicit types
                        # If the message looks like a SparkOutput (has id, content)
                        if "id" in raw_msg and "content" in raw_msg:
                             spark_output = SparkOutput(**raw_msg)
                             event = SparkPostedEvent(data=spark_output)

                    if event:
                        try:
                            # Try to put in buffer with timeout to drop if full
                            await asyncio.wait_for(buffer.put(event), timeout=0.1)
                        except asyncio.TimeoutError:
                            self.logger.warning(
                                LOG_EVENTS.PUBSUB_BUFFER_OVERFLOW,
                                "Buffer full, dropping message",
                                context={"channel": channel},
                            )
                    else:
                        self.logger.warning(
                            LOG_EVENTS.PUBSUB_DESERIALIZATION_ERROR,
                            "Unknown message type received",
                            context={"raw_msg": raw_msg},
                        )

                except Exception as e:
                     self.logger.error(
                        LOG_EVENTS.PUBSUB_DESERIALIZATION_ERROR,
                        "Failed to parse timeline event",
                        error=e,
                        context={"raw_msg": raw_msg},
                     )

        # Phase 1: Start PubSub subscription in background
        pubsub_task = asyncio.create_task(pubsub_listener())

        try:
            # Phase 2: Fetch active sparks from DB (while PubSub is buffering)
            snapshot_ids: set[str] = set()
            snapshot_count = 0

            async for spark in self.spark_repository.find_active_sparks(
                field_id=field_id,
                seconds=self.active_spark_seconds,
            ):
                snapshot_ids.add(spark.id)
                snapshot_count += 1

                # Convert domain Spark to SparkOutput -> SparkPostedEvent
                spark_output = SparkOutput(
                    id=spark.id,
                    content=spark.content,
                    user_hash=spark.user_hash[:8],
                    field_id=spark.field_id,
                    created_at=spark.created_at,
                    decay_at=spark.decay_at,
                )
                yield SparkPostedEvent(data=spark_output)

            self.logger.info(
                LOG_EVENTS.TIMELINE_SNAPSHOT_LOADED,
                "Loaded active sparks snapshot",
                context={"count": snapshot_count},
            )

            # Phase 3: Yield buffered messages (deduplicated for Posted events)
            while not buffer.empty():
                event = await buffer.get()

                if isinstance(event, SparkPostedEvent):
                    if event.data.id not in snapshot_ids:
                        snapshot_ids.add(event.data.id)
                        yield event
                else:
                    # Always yield updates
                    yield event

            # Phase 4: Continue yielding real-time stream
            while True:
                event = await buffer.get()

                if isinstance(event, SparkPostedEvent):
                    if event.data.id not in snapshot_ids:
                        snapshot_ids.add(event.data.id)
                        yield event
                else:
                    yield event

        finally:
            # Clean up: cancel the background task
            pubsub_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await pubsub_task

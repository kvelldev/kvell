"""Stream Bonfire UseCase Implementation.

This module implements the business logic for streaming bonfire detail updates.
"""

import asyncio
import contextlib
from collections.abc import AsyncIterator

from pydantic import ValidationError

from app.domain.constants import LOG_EVENTS
from app.domain.exception import AppError
from app.domain.repository.bonfire_repository import IBonfireRepository
from app.domain.repository.spark_repository import ISparkRepository
from app.usecase.dto.spark_dto import SparkOutput
from app.usecase.ports.logger import ILogger
from app.usecase.ports.pubsub import IPubSubGateway, PubSubMessage
from app.usecase.stream_bonfire.interface import (
    BonfireEvent,
    BonfireEventType,
    BonfireStreamMessage,
    IStreamBonfireUseCase,
    PubSubMessageAdapter,
    RawBonfireDecayedMessage,
    RawSparkMessage,
)

# Buffer size for PubSub messages (prevents memory leak)
BUFFER_MAX_SIZE = 1000


class StreamBonfireInteractor(IStreamBonfireUseCase):
    """Interactor for streaming bonfire detail updates."""

    def __init__(
        self,
        spark_repository: ISparkRepository,
        bonfire_repository: IBonfireRepository,
        pubsub_gateway: IPubSubGateway,
        logger: ILogger,
    ) -> None:
        """Initialize the interactor."""
        self.spark_repository = spark_repository
        self.bonfire_repository = bonfire_repository
        self.pubsub_gateway = pubsub_gateway
        self.logger = logger

    async def execute(self, bonfire_id: str) -> AsyncIterator[BonfireStreamMessage]:
        """Stream bonfire detail updates (Snapshot + Stream)."""
        bonfire = await self.bonfire_repository.find_by_id(bonfire_id)
        if bonfire is None:
            self._log_bonfire_not_found(bonfire_id)
            raise AppError(internal_code=1005)

        buffer: asyncio.Queue[PubSubMessage] = asyncio.Queue(maxsize=BUFFER_MAX_SIZE)
        channel = f"bonfire:{bonfire_id}"
        pubsub_task = asyncio.create_task(
            self._run_pubsub_listener(buffer, channel, bonfire_id)
        )

        try:
            # Phase 1: Yield snapshot from DB
            snapshot_ids: set[str] = set()
            async for output in self._yield_snapshot(bonfire_id, snapshot_ids):
                yield output

            # Phase 2: Yield deduplicated stream messages
            async for output in self._yield_stream(buffer, snapshot_ids):
                yield output

        finally:
            pubsub_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await pubsub_task

    async def _run_pubsub_listener(
        self,
        buffer: asyncio.Queue[PubSubMessage],
        channel: str,
        bonfire_id: str,
    ) -> None:
        """Listen to PubSub and buffer messages."""
        self.logger.info(
            LOG_EVENTS.TIMELINE_STREAM_STARTED,
            "Starting bonfire stream subscription",
            context={"channel": channel, "bonfire_id": bonfire_id},
        )
        async for message in self.pubsub_gateway.subscribe_raw(channel):
            self.logger.info(
                LOG_EVENTS.TIMELINE_STREAM_MESSAGE,
                "Received message from bonfire pub/sub",
                context={
                    "bonfire_id": bonfire_id,
                    "message_type": message.get("type", "unknown"),
                },
            )
            try:
                buffer.put_nowait(message)
            except asyncio.QueueFull:
                self.logger.warning(
                    LOG_EVENTS.PUBSUB_BUFFER_OVERFLOW,
                    "Stream buffer overflow, dropping message",
                    context={"bonfire_id": bonfire_id, "buffer_size": BUFFER_MAX_SIZE},
                )

    async def _yield_snapshot(
        self, bonfire_id: str, snapshot_ids: set[str]
    ) -> AsyncIterator[SparkOutput]:
        """Yield snapshot replies from DB."""
        count = 0
        async for spark in self.spark_repository.find_replies_by_bonfire_id(
            bonfire_id=bonfire_id,
        ):
            snapshot_ids.add(spark.id)
            count += 1
            yield SparkOutput(
                id=spark.id,
                content=spark.content,
                parent_bonfire_id=spark.parent_bonfire_id,
                created_at=spark.created_at,
                decay_at=spark.decay_at,
            )
        self.logger.info(
            LOG_EVENTS.TIMELINE_SNAPSHOT_LOADED,
            "Loaded bonfire replies snapshot",
            context={"bonfire_id": bonfire_id, "count": count},
        )

    async def _yield_stream(
        self,
        buffer: asyncio.Queue[PubSubMessage],
        snapshot_ids: set[str],
    ) -> AsyncIterator[BonfireStreamMessage]:
        """Yield deduplicated stream messages from buffer."""
        while True:
            msg = await buffer.get()
            parsed = self._parse_message(msg)
            if parsed is None:
                continue
            if isinstance(parsed, SparkOutput) and parsed.id in snapshot_ids:
                continue
            if isinstance(parsed, SparkOutput):
                snapshot_ids.add(parsed.id)
            yield parsed

    def _log_bonfire_not_found(self, bonfire_id: str) -> None:
        """Log bonfire not found warning."""
        self.logger.warning(
            LOG_EVENTS.BONFIRE_NOT_FOUND,
            "Bonfire not found for streaming",
            context={"bonfire_id": bonfire_id},
        )

    def _parse_message(self, message: PubSubMessage) -> BonfireStreamMessage | None:
        """Parse a raw pub/sub message into typed message using TypeAdapter.

        Args:
            message: Raw message dict from pub/sub

        Returns:
            SparkOutput for spark messages, BonfireEvent for events, None for invalid

        """
        try:
            parsed = PubSubMessageAdapter.validate_python(message)
        except ValidationError as e:
            self.logger.warning(
                LOG_EVENTS.PUBSUB_DESERIALIZATION_ERROR,
                "Failed to parse PubSub message",
                context={"error": str(e), "message": str(message)},
            )
            return None

        # Convert to stream message type
        if isinstance(parsed, RawSparkMessage):
            return SparkOutput(
                id=parsed.id,
                content=parsed.content,
                parent_bonfire_id=parsed.parent_bonfire_id,
                created_at=parsed.created_at,
                decay_at=parsed.decay_at,
            )
        if isinstance(parsed, RawBonfireDecayedMessage):
            return BonfireEvent(
                event_type=BonfireEventType.DECAYED,
                bonfire_id=parsed.bonfire_id,
                message=parsed.message,
            )
        # RawBonfireExtendedMessage
        return BonfireEvent(
            event_type=BonfireEventType.EXTENDED,
            bonfire_id=parsed.bonfire_id,
            message=parsed.message,
        )

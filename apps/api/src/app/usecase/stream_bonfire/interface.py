"""Stream Bonfire UseCase Interface.

This module defines the input port for bonfire detail streaming.
"""

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from datetime import datetime
from enum import Enum
from typing import Annotated, Any, Literal, cast

from pydantic import BaseModel, ConfigDict, Discriminator, Field, Tag, TypeAdapter

from app.usecase.dto.spark_dto import SparkOutput


class BonfireEventType(str, Enum):
    """Type of bonfire event."""

    DECAYED = "decayed"
    EXTENDED = "extended"


class BonfireEvent(BaseModel):
    """Event DTO for bonfire state changes."""

    model_config = ConfigDict(frozen=True)

    event_type: BonfireEventType = Field(..., description="Type of event")
    bonfire_id: str = Field(..., description="Bonfire ID")
    message: str = Field(default="", description="Optional message")


# Union type for stream messages
BonfireStreamMessage = SparkOutput | BonfireEvent


# =============================================================================
# PubSub Raw Message Types (for TypeAdapter parsing)
# =============================================================================


class RawSparkMessage(BaseModel):
    """Raw spark message from PubSub."""

    model_config = ConfigDict(frozen=True)

    type: Literal["spark"] = "spark"
    id: str
    content: str
    user_hash: str
    parent_bonfire_id: str | None = None
    field_id: str
    created_at: datetime
    decay_at: datetime


class RawBonfireDecayedMessage(BaseModel):
    """Raw bonfire decayed event from PubSub."""

    model_config = ConfigDict(frozen=True)

    type: Literal["bonfire_decayed"]
    bonfire_id: str
    message: str = ""


class RawBonfireExtendedMessage(BaseModel):
    """Raw bonfire extended event from PubSub."""

    model_config = ConfigDict(frozen=True)

    type: Literal["bonfire_extended"]
    bonfire_id: str
    message: str = ""


def _get_pubsub_message_discriminator(v: dict[str, Any] | object) -> str:
    """Discriminator for PubSub messages by 'type' field."""
    msg_type_str: str = "spark"

    if isinstance(v, dict):
        raw_type = v.get("type", "spark")
        msg_type_str = str(raw_type)
    else:
        raw_type = getattr(v, "type", "spark")
        msg_type_str = str(raw_type)

    # Direct mapping
    type_map = {
        "bonfire_decayed": "decayed",
        "bonfire_extended": "extended",
        "spark": "spark",
    }
    return type_map.get(msg_type_str, "spark")


# Discriminated union type for PubSub raw messages
RawPubSubMessage = Annotated[
    Annotated[RawSparkMessage, Tag("spark")]
    | Annotated[RawBonfireDecayedMessage, Tag("decayed")]
    | Annotated[RawBonfireExtendedMessage, Tag("extended")],
    Discriminator(_get_pubsub_message_discriminator),
]

# TypeAdapter for parsing PubSub messages
PubSubMessageAdapter: TypeAdapter[RawPubSubMessage] = TypeAdapter(RawPubSubMessage)


class IStreamBonfireUseCase(ABC):
    """Interface for streaming bonfire detail use case."""

    @abstractmethod
    async def execute(self, bonfire_id: str) -> AsyncIterator[BonfireStreamMessage]:
        """Stream bonfire detail updates (Snapshot + Stream).

        First yields existing replies from the database (Snapshot),
        then yields new replies and bonfire events from pub/sub (Stream).

        Args:
            bonfire_id: The bonfire ID to stream

        Yields:
            SparkOutput for replies or BonfireEvent for state changes

        """
        if False:  # pragma: no cover
            yield  # type: ignore[misc,unreachable]
        raise NotImplementedError

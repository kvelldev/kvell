"""Timeline Events DTOs.

This module defines Data Transfer Objects for timeline real-time events.
"""

from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_serializer

from app.domain.model.spark import SparkLevel
from app.usecase.dto.spark_dto import SparkOutput


class SparkPostedEvent(BaseModel):
    """Event triggered when a new spark is posted."""

    model_config = ConfigDict(frozen=True)

    type: Literal["spark_posted"] = "spark_posted"
    data: SparkOutput


class SparkUpdatedEvent(BaseModel):
    """Event triggered when a spark's state is updated (promotion, decay extension)."""

    model_config = ConfigDict(frozen=True)

    type: Literal["spark_updated"] = "spark_updated"
    spark_id: str = Field(..., description="ID of the updated spark")
    level: SparkLevel = Field(..., description="New level of the spark")
    decay_at: datetime = Field(
        ..., description="New timeout timestamp (UTC)"
    )
    bonfire_id: str | None = Field(
        default=None,
        description="ID of the created bonfire (if promoted to bonfire)",
    )

    @field_serializer("decay_at")
    def serialize_datetime(self, dt: datetime) -> str:
        """Serialize datetime to ISO 8601 format with Z suffix for UTC."""
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=UTC)
        return dt.astimezone(UTC).isoformat().replace("+00:00", "Z")


TimelineEvent = SparkPostedEvent | SparkUpdatedEvent

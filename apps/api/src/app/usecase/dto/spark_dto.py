"""Spark DTOs.

This module defines Data Transfer Objects for spark use cases.
"""

from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict, Field, field_serializer


class PostSparkInput(BaseModel):
    """Input DTO for posting a spark."""

    model_config = ConfigDict(frozen=True)

    content: str = Field(..., description="Spark content text", min_length=1)
    parent_bonfire_id: str | None = Field(
        default=None,
        description="Parent bonfire ID if this is a reply",
    )


class SparkOutput(BaseModel):
    """Output DTO for spark operations."""

    model_config = ConfigDict(frozen=True)

    id: str = Field(..., description="Spark ID")
    content: str = Field(..., description="Spark content")
    parent_bonfire_id: str | None = Field(
        default=None,
        description="Parent bonfire ID if this is a reply",
    )
    created_at: datetime = Field(..., description="Creation timestamp (UTC)")
    decay_at: datetime = Field(
        ..., description="Timestamp when the spark decays (becomes invisible)"
    )

    @field_serializer("created_at", "decay_at")
    def serialize_datetime(self, dt: datetime) -> str:
        """Serialize datetime to ISO 8601 format with Z suffix for UTC.

        If datetime is naive (no timezone info), assume it's UTC.

        Args:
            dt: Datetime to serialize

        Returns:
            ISO 8601 string with Z suffix (e.g., "2025-12-08T12:34:56.789000Z")

        """
        # If naive datetime, assume UTC
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=UTC)
        # Convert to UTC and format with Z suffix
        return dt.astimezone(UTC).isoformat().replace("+00:00", "Z")

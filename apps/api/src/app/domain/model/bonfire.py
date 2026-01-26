"""Bonfire Entity.

This module defines the Bonfire entity representing a promoted spark.
"""

from datetime import UTC, datetime, timedelta

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.domain.constants import BONFIRE_INITIAL_TTL_HOURS, VALID_FIELDS


class Bonfire(BaseModel):
    """Bonfire entity representing a promoted spark.

    A Bonfire is created when a Spark meets the promotion criteria
    (sufficient unique users and heat score).
    """

    model_config = ConfigDict(frozen=True)

    id: str = Field(..., description="Unique identifier (same as original spark_id)")
    spark_id: str = Field(..., description="Reference to the original spark")
    field_id: str = Field(..., description="Field ID the bonfire belongs to")
    content: str = Field(..., description="Original spark content")
    unique_user_count: int = Field(..., description="Number of unique users engaged")
    heat_score: int = Field(..., description="Heat score at promotion time")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Bonfire creation timestamp (UTC)",
    )
    decay_at: datetime = Field(
        ...,
        description="Timestamp when the bonfire decays",
    )

    @field_validator("field_id")
    @classmethod
    def validate_field_id(cls, v: str) -> str:
        """Validate that field_id is in the allowed list of fields."""
        if v not in VALID_FIELDS:
            raise ValueError(f"Invalid field_id: {v}")
        return v
    @staticmethod
    def create(
        spark_id: str,
        field_id: str,
        content: str,
        unique_user_count: int,
        heat_score: int,
        initial_decay_hours: int = BONFIRE_INITIAL_TTL_HOURS,
    ) -> "Bonfire":
        """Create a new Bonfire from a promoted Spark.

        Args:
        Args:
            spark_id: Original spark's ID
            field_id: Field ID
            content: Original spark content
            unique_user_count: Number of unique users at promotion
            heat_score: Heat score at promotion
            initial_decay_hours: Initial TTL in hours

        Returns:
            New Bonfire instance

        """
        now = datetime.now(UTC)
        return Bonfire(
            id=spark_id,
            spark_id=spark_id,
            field_id=field_id,
            content=content,
            unique_user_count=unique_user_count,
            heat_score=heat_score,
            created_at=now,
            decay_at=now + timedelta(hours=initial_decay_hours),
        )

    def extend_by_fuel(self, extension_minutes: int) -> "Bonfire":
        """Extend bonfire TTL when fuel is added.

        Args:
            extension_minutes: Minutes to extend from current decay_at

        Returns:
            New Bonfire instance with extended decay_at

        """
        new_decay_at = self.decay_at + timedelta(minutes=extension_minutes)
        return self.model_copy(update={"decay_at": new_decay_at})

    def extend_by_reply(
        self,
        extension_hours: int,
        current_time: datetime | None = None,
    ) -> "Bonfire":
        """Extend bonfire TTL when a reply is added.

        Only extends if remaining TTL is shorter than extension_hours.

        Args:
            extension_hours: Hours to extend from current time
            current_time: Current time (default: now)

        Returns:
            New Bonfire instance with extended decay_at (or unchanged)

        """
        now = current_time or datetime.now(UTC)
        new_decay_at = now + timedelta(hours=extension_hours)

        # Only extend if new decay_at is later than current
        if new_decay_at > self.decay_at:
            return self.model_copy(update={"decay_at": new_decay_at})
        return self

    @property
    def is_active(self) -> bool:
        """Check if bonfire is still active (not decayed)."""
        return datetime.now(UTC) < self.decay_at

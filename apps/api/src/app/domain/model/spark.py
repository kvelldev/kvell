"""Spark Entity.

This module defines the Spark entity representing a user's post.
"""

from datetime import UTC, datetime, timedelta

from pydantic import BaseModel, ConfigDict, Field


class Spark(BaseModel):
    """Spark entity representing a user's post."""

    model_config = ConfigDict(frozen=True)

    id: str = Field(..., description="Unique identifier")
    content: str = Field(..., description="Spark content text")
    user_hash: str = Field(..., description="Anonymized user identifier")
    fuel_count: int = Field(default=0, description="Number of fuel added to this spark")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Creation timestamp",
    )
    visible_until: datetime = Field(
        ...,
        description="Timestamp until which the spark is visible",
    )
    expire_at: datetime = Field(
        ...,
        description="Timestamp when the spark will be physically deleted (TTL)",
    )

    @staticmethod
    def create(
        spark_id: str,
        content: str,
        user_hash: str,
        visible_duration_minutes: int,
        ttl_days: int,
    ) -> "Spark":
        """Create a new Spark entity with calculated timestamps.

        Args:
            spark_id: Unique identifier for the spark
            content: Spark content text
            user_hash: Anonymized user identifier
            visible_duration_minutes: Duration in minutes for visibility
            ttl_days: Time to live in days before physical deletion

        Returns:
            New Spark instance

        """
        now = datetime.now(UTC)
        return Spark(
            id=spark_id,
            content=content,
            user_hash=user_hash,
            fuel_count=0,
            created_at=now,
            visible_until=now + timedelta(minutes=visible_duration_minutes),
            expire_at=now + timedelta(days=ttl_days),
        )

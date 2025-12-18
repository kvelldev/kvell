"""Spark Entity.

This module defines the Spark entity representing a user's post.
"""

from datetime import UTC, datetime, timedelta
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class SparkLevel(str, Enum):
    """Level of spark engagement."""

    SPARK = "spark"  # Initial state (TTL: 30min)
    KINDLING = "kindling"  # Extended state (UU >= 3, TTL: 3h)
    BONFIRE = "bonfire"  # Promoted state (UU >= threshold AND heat_score >= 50)


class Spark(BaseModel):
    """Spark entity representing a user's post."""

    model_config = ConfigDict(frozen=True)

    id: str = Field(..., description="Unique identifier")
    content: str = Field(..., description="Spark content text")
    user_hash: str = Field(..., description="Anonymized user identifier")
    fuel_count: int = Field(default=0, description="Number of fuel added to this spark")
    level: SparkLevel = Field(
        default=SparkLevel.SPARK,
        description="Current promotion level",
    )
    parent_bonfire_id: str | None = Field(
        default=None,
        description="Parent bonfire ID if this is a reply, None for root sparks",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Creation timestamp (UTC)",
    )
    decay_at: datetime = Field(
        ...,
        description="Timestamp when the spark decays (becomes invisible)",
    )
    vanish_at: datetime = Field(
        ...,
        description="Timestamp when the spark vanishes (physical deletion via TTL)",
    )

    @staticmethod
    def create(
        spark_id: str,
        content: str,
        user_hash: str,
        decay_after_seconds: int,
        vanish_after_days: int,
        parent_bonfire_id: str | None = None,
        decay_at: datetime | None = None,
    ) -> "Spark":
        """Create a new Spark entity with calculated timestamps.

        Args:
            spark_id: Unique identifier for the spark
            content: Spark content text
            user_hash: Anonymized user identifier
            decay_after_seconds: Duration in seconds until spark decays
            vanish_after_days: Days until spark vanishes (physical deletion)
            parent_bonfire_id: Parent bonfire ID if this is a reply
            decay_at: Explicit decay_at (used for replies to inherit from bonfire)

        Returns:
            New Spark instance

        """
        now = datetime.now(UTC)
        return Spark(
            id=spark_id,
            content=content,
            user_hash=user_hash,
            fuel_count=0,
            parent_bonfire_id=parent_bonfire_id,
            created_at=now,
            decay_at=decay_at if decay_at else now + timedelta(seconds=decay_after_seconds),
            vanish_at=now + timedelta(days=vanish_after_days),
        )

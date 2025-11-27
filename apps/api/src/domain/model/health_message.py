"""Health Message Entity.

This module defines the HealthMessage entity for E2E health check.
"""

from datetime import UTC, datetime

from pydantic import BaseModel, Field


class HealthMessage(BaseModel):
    """Health message entity for system health check."""

    id: str = Field(..., description="Unique identifier")
    message: str = Field(..., description="Health check message")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Creation timestamp",
    )

    class Config:
        """Pydantic configuration."""

        frozen = True  # Immutable entity

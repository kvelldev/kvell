"""Spark DTOs.

This module defines Data Transfer Objects for spark use cases.
"""

from pydantic import BaseModel, ConfigDict, Field


class PostSparkInput(BaseModel):
    """Input DTO for posting a spark."""

    model_config = ConfigDict(frozen=True)

    content: str = Field(..., description="Spark content text", min_length=1)


class SparkOutput(BaseModel):
    """Output DTO for spark operations."""

    model_config = ConfigDict(frozen=True)

    id: str = Field(..., description="Spark ID")
    content: str = Field(..., description="Spark content")
    created_at: str = Field(..., description="Creation timestamp (ISO format)")

"""Health Check DTOs.

This module defines Data Transfer Objects for health check use cases.
"""

from pydantic import BaseModel, Field


class SaveHealthInput(BaseModel):
    """Input DTO for saving health message."""

    message: str = Field(..., description="Health check message to save")


class HealthOutput(BaseModel):
    """Output DTO for health check operations."""

    id: str = Field(..., description="Message ID")
    message: str = Field(..., description="Health check message")
    created_at: str = Field(..., description="Creation timestamp (ISO format)")

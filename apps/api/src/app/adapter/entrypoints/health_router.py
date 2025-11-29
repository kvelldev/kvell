"""Health Check API Router.

This module defines API endpoints for health check operations.
"""

from typing import Annotated

from fastapi import APIRouter, Depends

from app.adapter.entrypoints.dependencies import get_health_usecase
from app.usecase.dto.health_dto import HealthOutput, SaveHealthInput
from app.usecase.health_check.interface import IHealthCheckUseCase

router = APIRouter(prefix="/api/health", tags=["health"])


@router.post("/echo")
async def save_health_message(
    input_data: SaveHealthInput,
    usecase: Annotated[IHealthCheckUseCase, Depends(get_health_usecase)],
) -> HealthOutput:
    """Save a health check message.

    Args:
        input_data: Input data containing the message
        usecase: Health check use case (injected)

    Returns:
        The saved message details

    """
    return await usecase.save_message(input_data)


@router.get("/latest")
async def get_latest_message(
    usecase: Annotated[IHealthCheckUseCase, Depends(get_health_usecase)],
) -> HealthOutput | None:
    """Get the latest health check message.

    Args:
        usecase: Health check use case (injected)

    Returns:
        The latest message, or None if not found

    """
    return await usecase.get_latest_message()

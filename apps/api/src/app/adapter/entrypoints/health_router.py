"""Health Check API Router.

This module defines API endpoints for health check operations.
"""

from typing import Annotated

from fastapi import APIRouter, Depends

from app.adapter.entrypoints.dependencies import get_health_usecase, get_logger
from app.domain.constants import LOG_EVENTS
from app.usecase.dto.health_dto import HealthOutput, SaveHealthInput
from app.usecase.health_check.interface import IHealthCheckUseCase
from app.usecase.ports.logger import ILogger

router = APIRouter(prefix="/api/health", tags=["health"])


@router.post("/echo")
async def save_health_message(
    input_data: SaveHealthInput,
    usecase: Annotated[IHealthCheckUseCase, Depends(get_health_usecase)],
    logger: Annotated[ILogger, Depends(get_logger)],
) -> HealthOutput:
    """Save a health check message.

    Args:
        input_data: Input data containing the message
        usecase: Health check use case (injected)
        logger: Logger instance (injected)

    Returns:
        The saved message details

    """
    logger.info(
        LOG_EVENTS.HEALTH_CHECK_STARTED,
        "Health check save request received",
        context={"message_length": len(input_data.message)},
    )

    result = await usecase.save_message(input_data)

    logger.info(
        LOG_EVENTS.HEALTH_MESSAGE_SAVED,
        "Health check message saved",
        context={"message_id": result.id},
    )

    return result


@router.get("/latest")
async def get_latest_message(
    usecase: Annotated[IHealthCheckUseCase, Depends(get_health_usecase)],
    logger: Annotated[ILogger, Depends(get_logger)],
) -> HealthOutput | None:
    """Get the latest health check message.

    Args:
        usecase: Health check use case (injected)
        logger: Logger instance (injected)

    Returns:
        The latest message, or None if not found

    """
    logger.info(
        LOG_EVENTS.HEALTH_CHECK_STARTED,
        "Health check get latest request received",
    )

    result = await usecase.get_latest_message()

    logger.info(
        LOG_EVENTS.HEALTH_MESSAGE_RETRIEVED,
        "Health check message retrieved" if result else "No message found",
    )

    return result

"""Spark API Router.

This module defines API endpoints for spark operations.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, Request, WebSocket, WebSocketDisconnect, status

from app.adapter.entrypoints.dependencies import (
    get_add_fuel_usecase,
    get_identity_provider,
    get_logger,
    get_post_spark_usecase,
    get_stream_timeline_usecase,
)
from app.domain.constants import LOG_EVENTS
from app.domain.service.identity_provider import IIdentityProvider
from app.usecase.add_fuel.interface import AddFuelInput, AddFuelOutput, IAddFuelUseCase
from app.usecase.dto.spark_dto import PostSparkInput, SparkOutput
from app.usecase.ports.logger import ILogger
from app.usecase.post_spark.interface import IPostSparkUseCase
from app.usecase.stream_timeline.interface import IStreamTimelineUseCase

router = APIRouter(prefix="/api/sparks", tags=["sparks"])


def get_client_ip(request: Request) -> str:
    """Extract client IP address from request.

    Args:
        request: FastAPI request object

    Returns:
        Client IP address

    """
    # Check for X-Forwarded-For header (proxy/load balancer)
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        # Take the first IP if multiple are present
        return forwarded.split(",")[0].strip()

    # Fallback to direct client IP
    if request.client:
        return request.client.host

    # Last resort fallback
    return "0.0.0.0"  # noqa: S104


@router.post("", status_code=status.HTTP_201_CREATED)
async def post_spark(
    request: Request,
    input_data: PostSparkInput,
    usecase: Annotated[IPostSparkUseCase, Depends(get_post_spark_usecase)],
    logger: Annotated[ILogger, Depends(get_logger)],
) -> SparkOutput:
    """Post a new spark.

    Args:
        request: FastAPI request object (for IP extraction)
        input_data: Input data containing spark content
        usecase: Post spark use case (injected)
        logger: Logger instance (injected)

    Returns:
        The created spark details

    Raises:
        AppError: If validation fails or rate limit is exceeded

    """
    ip_address = get_client_ip(request)

    logger.info(
        LOG_EVENTS.SPARK_POST_STARTED,
        "Spark post request received",
        context={
            "content_length": len(input_data.content),
            "ip_address": ip_address,
        },
    )

    result = await usecase.execute(input_data, ip_address)

    logger.info(
        LOG_EVENTS.SPARK_POST_SUCCESS,
        "Spark posted successfully",
        context={"spark_id": result.id},
    )

    return result


@router.post("/{spark_id}/fuel", status_code=status.HTTP_200_OK)
async def add_fuel_to_spark(
    request: Request,
    spark_id: str,
    usecase: Annotated[IAddFuelUseCase, Depends(get_add_fuel_usecase)],
    identity_provider: Annotated[IIdentityProvider, Depends(get_identity_provider)],
    logger: Annotated[ILogger, Depends(get_logger)],
) -> AddFuelOutput:
    """Add fuel to a spark.

    Args:
        request: FastAPI request object (for IP extraction)
        spark_id: The spark ID to add fuel to
        usecase: Add fuel use case (injected)
        identity_provider: Identity provider (injected)
        logger: Logger instance (injected)

    Returns:
        Success response (without revealing fuel count)

    Raises:
        AppError: If spark not found (1005) or already decayed (1001)

    """
    ip_address = get_client_ip(request)
    user_hash = identity_provider.get_user_hash(ip_address)

    logger.info(
        LOG_EVENTS.FUEL_ADD_STARTED,
        "Fuel add request received",
        context={
            "spark_id": spark_id,
            "ip_address": ip_address,
        },
    )

    input_data = AddFuelInput(spark_id=spark_id, user_hash=user_hash)
    output = await usecase.execute(input_data)

    logger.info(
        LOG_EVENTS.FUEL_ADD_SUCCESS,
        "Fuel add request completed",
        context={"spark_id": spark_id},
    )

    return output


@router.websocket("/{field_id}/ws")
async def websocket_timeline(
    websocket: WebSocket,
    field_id: str,
    usecase: Annotated[IStreamTimelineUseCase, Depends(get_stream_timeline_usecase)],
    logger: Annotated[ILogger, Depends(get_logger)],
) -> None:
    """WebSocket endpoint for streaming timeline updates.

    Args:
        websocket: WebSocket connection
        usecase: Stream timeline use case (injected)
        logger: Logger instance (injected)

    """
    await websocket.accept()

    logger.info(
        LOG_EVENTS.WEBSOCKET_CONNECTED,
        "WebSocket connection established",
        context={"client": str(websocket.client), "field_id": field_id},
    )

    try:
        # Stream timeline updates (Snapshot + Stream)
        async for timeline_event in usecase.execute(field_id):
            # Send event as JSON to client
            # model_dump(mode='json') ensures datetime serialization uses string format
            await websocket.send_json(timeline_event.model_dump(mode="json"))

    except WebSocketDisconnect:
        logger.info(
            LOG_EVENTS.WEBSOCKET_DISCONNECTED,
            "WebSocket connection closed by client",
            context={"client": str(websocket.client)},
        )

    except Exception as e:
        logger.exception(
            LOG_EVENTS.WEBSOCKET_ERROR,
            "Error during WebSocket communication",
            error=e,
            context={"client": str(websocket.client)},
        )
        raise

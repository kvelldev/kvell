"""Spark API Router.

This module defines API endpoints for spark operations.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, Request, WebSocket, WebSocketDisconnect, status

from app.adapter.entrypoints.dependencies import (
    get_logger,
    get_post_spark_usecase,
    get_stream_timeline_usecase,
)
from app.domain.constants import LOG_EVENTS
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


@router.websocket("/ws")
async def websocket_timeline(
    websocket: WebSocket,
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
        context={"client": str(websocket.client)},
    )

    try:
        # Stream timeline updates (Snapshot + Stream)
        async for spark_output in usecase.execute():
            # Send spark as JSON to client
            await websocket.send_json(spark_output.model_dump())

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

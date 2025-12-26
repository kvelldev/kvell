"""Bonfire API Router.

This module provides REST and WebSocket endpoints for bonfire operations.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse

from app.adapter.entrypoints.dependencies import (
    get_get_bonfires_usecase,
    get_logger,
    get_stream_bonfire_usecase,
)
from app.domain.constants import LOG_EVENTS
from app.usecase.dto.spark_dto import SparkOutput
from app.usecase.get_bonfires.interface import IGetActiveBonfiresUseCase
from app.usecase.ports.logger import ILogger
from app.usecase.stream_bonfire.interface import IStreamBonfireUseCase

router = APIRouter(prefix="/api/bonfires", tags=["bonfires"])


@router.get("")
async def get_active_bonfires(
    field_id: str,
    usecase: IGetActiveBonfiresUseCase = Depends(get_get_bonfires_usecase),
) -> JSONResponse:
    """Get all active bonfires.

    Returns:
        List of active bonfires with their details

    """
    output = await usecase.execute(field_id)

    return JSONResponse(
        status_code=200,
        content={
            "bonfires": [
                {
                    "id": b.id,
                    "spark_id": b.spark_id,
                    "field_id": b.field_id,
                    "content": b.content,
                    "unique_user_count": b.unique_user_count,
                    "heat_score": b.heat_score,
                    "created_at": b.created_at.isoformat(),
                    "decay_at": b.decay_at.isoformat(),
                }
                for b in output.bonfires
            ],
            "count": output.count,
        },
    )


@router.websocket("/{bonfire_id}/ws")
async def websocket_bonfire(
    websocket: WebSocket,
    bonfire_id: str,
    usecase: Annotated[IStreamBonfireUseCase, Depends(get_stream_bonfire_usecase)],
    logger: Annotated[ILogger, Depends(get_logger)],
) -> None:
    """WebSocket endpoint for streaming bonfire detail updates.

    Args:
        websocket: WebSocket connection
        bonfire_id: The bonfire ID to stream
        usecase: Stream bonfire use case (injected)
        logger: Logger instance (injected)

    """
    await websocket.accept()

    logger.info(
        LOG_EVENTS.WEBSOCKET_CONNECTED,
        "WebSocket connection established for bonfire",
        context={"client": str(websocket.client), "bonfire_id": bonfire_id},
    )

    try:
        # Stream bonfire updates (Snapshot + Stream)
        async for message in usecase.execute(bonfire_id):
            if isinstance(message, SparkOutput):
                # Send spark reply as JSON to client
                await websocket.send_json({
                    "type": "spark",
                    **message.model_dump(),
                })
            else:
                # BonfireEvent: Send bonfire event as JSON to client
                await websocket.send_json({
                    "type": message.event_type.value,
                    "bonfire_id": message.bonfire_id,
                    "message": message.message,
                })

    except WebSocketDisconnect:
        logger.info(
            LOG_EVENTS.WEBSOCKET_DISCONNECTED,
            "WebSocket connection closed by client",
            context={"client": str(websocket.client), "bonfire_id": bonfire_id},
        )

    except Exception as e:
        logger.exception(
            LOG_EVENTS.WEBSOCKET_ERROR,
            "Error during WebSocket communication",
            error=e,
            context={"client": str(websocket.client), "bonfire_id": bonfire_id},
        )
        raise

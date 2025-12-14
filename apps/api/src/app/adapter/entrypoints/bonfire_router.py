"""Bonfire API Router.

This module provides REST endpoints for bonfire operations.
"""

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from app.adapter.entrypoints.dependencies import get_get_bonfires_usecase
from app.usecase.get_bonfires.interface import IGetActiveBonfiresUseCase

router = APIRouter(prefix="/api/bonfires", tags=["bonfires"])


@router.get("")
async def get_active_bonfires(
    usecase: IGetActiveBonfiresUseCase = Depends(get_get_bonfires_usecase),
) -> JSONResponse:
    """Get all active bonfires.

    Returns:
        List of active bonfires with their details

    """
    output = await usecase.execute()

    return JSONResponse(
        status_code=200,
        content={
            "bonfires": [
                {
                    "id": b.id,
                    "spark_id": b.spark_id,
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



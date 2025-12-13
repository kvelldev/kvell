"""Bonfire API Router.

This module provides REST endpoints for bonfire operations.
"""

from uuid import uuid4

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from app.adapter.entrypoints.dependencies import get_get_bonfires_usecase
from app.adapter.infra.database import Database
from app.domain.model.bonfire import Bonfire
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


@router.post("/seed")
async def seed_bonfires() -> JSONResponse:
    """Seed demo bonfires for demonstration.

    Returns:
        Number of bonfires created

    """
    db = Database.get_database()
    collection = db["bonfires"]

    demo_bonfires = [
        Bonfire.create(
            spark_id=str(uuid4()),
            content="これはテスト用の焚き火です。システムによって自動的に生成されました。",
            unique_user_count=15,
            heat_score=80,
            initial_decay_hours=24,
        ),
        Bonfire.create(
            spark_id=str(uuid4()),
            content="もう一つの焚き火。カルーセルの動作確認用です。横スクロールができるはずです。",
            unique_user_count=30,
            heat_score=200,
            initial_decay_hours=48,
        ),
        Bonfire.create(
            spark_id=str(uuid4()),
            content="短い投稿でも、熱量が高ければ焚き火になります。🔥",
            unique_user_count=10,
            heat_score=55,
            initial_decay_hours=3,
        ),
        Bonfire.create(
            spark_id=str(uuid4()),
            content="Default image check. The flame icon should be visible.",
            unique_user_count=50,
            heat_score=500,
            initial_decay_hours=12,
        ),
        Bonfire.create(
            spark_id=str(uuid4()),
            content="Last one for the scroll snap check. 🎉",
            unique_user_count=12,
            heat_score=60,
            initial_decay_hours=5,
        ),
    ]

    for bonfire in demo_bonfires:
        await collection.insert_one(
            {
                "id": bonfire.id,
                "spark_id": bonfire.spark_id,
                "content": bonfire.content,
                "unique_user_count": bonfire.unique_user_count,
                "heat_score": bonfire.heat_score,
                "created_at": bonfire.created_at,
                "decay_at": bonfire.decay_at,
            }
        )

    return JSONResponse(
        status_code=201,
        content={"message": f"Seeded {len(demo_bonfires)} demo bonfires"},
    )


@router.delete("")
async def delete_all_bonfires() -> JSONResponse:
    """Delete all bonfires (cleanup for demo).

    Returns:
        Number of bonfires deleted

    """
    db = Database.get_database()
    collection = db["bonfires"]

    result = await collection.delete_many({})

    return JSONResponse(
        status_code=200,
        content={"message": f"Deleted {result.deleted_count} bonfires"},
    )

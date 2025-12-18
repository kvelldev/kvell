"""Debug API Router.

This module provides endpoints for development/demo operations.
Should be disabled or protected in production.
"""

from datetime import timedelta
from uuid import uuid4

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.adapter.infra.database import Database
from app.domain.model.bonfire import Bonfire
from app.domain.model.spark import Spark

router = APIRouter(prefix="/api/debug", tags=["debug"])

# Demo reply contents for seeding
DEMO_REPLY_CONTENTS = [
    "なるほど、そういう見方もあるんですね",
    "同意！私もそう思ってた",
    "これは興味深い話題ですね 🤔",
    "もう少し詳しく聞きたいです",
    "賛成です！素晴らしい意見だと思います",
    "ちょっと違う視点から言うと...",
    "面白い！シェアしてくれてありがとう",
    "これについてもっと議論したい",
]


@router.post("/seed")
async def seed_bonfires() -> JSONResponse:
    """Seed demo bonfires with replies for demonstration.

    Returns:
        Number of bonfires and replies created

    """
    db = Database.get_database()
    bonfires_collection = db["bonfires"]
    sparks_collection = db["sparks"]

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

    total_replies = 0

    for bonfire in demo_bonfires:
        # Insert bonfire
        await bonfires_collection.insert_one(
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

        # Create replies for this bonfire (3-5 replies each)
        num_replies = (hash(bonfire.id) % 3) + 3  # 3-5 replies
        for i in range(num_replies):
            reply = Spark.create(
                spark_id=str(uuid4()),
                content=DEMO_REPLY_CONTENTS[i % len(DEMO_REPLY_CONTENTS)],
                user_hash=f"demo-user-{i}",
                decay_after_seconds=3600,  # 1 hour (will be overridden)
                vanish_after_days=30,
                parent_bonfire_id=bonfire.id,
                decay_at=bonfire.decay_at,  # Inherit from parent bonfire
            )

            # Stagger creation times for realistic ordering
            staggered_created_at = bonfire.created_at + timedelta(minutes=i * 5)

            await sparks_collection.insert_one(
                {
                    "id": reply.id,
                    "content": reply.content,
                    "user_hash": reply.user_hash,
                    "fuel_count": reply.fuel_count,
                    "level": reply.level.value,
                    "parent_bonfire_id": reply.parent_bonfire_id,
                    "created_at": staggered_created_at,
                    "decay_at": reply.decay_at,
                    "vanish_at": reply.vanish_at,
                }
            )
            total_replies += 1

    return JSONResponse(
        status_code=201,
        content={
            "message": (
                f"Seeded {len(demo_bonfires)} bonfires with {total_replies} replies"
            )
        },
    )


@router.delete("/cleanup")
async def delete_all_bonfires() -> JSONResponse:
    """Delete all bonfires and their replies (cleanup for demo).

    Returns:
        Number of bonfires and replies deleted

    """
    db = Database.get_database()
    bonfires_collection = db["bonfires"]
    sparks_collection = db["sparks"]

    # Delete all reply sparks (sparks with parent_bonfire_id)
    sparks_result = await sparks_collection.delete_many(
        {"parent_bonfire_id": {"$ne": None}}
    )

    # Delete all bonfires
    bonfires_result = await bonfires_collection.delete_many({})

    return JSONResponse(
        status_code=200,
        content={
            "message": (
                f"Deleted {bonfires_result.deleted_count} bonfires "
                f"and {sparks_result.deleted_count} replies"
            )
        },
    )

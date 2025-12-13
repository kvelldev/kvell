import asyncio
import sys
import os
import argparse
from datetime import datetime, timedelta, UTC
from uuid import uuid4

# Add src to python path to allow imports from app
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, "../src")
sys.path.append(src_path)

from app.adapter.infra.database import Database
from app.adapter.infra.logger import JsonLogger
from app.adapter.gateways.mongo_bonfire_repository import MongoBonfireRepository
from app.domain.model.bonfire import Bonfire


async def main():
    parser = argparse.ArgumentParser(description="Seed or clean bonfires.")
    parser.add_argument(
        "--clean", action="store_true", help="Delete all bonfires instead of seeding"
    )
    args = parser.parse_args()

    logger = JsonLogger(service_name="seed-script")

    print("Connecting to database...")
    try:
        Database.connect()
        db = Database.get_database()
        print("Connected.")
    except Exception as e:
        print(f"Failed to connect to DB: {e}")
        return

    repo = MongoBonfireRepository(db, logger)

    if args.clean:
        print("Cleaning up bonfires...")
        try:
            # Delete all documents in bonfires collection
            result = await db["bonfires"].delete_many({})
            print(f"Deleted {result.deleted_count} bonfires.")
        except Exception as e:
            print(f"Failed to clean bonfires: {e}")
    else:
        print("Creating dummy bonfires...")
        bonfires = [
            Bonfire.create(
                spark_id=str(uuid4()),
                content="これはテスト用の焚き火です。システムによって自動的に生成されました。24時間燃え続けます。",
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
                content="短い投稿でも、熱量が高ければ焚き火になります。",
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
                content="Last one for the scroll snap check.",
                unique_user_count=12,
                heat_score=60,
                initial_decay_hours=5,
            ),
        ]

        for b in bonfires:
            try:
                await repo.save(b)
                print(f"Saved bonfire: {b.id} ({b.content[:20]}...)")
            except Exception as e:
                print(f"Failed to save bonfire {b.id}: {e}")

        print("Seeding completed.")

    Database.disconnect()


if __name__ == "__main__":
    asyncio.run(main())

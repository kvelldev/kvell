"""MongoDB implementation of Spark Repository.

This module implements the spark repository using MongoDB.
"""

from collections.abc import AsyncIterator
from datetime import UTC, datetime, timedelta
from typing import Any

from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import IndexModel
from pymongo.errors import PyMongoError

from app.domain.constants import LOG_EVENTS
from app.domain.exception import AppError
from app.domain.model.spark import Spark
from app.domain.repository.spark_repository import ISparkRepository
from app.usecase.ports.logger import ILogger


class MongoSparkRepository(ISparkRepository):
    """MongoDB implementation of spark repository."""

    COLLECTION_NAME = "sparks"

    def __init__(self, db: AsyncIOMotorDatabase[Any], logger: ILogger) -> None:
        """Initialize the repository.

        Args:
            db: MongoDB database instance
            logger: Logger for structured logging

        """
        self.collection = db[self.COLLECTION_NAME]
        self.logger = logger

    async def ensure_indexes(self) -> None:
        """Create necessary indexes for the sparks collection.

        This should be called during application startup.
        """
        try:
            indexes = [
                # TTL index for automatic deletion
                IndexModel(
                    [("expire_at", 1)],
                    name="expire_at_ttl",
                    expireAfterSeconds=0,
                ),
                # Query index for timeline retrieval (by visible_until)
                IndexModel(
                    [("visible_until", -1)],
                    name="visible_until_desc",
                ),
                # Query index for active sparks retrieval (by created_at)
                IndexModel(
                    [("created_at", 1)],
                    name="created_at_asc",
                ),
            ]
            await self.collection.create_indexes(indexes)
            self.logger.info(
                LOG_EVENTS.DB_CONNECTION_SUCCESS,
                "Spark indexes created successfully",
                context={"collection": self.COLLECTION_NAME},
            )
        except PyMongoError as e:
            self.logger.exception(
                LOG_EVENTS.DB_QUERY_ERROR,
                f"Failed to create indexes: {self.COLLECTION_NAME}",
                error=e,
            )
            raise AppError(
                internal_code=2002,
                context={"tableName": self.COLLECTION_NAME},
                cause=e,
            ) from e

    async def save(self, spark: Spark) -> Spark:
        """Save a spark.

        Args:
            spark: The spark to save

        Returns:
            The saved spark

        Raises:
            AppError: If database operation fails

        """
        try:
            self.logger.info(
                LOG_EVENTS.DB_CONNECTION_SUCCESS,
                "Saving spark to MongoDB",
                context={
                    "collection": self.COLLECTION_NAME,
                    "spark_id": spark.id,
                },
            )

            document = {
                "id": spark.id,
                "content": spark.content,
                "user_hash": spark.user_hash,
                "fuel_count": spark.fuel_count,
                "created_at": spark.created_at,
                "visible_until": spark.visible_until,
                "expire_at": spark.expire_at,
            }

            await self.collection.insert_one(document)

            self.logger.info(
                LOG_EVENTS.DB_CONNECTION_SUCCESS,
                "Spark saved successfully",
                context={"spark_id": spark.id},
            )
        except PyMongoError as e:
            self.logger.exception(
                LOG_EVENTS.DB_QUERY_ERROR,
                f"Failed to save spark: {self.COLLECTION_NAME}",
                error=e,
                context={
                    "collection": self.COLLECTION_NAME,
                    "spark_id": spark.id,
                },
            )
            raise AppError(
                internal_code=2002,
                context={"tableName": self.COLLECTION_NAME},
                cause=e,
            ) from e
        else:
            return spark

    async def find_by_id(self, spark_id: str) -> Spark | None:
        """Find a spark by ID.

        Args:
            spark_id: The spark ID to search for

        Returns:
            The spark if found, None otherwise

        Raises:
            AppError: If database operation fails

        """
        try:
            self.logger.info(
                LOG_EVENTS.DB_CONNECTION_SUCCESS,
                "Querying spark by ID",
                context={
                    "collection": self.COLLECTION_NAME,
                    "spark_id": spark_id,
                },
            )

            document: dict[str, Any] | None = await self.collection.find_one(
                {"id": spark_id},
            )
        except PyMongoError as e:
            self.logger.exception(
                LOG_EVENTS.DB_QUERY_ERROR,
                f"Failed to query spark: {self.COLLECTION_NAME}",
                error=e,
                context={
                    "collection": self.COLLECTION_NAME,
                    "spark_id": spark_id,
                },
            )
            raise AppError(
                internal_code=2002,
                context={"tableName": self.COLLECTION_NAME},
                cause=e,
            ) from e
        else:
            if document is None:
                self.logger.info(
                    LOG_EVENTS.DB_CONNECTION_SUCCESS,
                    "Spark not found",
                    context={
                        "collection": self.COLLECTION_NAME,
                        "spark_id": spark_id,
                    },
                )
                return None

            self.logger.info(
                LOG_EVENTS.DB_CONNECTION_SUCCESS,
                "Spark retrieved successfully",
                context={
                    "collection": self.COLLECTION_NAME,
                    "spark_id": document["id"],
                },
            )

            return Spark(
                id=document["id"],
                content=document["content"],
                user_hash=document["user_hash"],
                fuel_count=document.get("fuel_count", 0),
                created_at=document["created_at"],
                visible_until=document["visible_until"],
                expire_at=document["expire_at"],
            )

    async def find_active_sparks(self, minutes: int) -> AsyncIterator[Spark]:
        """Find all active sparks created within the specified minutes.

        Args:
            minutes: Number of minutes to look back from now

        Yields:
            Active sparks sorted by created_at in ascending order (oldest first)

        Raises:
            AppError: If database operation fails

        """
        try:
            # Calculate the cutoff time
            cutoff_time = datetime.now(UTC) - timedelta(minutes=minutes)

            self.logger.info(
                LOG_EVENTS.DB_CONNECTION_SUCCESS,
                "Querying active sparks",
                context={
                    "collection": self.COLLECTION_NAME,
                    "cutoff_time": cutoff_time.isoformat(),
                },
            )

            # Query for sparks created after cutoff_time, sorted by created_at ascending
            cursor = self.collection.find(
                {"created_at": {"$gte": cutoff_time}},
            ).sort("created_at", 1)

            # Yield sparks one by one (streaming, no to_list)
            count = 0
            async for doc in cursor:
                count += 1
                yield Spark(
                    id=doc["id"],
                    content=doc["content"],
                    user_hash=doc["user_hash"],
                    fuel_count=doc.get("fuel_count", 0),
                    created_at=doc["created_at"],
                    visible_until=doc["visible_until"],
                    expire_at=doc["expire_at"],
                )

            self.logger.info(
                LOG_EVENTS.DB_CONNECTION_SUCCESS,
                "Active sparks retrieved successfully",
                context={
                    "collection": self.COLLECTION_NAME,
                    "count": count,
                },
            )

        except PyMongoError as e:
            self.logger.exception(
                LOG_EVENTS.DB_QUERY_ERROR,
                f"Failed to query active sparks: {self.COLLECTION_NAME}",
                error=e,
                context={
                    "collection": self.COLLECTION_NAME,
                    "minutes": minutes,
                },
            )
            raise AppError(
                internal_code=2002,
                context={"tableName": self.COLLECTION_NAME},
                cause=e,
            ) from e

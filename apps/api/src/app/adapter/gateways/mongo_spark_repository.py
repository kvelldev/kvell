"""MongoDB implementation of Spark Repository.

This module implements the spark repository using MongoDB.
"""

from collections.abc import AsyncIterator
from datetime import UTC, datetime, timedelta
from typing import Any

from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import IndexModel
from pymongo.errors import DuplicateKeyError, PyMongoError

from app.domain.constants import LOG_EVENTS
from app.domain.exception import AppError
from app.domain.model.spark import Spark, SparkLevel
from app.domain.model.spark_engagement import SparkEngagement
from app.domain.repository.spark_repository import ISparkRepository
from app.usecase.ports.logger import ILogger


class MongoSparkRepository(ISparkRepository):
    """MongoDB implementation of spark repository."""

    COLLECTION_NAME = "sparks"
    FUEL_HISTORY_COLLECTION = "spark_fuel_history"

    def __init__(self, db: AsyncIOMotorDatabase[Any], logger: ILogger) -> None:
        """Initialize the repository.

        Args:
            db: MongoDB database instance
            logger: Logger for structured logging

        """
        self.db = db
        self.collection = db[self.COLLECTION_NAME]
        self.fuel_history_collection = db[self.FUEL_HISTORY_COLLECTION]
        self.logger = logger

    async def ensure_indexes(self) -> None:
        """Create necessary indexes for the sparks and fuel history collections.

        This should be called during application startup.
        """
        try:
            # Sparks collection indexes
            spark_indexes = [
                # TTL index for automatic deletion
                IndexModel(
                    [("vanish_at", 1)],
                    name="vanish_at_ttl",
                    expireAfterSeconds=0,
                ),
                # Query index for timeline retrieval (by decay_at)
                IndexModel(
                    [("decay_at", -1)],
                    name="decay_at_desc",
                ),
                # Query index for active sparks retrieval (by created_at)
                IndexModel(
                    [("created_at", 1)],
                    name="created_at_asc",
                ),
                # Query index for replies retrieval (by parent_bonfire_id)
                IndexModel(
                    [("parent_bonfire_id", 1), ("created_at", 1)],
                    name="parent_bonfire_id_created_at_asc",
                ),
            ]
            await self.collection.create_indexes(spark_indexes)
            self.logger.info(
                LOG_EVENTS.DB_CONNECTION_SUCCESS,
                "Spark indexes created successfully",
                context={"collection": self.COLLECTION_NAME},
            )

            # Fuel history collection indexes
            fuel_history_indexes = [
                # Unique compound index for idempotency
                IndexModel(
                    [("spark_id", 1), ("user_hash", 1)],
                    name="spark_user_unique",
                    unique=True,
                ),
                # TTL index for cleanup (optional - keep fuel history for 30 days)
                IndexModel(
                    [("created_at", 1)],
                    name="created_at_ttl",
                    expireAfterSeconds=30 * 24 * 60 * 60,  # 30 days
                ),
            ]
            await self.fuel_history_collection.create_indexes(fuel_history_indexes)
            self.logger.info(
                LOG_EVENTS.DB_CONNECTION_SUCCESS,
                "Fuel history indexes created successfully",
                context={"collection": self.FUEL_HISTORY_COLLECTION},
            )

        except PyMongoError as e:
            self.logger.exception(
                LOG_EVENTS.DB_QUERY_ERROR,
                "Failed to create indexes",
                error=e,
            )
            raise AppError(
                internal_code=2002,
                context={"tableName": "sparks/fuel_history"},
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
                "level": spark.level.value,
                "parent_bonfire_id": spark.parent_bonfire_id,
                "created_at": spark.created_at,
                "decay_at": spark.decay_at,
                "vanish_at": spark.vanish_at,
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

            # MongoDB stores datetime as UTC but returns them as timezone-naive
            # Add UTC timezone to match Spark model expectations
            created_at = document["created_at"].replace(tzinfo=UTC)
            decay_at = document["decay_at"].replace(tzinfo=UTC)
            vanish_at = document["vanish_at"].replace(tzinfo=UTC)

            # Parse level with fallback for legacy documents
            level_str = document.get("level", SparkLevel.SPARK.value)
            level = SparkLevel(level_str)

            return Spark(
                id=document["id"],
                content=document["content"],
                user_hash=document["user_hash"],
                fuel_count=document.get("fuel_count", 0),
                level=level,
                parent_bonfire_id=document.get("parent_bonfire_id"),
                created_at=created_at,
                decay_at=decay_at,
                vanish_at=vanish_at,
            )

    async def find_active_sparks(
        self,
        seconds: int,
        limit: int = 1000,
    ) -> AsyncIterator[Spark]:
        """Find all active sparks created within the specified seconds.

        Args:
            seconds: Number of seconds to look back from now
            limit: Maximum number of sparks to return (default 1000)

        Yields:
            Active sparks sorted by created_at in ascending order (oldest first)

        Raises:
            AppError: If database operation fails

        """
        try:
            # Calculate the cutoff time
            cutoff_time = datetime.now(UTC) - timedelta(seconds=seconds)

            self.logger.info(
                LOG_EVENTS.DB_CONNECTION_SUCCESS,
                "Querying active sparks",
                context={
                    "collection": self.COLLECTION_NAME,
                    "cutoff_time": cutoff_time.isoformat(),
                    "limit": limit,
                },
            )

            # Query for active sparks (not BONFIRE) created after cutoff_time
            cursor = self.collection.find(
                {
                    "created_at": {"$gte": cutoff_time},
                    "level": {"$ne": SparkLevel.BONFIRE.value},
                },
            ).sort("created_at", 1).limit(limit)

            # Yield sparks one by one (streaming, no to_list)
            count = 0
            async for doc in cursor:
                count += 1
                # MongoDB returns datetime as UTC but timezone-naive
                # Add UTC timezone to match Spark model expectations
                created_at = doc["created_at"].replace(tzinfo=UTC)
                decay_at = doc["decay_at"].replace(tzinfo=UTC)
                vanish_at = doc["vanish_at"].replace(tzinfo=UTC)

                # Parse level with fallback for legacy documents
                level_str = doc.get("level", SparkLevel.SPARK.value)
                level = SparkLevel(level_str)

                yield Spark(
                    id=doc["id"],
                    content=doc["content"],
                    user_hash=doc["user_hash"],
                    fuel_count=doc.get("fuel_count", 0),
                    level=level,
                    parent_bonfire_id=doc.get("parent_bonfire_id"),
                    created_at=created_at,
                    decay_at=decay_at,
                    vanish_at=vanish_at,
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
                    "seconds": seconds,
                },
            )
            raise AppError(
                internal_code=2002,
                context={"tableName": self.COLLECTION_NAME},
                cause=e,
            ) from e

    async def try_add_fuel(self, spark_id: str, user_hash: str) -> bool:
        """Atomically add fuel to a spark if the user hasn't fueled it yet.

        This method ensures atomicity and idempotency using MongoDB transactions:
        1. Start a transaction session
        2. Insert fuel history record (idempotency check via unique index)
        3. Increment spark's fuel_count
        4. Commit transaction (or abort on any error)

        Args:
            spark_id: The spark ID to add fuel to
            user_hash: The user hash attempting to add fuel

        Returns:
            True if fuel was added (first time), False if user already fueled

        Raises:
            AppError: If database operation fails (excluding duplicate key)

        """
        # Start a session for transaction
        async with await self.db.client.start_session() as session:
            try:
                async with session.start_transaction():
                    # Step 1: Try to insert fuel history (idempotency check)
                    fuel_history_doc = {
                        "spark_id": spark_id,
                        "user_hash": user_hash,
                        "created_at": datetime.now(UTC),
                    }

                    await self.fuel_history_collection.insert_one(
                        fuel_history_doc,
                        session=session,
                    )

                    # Step 2: If insert succeeded, increment fuel_count atomically
                    await self.collection.update_one(
                        {"id": spark_id},
                        {"$inc": {"fuel_count": 1}},
                        session=session,
                    )

                    # Transaction commits automatically on context exit
                    self.logger.info(
                        LOG_EVENTS.DB_CONNECTION_SUCCESS,
                        "Fuel added successfully (transactional)",
                        context={
                            "spark_id": spark_id,
                            "user_hash": user_hash,
                        },
                    )

            except DuplicateKeyError:
                # User already fueled this spark - idempotent behavior
                # Transaction auto-aborts, no changes persisted
                self.logger.info(
                    LOG_EVENTS.DB_CONNECTION_SUCCESS,
                    "User already fueled this spark (idempotent)",
                    context={
                        "spark_id": spark_id,
                        "user_hash": user_hash,
                    },
                )
                return False

            except PyMongoError as e:
                # Transaction auto-aborts on any PyMongo error
                self.logger.exception(
                    LOG_EVENTS.DB_QUERY_ERROR,
                    "Failed to add fuel (transaction aborted)",
                    error=e,
                    context={
                        "spark_id": spark_id,
                        "user_hash": user_hash,
                    },
                )
                raise AppError(
                    internal_code=2002,
                    context={"tableName": self.FUEL_HISTORY_COLLECTION},
                    cause=e,
                ) from e

            else:
                return True

    async def get_engagement(
        self,
        spark_id: str,
        fuel_weight: int = 1,
        reply_weight: int = 5,
    ) -> SparkEngagement | None:
        """Get engagement metrics for a spark.

        Calculates unique user count and fuel count from fuel history.

        Args:
            spark_id: The spark ID to get engagement for
            fuel_weight: Weight for fuel actions in heat score calculation
            reply_weight: Weight for reply actions in heat score calculation

        Returns:
            SparkEngagement if spark exists, None otherwise

        Raises:
            AppError: If database operation fails

        """
        try:
            # Check if spark exists first
            spark_doc = await self.collection.find_one(
                {"id": spark_id},
                {"fuel_count": 1},
            )

            if spark_doc is None:
                return None

            # Count unique users from fuel history
            unique_users = await self.fuel_history_collection.count_documents(
                {"spark_id": spark_id},
            )

            fuel_count = spark_doc.get("fuel_count", 0)

            self.logger.info(
                LOG_EVENTS.DB_CONNECTION_SUCCESS,
                "Engagement metrics retrieved",
                context={
                    "spark_id": spark_id,
                    "unique_user_count": unique_users,
                    "fuel_count": fuel_count,
                },
            )

            return SparkEngagement(
                spark_id=spark_id,
                unique_user_count=unique_users,
                fuel_count=fuel_count,
                reply_count=0,  # Future feature
                fuel_weight=fuel_weight,
                reply_weight=reply_weight,
            )

        except PyMongoError as e:
            self.logger.exception(
                LOG_EVENTS.DB_QUERY_ERROR,
                "Failed to get engagement metrics",
                error=e,
                context={"spark_id": spark_id},
            )
            raise AppError(
                internal_code=2002,
                context={"tableName": self.FUEL_HISTORY_COLLECTION},
                cause=e,
            ) from e

    async def update_level(self, spark_id: str, level: SparkLevel) -> bool:
        """Update spark's promotion level.

        Args:
            spark_id: The spark ID to update
            level: New spark level

        Returns:
            True if updated successfully, False if spark not found

        Raises:
            AppError: If database operation fails

        """
        try:
            result = await self.collection.update_one(
                {"id": spark_id},
                {"$set": {"level": level.value}},
            )

            if result.matched_count == 0:
                self.logger.warning(
                    LOG_EVENTS.DB_CONNECTION_SUCCESS,
                    "Spark not found for level update",
                    context={"spark_id": spark_id},
                )
                return False

            self.logger.info(
                LOG_EVENTS.DB_CONNECTION_SUCCESS,
                "Spark level updated",
                context={
                    "spark_id": spark_id,
                    "new_level": level.value,
                },
            )
        except PyMongoError as e:
            self.logger.exception(
                LOG_EVENTS.DB_QUERY_ERROR,
                "Failed to update spark level",
                error=e,
                context={"spark_id": spark_id},
            )
            raise AppError(
                internal_code=2002,
                context={"tableName": self.COLLECTION_NAME},
                cause=e,
            ) from e
        else:
            return True

    async def update_decay_at(
        self,
        spark_id: str,
        new_decay_at: datetime,
    ) -> bool:
        """Update spark's decay_at timestamp.

        Used when promoting to kindling (TTL extension).

        Args:
            spark_id: The spark ID to update
            new_decay_at: New decay timestamp

        Returns:
            True if updated successfully, False if spark not found

        Raises:
            AppError: If database operation fails

        """
        try:
            result = await self.collection.update_one(
                {"id": spark_id},
                {"$set": {"decay_at": new_decay_at}},
            )

            if result.matched_count == 0:
                self.logger.warning(
                    LOG_EVENTS.DB_CONNECTION_SUCCESS,
                    "Spark not found for decay_at update",
                    context={"spark_id": spark_id},
                )
                return False

            self.logger.info(
                LOG_EVENTS.DB_CONNECTION_SUCCESS,
                "Spark decay_at updated",
                context={
                    "spark_id": spark_id,
                    "new_decay_at": new_decay_at.isoformat(),
                },
            )
        except PyMongoError as e:
            self.logger.exception(
                LOG_EVENTS.DB_QUERY_ERROR,
                "Failed to update spark decay_at",
                error=e,
                context={"spark_id": spark_id},
            )
            raise AppError(
                internal_code=2002,
                context={"tableName": self.COLLECTION_NAME},
                cause=e,
            ) from e
        else:
            return True

    async def find_replies_by_bonfire_id(
        self,
        bonfire_id: str,
        limit: int = 1000,
    ) -> AsyncIterator[Spark]:
        """Find all replies for a specific bonfire.

        Args:
            bonfire_id: The parent bonfire ID
            limit: Maximum number of replies to return (default 1000)

        Yields:
            Reply sparks sorted by created_at in ascending order (oldest first)

        Raises:
            AppError: If database operation fails

        """
        try:
            self.logger.info(
                LOG_EVENTS.DB_CONNECTION_SUCCESS,
                "Querying replies by bonfire ID",
                context={
                    "collection": self.COLLECTION_NAME,
                    "bonfire_id": bonfire_id,
                    "limit": limit,
                },
            )

            # Query for sparks with matching parent_bonfire_id, sorted by created_at
            cursor = self.collection.find(
                {"parent_bonfire_id": bonfire_id},
            ).sort("created_at", 1).limit(limit)

            # Yield sparks one by one (streaming, no to_list)
            count = 0
            async for doc in cursor:
                count += 1
                # MongoDB returns datetime as UTC but timezone-naive
                created_at = doc["created_at"].replace(tzinfo=UTC)
                decay_at = doc["decay_at"].replace(tzinfo=UTC)
                vanish_at = doc["vanish_at"].replace(tzinfo=UTC)

                # Parse level with fallback for legacy documents
                level_str = doc.get("level", SparkLevel.SPARK.value)
                level = SparkLevel(level_str)

                yield Spark(
                    id=doc["id"],
                    content=doc["content"],
                    user_hash=doc["user_hash"],
                    fuel_count=doc.get("fuel_count", 0),
                    level=level,
                    parent_bonfire_id=doc.get("parent_bonfire_id"),
                    created_at=created_at,
                    decay_at=decay_at,
                    vanish_at=vanish_at,
                )

            self.logger.info(
                LOG_EVENTS.DB_CONNECTION_SUCCESS,
                "Replies retrieved successfully",
                context={
                    "collection": self.COLLECTION_NAME,
                    "bonfire_id": bonfire_id,
                    "count": count,
                },
            )

        except PyMongoError as e:
            self.logger.exception(
                LOG_EVENTS.DB_QUERY_ERROR,
                f"Failed to query replies: {self.COLLECTION_NAME}",
                error=e,
                context={
                    "collection": self.COLLECTION_NAME,
                    "bonfire_id": bonfire_id,
                },
            )
            raise AppError(
                internal_code=2002,
                context={"tableName": self.COLLECTION_NAME},
                cause=e,
            ) from e

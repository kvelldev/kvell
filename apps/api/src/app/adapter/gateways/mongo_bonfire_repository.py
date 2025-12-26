"""MongoDB implementation of Bonfire Repository.

This module implements the bonfire repository using MongoDB.
"""

from collections.abc import AsyncIterator
from datetime import UTC, datetime
from typing import Any

from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import DESCENDING, IndexModel
from pymongo.errors import DuplicateKeyError, PyMongoError

from app.adapter.gateways.base_repository import BaseRepository
from app.domain.constants import LOG_EVENTS
from app.domain.exception import AppError
from app.domain.model.bonfire import Bonfire
from app.domain.repository.bonfire_repository import IBonfireRepository
from app.usecase.ports.logger import ILogger


class MongoBonfireRepository(BaseRepository, IBonfireRepository):
    """MongoDB implementation of bonfire repository."""

    COLLECTION_NAME = "bonfires"

    def __init__(self, db: AsyncIOMotorDatabase[Any], logger: ILogger) -> None:
        """Initialize the repository.

        Args:
            db: MongoDB database instance
            logger: Logger for structured logging

        """
        self.db = db
        self.collection = db[self.COLLECTION_NAME]
        self.logger = logger

    async def ensure_indexes(self) -> None:
        """Create necessary indexes for the bonfires collection.

        This should be called during application startup.
        """
        try:
            indexes = [
                # TTL index for automatic deletion when decayed
                IndexModel(
                    [("decay_at", 1)],
                    name="decay_at_ttl",
                    expireAfterSeconds=0,
                ),
                # Query index for active bonfires (by field_id, decay_at descending)
                IndexModel(
                    [("field_id", 1), ("decay_at", DESCENDING)],
                    name="field_decay_at_desc",
                ),
                # Index for looking up bonfire by spark_id
                IndexModel(
                    [("spark_id", 1)],
                    name="spark_id_idx",
                    unique=True,
                ),
            ]
            await self.collection.create_indexes(indexes)
            self.logger.info(
                LOG_EVENTS.DB_CONNECTION_SUCCESS,
                "Bonfire indexes created successfully",
                context={"collection": self.COLLECTION_NAME},
            )
        except PyMongoError as e:
            self.logger.exception(
                LOG_EVENTS.DB_QUERY_ERROR,
                "Failed to create bonfire indexes",
                error=e,
            )
            raise AppError(
                internal_code=2002,
                context={"tableName": self.COLLECTION_NAME},
                cause=e,
            ) from e

    async def save(self, bonfire: Bonfire) -> Bonfire:
        """Save a bonfire.

        Args:
            bonfire: The bonfire to save

        Returns:
            The saved bonfire

        Raises:
            AppError: If database operation fails

        """
        try:
            document = {
                "id": bonfire.id,
                "spark_id": bonfire.spark_id,
                "field_id": bonfire.field_id,
                "content": bonfire.content,
                "unique_user_count": bonfire.unique_user_count,
                "heat_score": bonfire.heat_score,
                "created_at": bonfire.created_at,
                "decay_at": bonfire.decay_at,
            }

            await self.collection.insert_one(document)

            self.logger.info(
                LOG_EVENTS.BONFIRE_CREATED,
                "Bonfire saved successfully",
                context={"bonfire_id": bonfire.id},
            )
        except DuplicateKeyError:
            # Race condition: Bonfire already created by another request.
            # This is acceptable (idempotent).
            self.logger.warning(
                LOG_EVENTS.BONFIRE_CREATED,
                "Bonfire persistence skipped (already exists)",
                context={"bonfire_id": bonfire.id},
            )
            # Proceed as if success
        except PyMongoError as e:
            self.logger.exception(
                LOG_EVENTS.DB_QUERY_ERROR,
                f"Failed to save bonfire: {self.COLLECTION_NAME}",
                error=e,
                context={"bonfire_id": bonfire.id},
            )
            raise AppError(
                internal_code=2002,
                context={"tableName": self.COLLECTION_NAME},
                cause=e,
            ) from e
        else:
            return bonfire

    async def find_by_id(self, bonfire_id: str) -> Bonfire | None:
        """Find a bonfire by ID.

        Args:
            bonfire_id: The bonfire ID to search for

        Returns:
            The bonfire if found, None otherwise

        Raises:
            AppError: If database operation fails

        """
        try:
            document: dict[str, Any] | None = await self.collection.find_one(
                {"id": bonfire_id},
            )
        except PyMongoError as e:
            self.logger.exception(
                LOG_EVENTS.DB_QUERY_ERROR,
                f"Failed to query bonfire: {self.COLLECTION_NAME}",
                error=e,
                context={"bonfire_id": bonfire_id},
            )
            raise AppError(
                internal_code=2002,
                context={"tableName": self.COLLECTION_NAME},
                cause=e,
            ) from e
        else:
            if document is None:
                return None

            return self._document_to_bonfire(document)

    async def find_by_spark_id(self, spark_id: str) -> Bonfire | None:
        """Find a bonfire by its original spark ID.

        Args:
            spark_id: The original spark ID

        Returns:
            The bonfire if found, None otherwise

        Raises:
            AppError: If database operation fails

        """
        try:
            document: dict[str, Any] | None = await self.collection.find_one(
                {"spark_id": spark_id},
            )
        except PyMongoError as e:
            self.logger.exception(
                LOG_EVENTS.DB_QUERY_ERROR,
                f"Failed to query bonfire by spark_id: {self.COLLECTION_NAME}",
                error=e,
                context={"spark_id": spark_id},
            )
            raise AppError(
                internal_code=2002,
                context={"tableName": self.COLLECTION_NAME},
                cause=e,
            ) from e
        else:
            if document is None:
                return None

            return self._document_to_bonfire(document)

    async def find_active_bonfires(self, field_id: str) -> AsyncIterator[Bonfire]:
        """Find all active (non-decayed) bonfires.

        Yields:
            Active bonfires sorted by created_at descending (newest first)

        Raises:
            AppError: If database operation fails

        """
        try:
            now = datetime.now(UTC)

            # Query for bonfires that haven't decayed yet in the specific field
            cursor = self.collection.find(
                {
                    "field_id": field_id,
                    "decay_at": {"$gt": now},
                },
            ).sort("created_at", 1)

            async for doc in cursor:
                yield self._document_to_bonfire(doc)

        except PyMongoError as e:
            self.logger.exception(
                LOG_EVENTS.DB_QUERY_ERROR,
                f"Failed to query active bonfires: {self.COLLECTION_NAME}",
                error=e,
            )
            raise AppError(
                internal_code=2002,
                context={"tableName": self.COLLECTION_NAME},
                cause=e,
            ) from e

    async def update_decay_at(
        self,
        bonfire_id: str,
        new_decay_at: datetime,
    ) -> bool:
        """Update bonfire's decay_at timestamp.

        Uses atomic update to prevent race conditions.

        Args:
            bonfire_id: The bonfire ID to update
            new_decay_at: New decay timestamp

        Returns:
            True if updated successfully, False if bonfire not found

        Raises:
            AppError: If database operation fails

        """
        try:
            result = await self.collection.update_one(
                {"id": bonfire_id},
                {"$max": {"decay_at": new_decay_at}},
            )

            if result.matched_count == 0:
                self.logger.warning(
                    LOG_EVENTS.BONFIRE_NOT_FOUND,
                    "Bonfire not found for decay_at update",
                    context={"bonfire_id": bonfire_id},
                )
                return False

            self.logger.info(
                LOG_EVENTS.BONFIRE_EXTENDED,
                "Bonfire decay_at updated",
                context={
                    "bonfire_id": bonfire_id,
                    "new_decay_at": new_decay_at.isoformat(),
                },
            )
        except PyMongoError as e:
            self.logger.exception(
                LOG_EVENTS.DB_QUERY_ERROR,
                f"Failed to update bonfire decay_at: {self.COLLECTION_NAME}",
                error=e,
                context={"bonfire_id": bonfire_id},
            )
            raise AppError(
                internal_code=2002,
                context={"tableName": self.COLLECTION_NAME},
                cause=e,
            ) from e
        else:
            return True

    async def delete_by_id(self, bonfire_id: str) -> bool:
        """Delete a bonfire by ID.

        Args:
            bonfire_id: The bonfire ID to delete

        Returns:
            True if deleted successfully, False if not found

        Raises:
            AppError: If database operation fails

        """
        try:
            result = await self.collection.delete_one({"id": bonfire_id})

            if result.deleted_count == 0:
                return False

            self.logger.info(
                LOG_EVENTS.BONFIRE_DECAYED,
                "Bonfire deleted",
                context={"bonfire_id": bonfire_id},
            )
        except PyMongoError as e:
            self.logger.exception(
                LOG_EVENTS.DB_QUERY_ERROR,
                f"Failed to delete bonfire: {self.COLLECTION_NAME}",
                error=e,
                context={"bonfire_id": bonfire_id},
            )
            raise AppError(
                internal_code=2002,
                context={"tableName": self.COLLECTION_NAME},
                cause=e,
            ) from e
        else:
            return True

    def _document_to_bonfire(self, document: dict[str, Any]) -> Bonfire:
        """Convert MongoDB document to Bonfire entity.

        Args:
            document: MongoDB document

        Returns:
            Bonfire entity

        """
        # MongoDB returns datetime as UTC but timezone-naive
        created_at = self._ensure_utc(document["created_at"])
        decay_at = self._ensure_utc(document["decay_at"])

        return Bonfire(
            id=document["id"],
            spark_id=document["spark_id"],
            field_id=document["field_id"],
            content=document["content"],
            unique_user_count=document["unique_user_count"],
            heat_score=document["heat_score"],
            created_at=created_at,
            decay_at=decay_at,
        )

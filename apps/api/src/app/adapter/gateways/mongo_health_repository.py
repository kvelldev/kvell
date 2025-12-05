"""MongoDB implementation of Health Repository.

This module implements the health repository using MongoDB.
"""

from typing import Any

from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.errors import PyMongoError

from app.domain.constants import LOG_EVENTS
from app.domain.exception import AppError
from app.domain.model.health_message import HealthMessage
from app.domain.repository.health_repository import IHealthRepository
from app.usecase.ports.logger import ILogger


class MongoHealthRepository(IHealthRepository):
    """MongoDB implementation of health repository."""

    COLLECTION_NAME = "health_messages"

    def __init__(self, db: AsyncIOMotorDatabase[Any], logger: ILogger) -> None:
        """Initialize the repository.

        Args:
            db: MongoDB database instance
            logger: Logger for structured logging

        """
        self.collection = db[self.COLLECTION_NAME]
        self.logger = logger

    async def save(self, message: HealthMessage) -> HealthMessage:
        """Save a health message.

        Args:
            message: The health message to save

        Returns:
            The saved health message

        Raises:
            AppError: If database operation fails

        """
        try:
            self.logger.info(
                LOG_EVENTS.DB_CONNECTION_SUCCESS,
                "Saving health message to MongoDB",
                context={
                    "collection": self.COLLECTION_NAME,
                    "message_id": message.id,
                },
            )

            document = {
                "id": message.id,
                "message": message.message,
                "created_at": message.created_at,
            }

            await self.collection.insert_one(document)

            self.logger.info(
                LOG_EVENTS.DB_CONNECTION_SUCCESS,
                "Health message saved successfully",
                context={"message_id": message.id},
            )
        except PyMongoError as e:
            self.logger.exception(
                LOG_EVENTS.DB_QUERY_ERROR,
                f"Failed to save health message: {self.COLLECTION_NAME}",
                error=e,
                context={
                    "collection": self.COLLECTION_NAME,
                    "message_id": message.id,
                },
            )
            raise AppError(
                internal_code=2002,
                context={"tableName": self.COLLECTION_NAME},
                cause=e,
            ) from e
        else:
            return message

    async def find_latest(self) -> HealthMessage | None:
        """Find the latest health message.

        Returns:
            The latest health message, or None if not found

        Raises:
            AppError: If database operation fails

        """
        try:
            self.logger.info(
                LOG_EVENTS.DB_CONNECTION_SUCCESS,
                "Querying latest health message",
                context={"collection": self.COLLECTION_NAME},
            )

            document: dict[str, Any] | None = await self.collection.find_one(
                sort=[("created_at", -1)],
            )
        except PyMongoError as e:
            self.logger.exception(
                LOG_EVENTS.DB_QUERY_ERROR,
                f"Failed to query health message: {self.COLLECTION_NAME}",
                error=e,
                context={"collection": self.COLLECTION_NAME},
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
                    "No health message found",
                    context={"collection": self.COLLECTION_NAME},
                )
                return None

            self.logger.info(
                LOG_EVENTS.DB_CONNECTION_SUCCESS,
                "Health message retrieved successfully",
                context={
                    "collection": self.COLLECTION_NAME,
                    "message_id": document["id"],
                },
            )

            return HealthMessage(
                id=document["id"],
                message=document["message"],
                created_at=document["created_at"],
            )

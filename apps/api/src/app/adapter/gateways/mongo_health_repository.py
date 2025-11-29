"""MongoDB implementation of Health Repository.

This module implements the health repository using MongoDB.
"""

from typing import Any

from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.errors import PyMongoError

from app.domain.exception import AppError
from app.domain.model.health_message import HealthMessage
from app.domain.repository.health_repository import IHealthRepository


class MongoHealthRepository(IHealthRepository):
    """MongoDB implementation of health repository."""

    COLLECTION_NAME = "health_messages"

    def __init__(self, db: AsyncIOMotorDatabase[Any]) -> None:
        """Initialize the repository.

        Args:
            db: MongoDB database instance

        """
        self.collection = db[self.COLLECTION_NAME]

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
            document = {
                "id": message.id,
                "message": message.message,
                "created_at": message.created_at,
            }

            await self.collection.insert_one(document)
        except PyMongoError as e:
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
            document: dict[str, Any] | None = await self.collection.find_one(
                sort=[("created_at", -1)],
            )
        except PyMongoError as e:
            raise AppError(
                internal_code=2002,
                context={"tableName": self.COLLECTION_NAME},
                cause=e,
            ) from e
        else:
            if document is None:
                return None

            return HealthMessage(
                id=document["id"],
                message=document["message"],
                created_at=document["created_at"],
            )

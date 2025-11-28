"""MongoDB implementation of Health Repository.

This module implements the health repository using MongoDB.
"""

from domain.model.health_message import HealthMessage
from domain.repository.health_repository import IHealthRepository
from motor.motor_asyncio import AsyncIOMotorDatabase


class MongoHealthRepository(IHealthRepository):
    """MongoDB implementation of health repository."""

    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        """Initialize the repository.

        Args:
            db: MongoDB database instance

        """
        self.collection = db["health_messages"]

    async def save(self, message: HealthMessage) -> HealthMessage:
        """Save a health message.

        Args:
            message: The health message to save

        Returns:
            The saved health message

        """
        document = {
            "id": message.id,
            "message": message.message,
            "created_at": message.created_at,
        }

        await self.collection.insert_one(document)
        return message

    async def find_latest(self) -> HealthMessage | None:
        """Find the latest health message.

        Returns:
            The latest health message, or None if not found

        """
        document = await self.collection.find_one(
            sort=[("created_at", -1)],
        )

        if document is None:
            return None

        return HealthMessage(
            id=document["id"],
            message=document["message"],
            created_at=document["created_at"],
        )

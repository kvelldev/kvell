"""Database configuration and connection management.

This module manages MongoDB connection using Motor.
"""

from typing import Any

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.adapter.infra.settings import settings


class Database:
    """MongoDB database connection manager."""

    client: AsyncIOMotorClient[Any] | None = None
    db: AsyncIOMotorDatabase[Any] | None = None

    @classmethod
    def connect(cls) -> None:
        """Establish connection to MongoDB."""
        cls.client = AsyncIOMotorClient(settings.mongo_uri)
        cls.db = cls.client[settings.mongo_db]

    @classmethod
    def disconnect(cls) -> None:
        """Close connection to MongoDB."""
        if cls.client:
            cls.client.close()

    @classmethod
    def get_database(cls) -> AsyncIOMotorDatabase[Any]:
        """Get the database instance.

        Returns:
            MongoDB database instance

        Raises:
            RuntimeError: If database is not connected

        """
        if cls.db is None:
            msg = "Database not connected. Call connect() first."
            raise RuntimeError(msg)
        return cls.db

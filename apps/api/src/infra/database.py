"""Database configuration and connection management.

This module manages MongoDB connection using Motor.
"""

import os

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase


class Database:
    """MongoDB database connection manager."""

    client: AsyncIOMotorClient | None = None
    db: AsyncIOMotorDatabase | None = None

    @classmethod
    def connect(cls) -> None:
        """Establish connection to MongoDB."""
        mongo_uri = os.getenv(
            "MONGO_URI",
            "mongodb://localhost:27017",
        )
        mongo_db = os.getenv("MONGO_DB", "kvell")

        cls.client = AsyncIOMotorClient(mongo_uri)
        cls.db = cls.client[mongo_db]

    @classmethod
    def disconnect(cls) -> None:
        """Close connection to MongoDB."""
        if cls.client:
            cls.client.close()

    @classmethod
    def get_database(cls) -> AsyncIOMotorDatabase:
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

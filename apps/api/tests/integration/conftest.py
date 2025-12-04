"""Integration Test Configuration.

This module provides pytest fixtures for integration testing with real MongoDB.
Fixtures manage database connection, cleanup, and dependency injection.
"""

from collections.abc import AsyncIterator, Iterator
from typing import Any

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo import MongoClient

from app.adapter.entrypoints.dependencies import get_db
from app.adapter.infra.database import Database
from app.main import app


@pytest.fixture(scope="session")
def test_db_name() -> str:
    """Provide the test database name.

    Returns:
        Test database name

    """
    return "kvell_test"


@pytest.fixture(scope="session")
def mongo_client_sync() -> Iterator[MongoClient[Any]]:
    """Create a synchronous MongoDB client for testing.

    This fixture is session-scoped to reuse the connection across tests.
    Used for database cleanup operations which need to run synchronously.

    Yields:
        Synchronous MongoDB client instance

    """
    client: MongoClient[Any] = MongoClient("mongodb://localhost:27017")
    yield client
    client.close()


@pytest_asyncio.fixture(scope="function")
async def mongo_client() -> AsyncIterator[AsyncIOMotorClient[Any]]:
    """Create an async MongoDB client for testing.

    This fixture is function-scoped to avoid event loop issues.

    Yields:
        MongoDB client instance

    """
    client: AsyncIOMotorClient[Any] = AsyncIOMotorClient("mongodb://localhost:27017")
    yield client
    client.close()


@pytest_asyncio.fixture(scope="function")
async def test_database(
    mongo_client: AsyncIOMotorClient[Any], test_db_name: str
) -> AsyncIOMotorDatabase[Any]:
    """Provide the test database instance.

    This fixture is function-scoped to avoid event loop issues.

    Args:
        mongo_client: MongoDB client (injected)
        test_db_name: Test database name (injected)

    Returns:
        Test database instance

    """
    return mongo_client[test_db_name]


@pytest.fixture(autouse=False)
def clean_db(mongo_client_sync: MongoClient[Any], test_db_name: str) -> None:
    """Clean the database before each test.

    This fixture runs BEFORE each test function to ensure a clean state.
    We don't clean after tests to allow debugging of test data.
    Uses synchronous pymongo to avoid event loop issues.

    Args:
        mongo_client_sync: Synchronous MongoDB client (injected)
        test_db_name: Test database name (injected)

    """
    # Clean before test using synchronous client
    test_db = mongo_client_sync[test_db_name]
    collection_names = test_db.list_collection_names()
    for collection_name in collection_names:
        test_db[collection_name].drop()

    # Note: We don't clean after the test for debuggability


@pytest_asyncio.fixture
async def test_client(
    test_database: AsyncIOMotorDatabase[Any], clean_db: None
) -> AsyncIterator[AsyncClient]:
    """Create a FastAPI async test client with real database.

    This fixture overrides the get_db dependency to use the test database
    instead of the production database.

    Args:
        test_database: Test database instance (injected)
        clean_db: Ensures database is cleaned before test (dependency only)

    Yields:
        HTTPX AsyncClient for testing FastAPI app

    """
    # Ensure clean_db fixture has run (fixture dependency)
    _ = clean_db

    # Initialize Database singleton (required for app lifespan)
    Database.connect()

    # Override the database dependency to use test database
    def override_get_db() -> AsyncIOMotorDatabase[Any]:
        return test_database

    app.dependency_overrides[get_db] = override_get_db

    # Create client with lifespan disabled (we manage DB connection ourselves)
    async with AsyncClient(
        transport=ASGITransport(app=app, raise_app_exceptions=False),
        base_url="http://test",
    ) as client:
        yield client

    # Clean up
    app.dependency_overrides.clear()
    Database.disconnect()

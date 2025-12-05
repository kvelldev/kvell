"""Integration tests for Spark Router.

These tests verify the entire stack from API endpoint to MongoDB and Redis,
including Repository and Rate Limiter behavior.

Unlike unit tests which mock dependencies, these tests:
- Use real MongoDB connection
- Use real Redis connection
- Test actual database read/write operations
- Test actual rate limiting behavior
- Verify error mapping (AppError → HTTP errors)
- Validate multi-layer integration
"""

from typing import Any

import pytest
from fastapi import status
from httpx import AsyncClient
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.adapter.gateways.mongo_spark_repository import MongoSparkRepository
from app.adapter.infra.settings import settings


class TestSparkRouterIntegration:
    """Integration tests for spark API endpoints."""

    @pytest.fixture
    def collection(
        self, test_database: AsyncIOMotorDatabase[Any]
    ) -> Any:  # AsyncIOMotorCollection
        """Get the sparks collection from test database.

        Args:
            test_database: Test database instance (injected)

        Returns:
            MongoDB collection for sparks

        """
        return test_database[MongoSparkRepository.COLLECTION_NAME]

    @pytest.mark.asyncio
    async def test_postSpark_whenCalledWithValidContent_savesToDbAndReturns201(
        self,
        test_client: AsyncClient,
        collection: Any,
    ) -> None:
        """
        Action: postSpark (POST /api/sparks)
        Condition: whenCalledWithValidContent (valid request body)
        Result: savesToDbAndReturns201 (saves to MongoDB and returns 201)
        """
        # Arrange
        request_body = {"content": "This is a test spark"}

        # Act
        response = await test_client.post("/api/sparks", json=request_body)

        # Assert HTTP response
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["content"] == "This is a test spark"
        assert "id" in data
        assert "created_at" in data

        # Assert database persistence (verify Repository layer)
        doc = await collection.find_one({"id": data["id"]})
        assert doc is not None
        assert doc["content"] == "This is a test spark"
        assert doc["id"] == data["id"]
        assert doc["fuel_count"] == 0  # Default value
        assert "user_hash" in doc
        assert "visible_until" in doc
        assert "expire_at" in doc

    @pytest.mark.asyncio
    async def test_postSpark_whenContentExceedsMaxLength_returns422(
        self,
        test_client: AsyncClient,
        collection: Any,
    ) -> None:
        """
        Action: postSpark
        Condition: whenContentExceedsMaxLength (content exceeds max_length)
        Result: returns422 (validation error)
        """
        # Arrange: Create content exceeding max_length
        request_body = {"content": "x" * (settings.spark_max_length + 1)}

        # Act
        response = await test_client.post("/api/sparks", json=request_body)

        # Assert HTTP response
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        data = response.json()
        assert data["error"]["code"] == 1003

        # Assert: No document saved to DB
        count = await collection.count_documents({})
        assert count == 0

    @pytest.mark.asyncio
    async def test_postSpark_whenContentContainsNgWord_returns422(
        self,
        test_client: AsyncClient,
        collection: Any,
    ) -> None:
        """
        Action: postSpark
        Condition: whenContentContainsNgWord (content contains NG word)
        Result: returns422 (NG word validation error)
        """
        # Arrange: Use first NG word from settings
        ng_word = settings.spark_ng_words_list[0]
        request_body = {"content": f"This contains {ng_word.upper()} in text"}

        # Act
        response = await test_client.post("/api/sparks", json=request_body)

        # Assert HTTP response
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        data = response.json()
        assert data["error"]["code"] == 1002

        # Assert: No document saved to DB
        count = await collection.count_documents({})
        assert count == 0

    @pytest.mark.asyncio
    async def test_postSpark_whenRateLimitExceeded_returns429(
        self,
        test_client: AsyncClient,
        collection: Any,
    ) -> None:
        """
        Action: postSpark
        Condition: whenRateLimitExceeded (exceeds rate limit within window)
        Result: returns429 (rate limit error)
        """
        # Arrange: Use rate limit from settings
        # Note: Redis is initialized via test_client fixture dependency
        rate_limit = settings.spark_rate_limit_count
        request_body = {"content": "Rate limit test spark"}

        # Act: Post up to rate limit (should all succeed)
        for i in range(rate_limit):
            response = await test_client.post("/api/sparks", json=request_body)
            assert response.status_code == status.HTTP_201_CREATED, f"Request {i+1} failed"

        # Act: One more post should be rate limited
        response = await test_client.post("/api/sparks", json=request_body)

        # Assert HTTP response
        assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
        data = response.json()
        assert data["error"]["code"] == 1004

        # Assert: Only rate_limit documents saved to DB (not more)
        count = await collection.count_documents({})
        assert count == rate_limit

    @pytest.mark.asyncio
    async def test_postSpark_whenEmptyContent_returns422(
        self,
        test_client: AsyncClient,
        collection: Any,
    ) -> None:
        """
        Action: postSpark
        Condition: whenEmptyContent (empty string)
        Result: returns422 (validation error from Pydantic)
        """
        # Arrange
        request_body = {"content": ""}

        # Act
        response = await test_client.post("/api/sparks", json=request_body)

        # Assert HTTP response (Pydantic validation error)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        # Assert: No document saved to DB
        count = await collection.count_documents({})
        assert count == 0

    @pytest.mark.asyncio
    async def test_postSpark_whenCalledMultipleTimes_allSparksSavedWithCorrectFuelCount(
        self,
        test_client: AsyncClient,
        collection: Any,
    ) -> None:
        """
        Action: postSpark
        Condition: whenCalledMultipleTimes (3 POST requests)
        Result: allSparksSavedWithCorrectFuelCount (all sparks have fuel_count=0)
        """
        # Arrange
        sparks = ["First spark", "Second spark", "Third spark"]

        # Act: Save 3 sparks
        saved_ids: list[str] = []
        for spark_content in sparks:
            response = await test_client.post(
                "/api/sparks", json={"content": spark_content}
            )
            assert response.status_code == status.HTTP_201_CREATED
            saved_ids.append(response.json()["id"])

        # Assert: All 3 sparks are in DB
        count = await collection.count_documents({})
        assert count == 3

        # Verify all IDs exist with fuel_count=0
        for saved_id in saved_ids:
            doc = await collection.find_one({"id": saved_id})
            assert doc is not None
            assert doc["fuel_count"] == 0

    @pytest.mark.asyncio
    async def test_postSpark_whenContentAtMaxLength_savesSuccessfully(
        self,
        test_client: AsyncClient,
        collection: Any,
    ) -> None:
        """
        Action: postSpark
        Condition: whenContentAtMaxLength (exactly at max_length)
        Result: savesSuccessfully (boundary condition test)
        """
        # Arrange: Exactly at max_length
        request_body = {"content": "x" * settings.spark_max_length}

        # Act
        response = await test_client.post("/api/sparks", json=request_body)

        # Assert HTTP response
        assert response.status_code == status.HTTP_201_CREATED

        # Assert: Document saved to DB
        count = await collection.count_documents({})
        assert count == 1

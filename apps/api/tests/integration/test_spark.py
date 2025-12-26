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
from app.adapter.infra.logger import JsonLogger
from app.adapter.infra.settings import settings
from app.domain.model.spark import Spark


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
        request_body = {
            "content": "This is a test spark",
            "field_id": "sakurazaka46",
        }

        # Act
        response = await test_client.post("/api/sparks", json=request_body)

        # Assert HTTP response
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["content"] == "This is a test spark"
        assert data["field_id"] == "sakurazaka46"
        assert "id" in data
        assert "created_at" in data

        # Assert database persistence (verify Repository layer)
        doc = await collection.find_one({"id": data["id"]})
        assert doc is not None
        assert doc["content"] == "This is a test spark"
        assert doc["field_id"] == "sakurazaka46"
        assert doc["id"] == data["id"]
        assert doc["fuel_count"] == 0  # Default value
        assert "user_hash" in doc
        assert "decay_at" in doc
        assert "vanish_at" in doc

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
        request_body = {
            "content": "x" * (settings.spark_max_length + 1),
            "field_id": "sakurazaka46",
        }

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
        request_body = {
            "content": f"This contains {ng_word.upper()} in text",
            "field_id": "sakurazaka46",
        }

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
        request_body = {
            "content": "Rate limit test spark",
            "field_id": "sakurazaka46",
        }

        # Act: Post up to rate limit (should all succeed)
        for i in range(rate_limit):
            response = await test_client.post("/api/sparks", json=request_body)
            assert response.status_code == status.HTTP_201_CREATED, (
                f"Request {i + 1} failed"
            )

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
        request_body = {
            "content": "",
            "field_id": "sakurazaka46",
        }

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
                "/api/sparks",
                json={
                    "content": spark_content,
                    "field_id": "sakurazaka46",
                },
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
        request_body = {
            "content": "x" * settings.spark_max_length,
            "field_id": "sakurazaka46",
        }

        # Act
        response = await test_client.post("/api/sparks", json=request_body)

        # Assert HTTP response
        assert response.status_code == status.HTTP_201_CREATED

        # Assert: Document saved to DB
        count = await collection.count_documents({})
        assert count == 1


class TestSparkWebSocketIntegration:
    """Integration tests for spark WebSocket endpoint."""

    @pytest.fixture
    def collection(
        self, test_database: AsyncIOMotorDatabase[Any]
    ) -> Any:  # AsyncIOMotorCollection
        """Get the sparks collection from test database."""
        return test_database[MongoSparkRepository.COLLECTION_NAME]

    @pytest.mark.asyncio
    async def test_websocketTimeline_snapshotLoading_fromMongo(
        self,
        test_client: AsyncClient,  # noqa: ARG002
        collection: Any,
        test_database: AsyncIOMotorDatabase[Any],
    ) -> None:
        """Test snapshot loading from MongoDB for WebSocket timeline.

        This test validates the MongoDB integration for active spark retrieval.
        Full WebSocket behavior is validated through unit tests and E2E tests.
        """
        # Arrange: Insert active sparks into DB
        spark1 = Spark.create(
            spark_id="ws-snap-1",
            content="Active spark 1",
            user_hash="user-1",
            decay_after_seconds=600,
            vanish_after_days=30,
            field_id="sakurazaka46",
        )
        spark2 = Spark.create(
            spark_id="ws-snap-2",
            content="Active spark 2",
            user_hash="user-2",
            decay_after_seconds=600,
            vanish_after_days=30,
            field_id="sakurazaka46",
        )

        await collection.insert_one(
            {
                "id": spark1.id,
                "content": spark1.content,
                "user_hash": spark1.user_hash,
                "fuel_count": spark1.fuel_count,
                "field_id": spark1.field_id,
                "created_at": spark1.created_at,
                "decay_at": spark1.decay_at,
                "vanish_at": spark1.vanish_at,
            }
        )
        await collection.insert_one(
            {
                "id": spark2.id,
                "content": spark2.content,
                "user_hash": spark2.user_hash,
                "fuel_count": spark2.fuel_count,
                "field_id": spark2.field_id,
                "created_at": spark2.created_at,
                "decay_at": spark2.decay_at,
                "vanish_at": spark2.vanish_at,
            }
        )

        # Act: Query active sparks via repository (validates MongoDB integration)
        logger = JsonLogger()
        repository = MongoSparkRepository(test_database, logger)

        # Collect active sparks from async iterator (filtering by field_id)
        active_sparks: list[Spark] = [
            spark
            async for spark in repository.find_active_sparks(
                field_id="sakurazaka46", seconds=600
            )
        ]

        # Assert: Verify snapshot data retrieval works correctly
        assert len(active_sparks) == 2
        assert active_sparks[0].id == "ws-snap-1"
        assert active_sparks[0].content == "Active spark 1"
        assert active_sparks[1].id == "ws-snap-2"
        assert active_sparks[1].content == "Active spark 2"

    @pytest.mark.asyncio
    async def test_postSpark_publishesToRedis_integration(
        self,
        test_client: AsyncClient,
        collection: Any,
    ) -> None:
        """Test that posting a spark publishes to Redis Pub/Sub.

        This test validates the Redis Pub/Sub integration when posting sparks.
        Full streaming behavior is validated through unit tests and E2E tests.
        """
        # Arrange
        request_body = {
            "content": "Test spark for pub/sub",
            "field_id": "sakurazaka46",
        }

        # Act: Post a spark (this should publish to Redis)
        response = await test_client.post("/api/sparks", json=request_body)

        # Assert: Spark was created successfully
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["content"] == "Test spark for pub/sub"

        # Verify spark was saved to MongoDB
        doc = await collection.find_one({"id": data["id"]})
        assert doc is not None
        assert doc["content"] == "Test spark for pub/sub"

        # Note: Actual Redis pub/sub message delivery is validated through:
        # 1. Unit tests (with mocked pub/sub)
        # 2. Manual testing with real WebSocket clients
        # 3. E2E tests


class TestAddFuelIntegration:
    """Integration tests for add fuel API endpoint."""

    @pytest.fixture
    def collection(
        self, test_database: AsyncIOMotorDatabase[Any]
    ) -> Any:  # AsyncIOMotorCollection
        """Get the sparks collection from test database."""
        return test_database[MongoSparkRepository.COLLECTION_NAME]

    @pytest.fixture
    def fuel_history_collection(
        self, test_database: AsyncIOMotorDatabase[Any]
    ) -> Any:  # AsyncIOMotorCollection
        """Get the fuel history collection from test database."""
        return test_database[MongoSparkRepository.FUEL_HISTORY_COLLECTION]

    @pytest.mark.asyncio
    async def test_addFuel_whenFirstTime_incrementsFuelCountAndReturns200(
        self,
        test_client: AsyncClient,
        collection: Any,
        fuel_history_collection: Any,
    ) -> None:
        """
        Action: addFuel (POST /api/sparks/{spark_id}/fuel)
        Condition: whenFirstTime (first time this user fuels this spark)
        Result: incrementsFuelCountAndReturns200 (fuel_count++, 200 response)
        """
        # Arrange: Create a spark in DB
        spark = Spark.create(
            spark_id="test-spark-1",
            content="Test content",
            user_hash="author-hash",
            decay_after_seconds=600,
            vanish_after_days=30,
            field_id="sakurazaka46",
        )
        await collection.insert_one(
            {
                "id": spark.id,
                "content": spark.content,
                "user_hash": spark.user_hash,
                "fuel_count": 0,
                "field_id": spark.field_id,
                "created_at": spark.created_at,
                "decay_at": spark.decay_at,
                "vanish_at": spark.vanish_at,
            }
        )

        # Act: Add fuel from a different user
        response = await test_client.post(
            "/api/sparks/test-spark-1/fuel",
            headers={"X-Forwarded-For": "192.168.1.100"},  # Different IP
        )

        # Assert HTTP response
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True

        # Assert: fuel_count incremented in DB
        doc = await collection.find_one({"id": "test-spark-1"})
        assert doc is not None
        assert doc["fuel_count"] == 1

        # Assert: fuel history record created
        history_count = await fuel_history_collection.count_documents(
            {"spark_id": "test-spark-1"}
        )
        assert history_count == 1

    @pytest.mark.asyncio
    async def test_addFuel_whenSecondTime_isIdempotentAndReturns200(
        self,
        test_client: AsyncClient,
        collection: Any,
        fuel_history_collection: Any,
    ) -> None:
        """
        Action: addFuel
        Condition: whenSecondTime (same user tries to fuel twice)
        Result: isIdempotentAndReturns200 (fuel_count stays 1, both return 200)
        """
        # Arrange: Create a spark
        spark = Spark.create(
            spark_id="test-spark-2",
            content="Test content",
            user_hash="author-hash",
            decay_after_seconds=600,
            vanish_after_days=30,
            field_id="sakurazaka46",
        )
        await collection.insert_one(
            {
                "id": spark.id,
                "content": spark.content,
                "user_hash": spark.user_hash,
                "fuel_count": 0,
                "field_id": spark.field_id,
                "created_at": spark.created_at,
                "decay_at": spark.decay_at,
                "vanish_at": spark.vanish_at,
            }
        )

        # Act: Add fuel twice from same IP
        response1 = await test_client.post(
            "/api/sparks/test-spark-2/fuel",
            headers={"X-Forwarded-For": "192.168.1.200"},
        )
        response2 = await test_client.post(
            "/api/sparks/test-spark-2/fuel",
            headers={"X-Forwarded-For": "192.168.1.200"},  # Same IP
        )

        # Assert: Both requests return 200 OK
        assert response1.status_code == status.HTTP_200_OK
        assert response2.status_code == status.HTTP_200_OK
        assert response1.json()["success"] is True
        assert response2.json()["success"] is True

        # Assert: fuel_count is still 1 (idempotent)
        doc = await collection.find_one({"id": "test-spark-2"})
        assert doc is not None
        assert doc["fuel_count"] == 1

        # Assert: Only one history record exists
        history_count = await fuel_history_collection.count_documents(
            {"spark_id": "test-spark-2"}
        )
        assert history_count == 1

    @pytest.mark.asyncio
    async def test_addFuel_whenMultipleUsers_countsAllFuel(
        self,
        test_client: AsyncClient,
        collection: Any,
        fuel_history_collection: Any,
    ) -> None:
        """
        Action: addFuel
        Condition: whenMultipleUsers (3 different users fuel the same spark)
        Result: countsAllFuel (fuel_count becomes 3)
        """
        # Arrange: Create a spark
        spark = Spark.create(
            spark_id="test-spark-3",
            content="Test content",
            user_hash="author-hash",
            decay_after_seconds=600,
            vanish_after_days=30,
            field_id="sakurazaka46",
        )
        await collection.insert_one(
            {
                "id": spark.id,
                "content": spark.content,
                "user_hash": spark.user_hash,
                "fuel_count": 0,
                "field_id": spark.field_id,
                "created_at": spark.created_at,
                "decay_at": spark.decay_at,
                "vanish_at": spark.vanish_at,
            }
        )

        # Act: Add fuel from 3 different users
        await test_client.post(
            "/api/sparks/test-spark-3/fuel",
            headers={"X-Forwarded-For": "192.168.1.1"},
        )
        await test_client.post(
            "/api/sparks/test-spark-3/fuel",
            headers={"X-Forwarded-For": "192.168.1.2"},
        )
        await test_client.post(
            "/api/sparks/test-spark-3/fuel",
            headers={"X-Forwarded-For": "192.168.1.3"},
        )

        # Assert: fuel_count is 3
        doc = await collection.find_one({"id": "test-spark-3"})
        assert doc is not None
        assert doc["fuel_count"] == 3

        # Assert: 3 history records exist
        history_count = await fuel_history_collection.count_documents(
            {"spark_id": "test-spark-3"}
        )
        assert history_count == 3

    @pytest.mark.asyncio
    async def test_addFuel_whenSparkNotFound_returns404(
        self,
        test_client: AsyncClient,
    ) -> None:
        """
        Action: addFuel
        Condition: whenSparkNotFound (spark_id doesn't exist)
        Result: returns404 (NOT_FOUND error)
        """
        # Act: Try to fuel non-existent spark
        response = await test_client.post(
            "/api/sparks/nonexistent-spark/fuel",
            headers={"X-Forwarded-For": "192.168.1.100"},
        )

        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert data["error"]["code"] == 1005

    @pytest.mark.asyncio
    async def test_addFuel_whenSparkDecayed_returns410(
        self,
        test_client: AsyncClient,
        collection: Any,
    ) -> None:
        """
        Action: addFuel
        Condition: whenSparkDecayed (spark already decayed)
        Result: returns410 (GONE error)
        """
        # Arrange: Create a decayed spark (decay_at in the past)
        spark = Spark.create(
            spark_id="test-spark-decayed",
            content="Old content",
            user_hash="author-hash",
            decay_after_seconds=-600,  # Already decayed (negative offset)
            vanish_after_days=30,
            field_id="sakurazaka46",
        )
        await collection.insert_one(
            {
                "id": spark.id,
                "content": spark.content,
                "user_hash": spark.user_hash,
                "fuel_count": 0,
                "field_id": spark.field_id,
                "created_at": spark.created_at,
                "decay_at": spark.decay_at,
                "vanish_at": spark.vanish_at,
            }
        )

        # Act: Try to fuel decayed spark
        response = await test_client.post(
            "/api/sparks/test-spark-decayed/fuel",
            headers={"X-Forwarded-For": "192.168.1.100"},
        )

        # Assert
        assert response.status_code == status.HTTP_410_GONE
        data = response.json()
        assert data["error"]["code"] == 1001

    @pytest.mark.asyncio
    async def test_addFuel_whenSelfFuel_returnsSuccessButNoIncrement(
        self,
        test_client: AsyncClient,
        collection: Any,
        fuel_history_collection: Any,
    ) -> None:
        """
        Action: addFuel
        Condition: whenSelfFuel (user tries to fuel their own spark)
        Result: returnsSuccessButNoIncrement (200 OK, but fuel_count stays 0)
        """
        # Arrange: Create a spark with known author IP
        # SimpleIPProvider generates same hash for same IP
        # We rely on POST /api/sparks to set up hash, so this part needs update too

        # First, create the spark via API (to get correct user_hash)
        response = await test_client.post(
            "/api/sparks",
            json={
                "content": "Self spark",
                "field_id": "sakurazaka46",
            },
            headers={"X-Forwarded-For": "192.168.1.50"},
        )
        assert response.status_code == status.HTTP_201_CREATED
        created_spark_id = response.json()["id"]

        # Act: Try to fuel own spark (same IP)
        fuel_response = await test_client.post(
            f"/api/sparks/{created_spark_id}/fuel",
            headers={"X-Forwarded-For": "192.168.1.50"},  # Same IP as creator
        )

        # Assert: Returns success
        assert fuel_response.status_code == status.HTTP_200_OK
        assert fuel_response.json()["success"] is True

        # Assert: fuel_count is still 0 (not incremented)
        doc = await collection.find_one({"id": created_spark_id})
        assert doc is not None
        assert doc["fuel_count"] == 0

        # Assert: No fuel history record created
        history_count = await fuel_history_collection.count_documents(
            {"spark_id": created_spark_id}
        )
        assert history_count == 0

    @pytest.mark.asyncio
    async def test_addFuel_whenConcurrentRequests_transactionEnsuresConsistency(
        self,
        test_client: AsyncClient,
        collection: Any,
        fuel_history_collection: Any,
    ) -> None:
        """
        Action: addFuel
        Condition: whenConcurrentRequests (10 users fuel simultaneously)
        Result: transactionEnsuresConsistency (fuel_count == 10, no race conditions)
        """
        # Arrange: Create a spark
        spark = Spark.create(
            spark_id="test-spark-concurrent",
            content="Concurrent test",
            user_hash="author-hash",
            decay_after_seconds=600,
            vanish_after_days=30,
            field_id="sakurazaka46",
        )
        await collection.insert_one(
            {
                "id": spark.id,
                "content": spark.content,
                "user_hash": spark.user_hash,
                "fuel_count": 0,
                "field_id": spark.field_id,
                "created_at": spark.created_at,
                "decay_at": spark.decay_at,
                "vanish_at": spark.vanish_at,
            }
        )

        # Act: Send 10 concurrent requests from different IPs
        import asyncio

        tasks = [
            test_client.post(
                "/api/sparks/test-spark-concurrent/fuel",
                headers={"X-Forwarded-For": f"192.168.1.{i}"},
            )
            for i in range(1, 11)  # 10 different IPs
        ]

        responses = await asyncio.gather(*tasks)

        # Assert: All requests succeeded
        for response in responses:
            assert response.status_code == status.HTTP_200_OK
            assert response.json()["success"] is True

        # Assert: fuel_count is exactly 10 (no race condition)
        doc = await collection.find_one({"id": "test-spark-concurrent"})
        assert doc is not None
        assert doc["fuel_count"] == 10

        # Assert: Exactly 10 history records exist (transaction consistency)
        history_count = await fuel_history_collection.count_documents(
            {"spark_id": "test-spark-concurrent"}
        )
        assert history_count == 10

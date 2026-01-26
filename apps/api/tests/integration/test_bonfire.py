"""Integration tests for Bonfire Promotion Logic.

These tests verify the Spark to Bonfire promotion flow:
- Spark → Kindling (UU >= 3)
- Kindling → Bonfire (UU >= threshold AND heat_score >= 50)
- Anti-troll logic (1vs1 cannot promote)
- Bonfire TTL extension
- Get active bonfires

Tests use real MongoDB and Redis connections.
"""

from datetime import UTC, datetime, timedelta
from typing import Any

import pytest
from fastapi import status
from httpx import AsyncClient
from motor.motor_asyncio import AsyncIOMotorDatabase
from redis.asyncio import Redis

from app.adapter.gateways.mongo_bonfire_repository import MongoBonfireRepository
from app.adapter.gateways.mongo_spark_repository import MongoSparkRepository
from app.domain.model.spark import Spark, SparkLevel


class TestBonfirePromotionIntegration:
    """Integration tests for bonfire promotion logic."""

    @pytest.fixture
    def spark_collection(
        self, test_database: AsyncIOMotorDatabase[Any]
    ) -> Any:
        """Get the sparks collection from test database."""
        return test_database[MongoSparkRepository.COLLECTION_NAME]

    @pytest.fixture
    def fuel_history_collection(
        self, test_database: AsyncIOMotorDatabase[Any]
    ) -> Any:
        """Get the fuel_history collection from test database."""
        return test_database[MongoSparkRepository.FUEL_HISTORY_COLLECTION]

    @pytest.fixture
    def bonfire_collection(
        self, test_database: AsyncIOMotorDatabase[Any]
    ) -> Any:
        """Get the bonfires collection from test database."""
        return test_database[MongoBonfireRepository.COLLECTION_NAME]

    async def _create_spark(
        self,
        spark_collection: Any,
        spark_id: str,
        user_hash: str = "author-hash",
        level: SparkLevel = SparkLevel.SPARK,
        fuel_count: int = 0,
        decay_seconds: int = 1800,
        field_id: str = "sakurazaka46",
    ) -> Spark:
        """Helper to create a spark in the database."""
        spark = Spark.create(
            spark_id=spark_id,
            content="Test content for promotion",
            user_hash=user_hash,
            decay_after_seconds=decay_seconds,
            vanish_after_days=30,
            field_id=field_id,
        )
        await spark_collection.insert_one(
            {
                "id": spark.id,
                "content": spark.content,
                "user_hash": spark.user_hash,
                "fuel_count": fuel_count,
                "level": level.value,
                "field_id": spark.field_id,
                "created_at": spark.created_at,
                "decay_at": spark.decay_at,
                "vanish_at": spark.vanish_at,
            }
        )
        return spark

    async def _add_fuel_from_user(
        self,
        test_client: AsyncClient,
        spark_id: str,
        ip_address: str,
    ) -> Any:
        """Helper to add fuel from a specific user (IP)."""
        return await test_client.post(
            f"/api/sparks/{spark_id}/fuel",
            headers={"X-Forwarded-For": ip_address},
        )

    # ==========================================================================
    # Promotion to Kindling Tests
    # ==========================================================================

    @pytest.mark.asyncio
    async def test_addFuel_when3UniqueUsers_promotesToKindling(
        self,
        test_client: AsyncClient,
        spark_collection: Any,
        fuel_history_collection: Any,
    ) -> None:
        """
        Action: addFuel (POST /api/sparks/{id}/fuel)
        Condition: when3UniqueUsers (3 different users fuel the spark)
        Result: promotesToKindling (level changes to KINDLING)

        Spec: Kindling threshold is fixed at 3 UU
        """
        # Arrange: Create a spark
        spark = await self._create_spark(spark_collection, "spark-kindling-1")

        # Act: Add fuel from 3 different users
        await self._add_fuel_from_user(test_client, spark.id, "10.0.0.1")
        await self._add_fuel_from_user(test_client, spark.id, "10.0.0.2")
        response = await self._add_fuel_from_user(test_client, spark.id, "10.0.0.3")

        # Assert: Response indicates promotion
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["promoted"] is True
        assert data["previous_level"] == SparkLevel.SPARK.value
        assert data["current_level"] == SparkLevel.KINDLING.value
        assert data["bonfire_created"] is False

        # Assert: Database level updated
        doc = await spark_collection.find_one({"id": spark.id})
        assert doc["level"] == SparkLevel.KINDLING.value

    @pytest.mark.asyncio
    async def test_addFuel_when2UniqueUsers_remainsSpark(
        self,
        test_client: AsyncClient,
        spark_collection: Any,
        fuel_history_collection: Any,
    ) -> None:
        """
        Action: addFuel
        Condition: when2UniqueUsers (only 2 users fueled)
        Result: remainsSpark (level stays SPARK, no promotion)
        """
        # Arrange: Create a spark
        spark = await self._create_spark(spark_collection, "spark-no-promote-1")

        # Act: Add fuel from only 2 users
        await self._add_fuel_from_user(test_client, spark.id, "10.0.1.1")
        response = await self._add_fuel_from_user(test_client, spark.id, "10.0.1.2")

        # Assert: No promotion
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["promoted"] is False

        # Assert: Database level unchanged
        doc = await spark_collection.find_one({"id": spark.id})
        assert doc["level"] == SparkLevel.SPARK.value

    # ==========================================================================
    # Promotion to Bonfire Tests
    # ==========================================================================

    @pytest.mark.asyncio
    async def test_addFuel_whenThresholdMetAndHeatScoreHigh_promotesToBonfire(
        self,
        test_client: AsyncClient,
        spark_collection: Any,
        fuel_history_collection: Any,
        bonfire_collection: Any,
        test_redis: Redis,  # type: ignore[type-arg]
    ) -> None:
        """
        Action: addFuel
        Condition: whenThresholdMetAndHeatScoreHigh (UU >= threshold, heat >= 50)
        Result: promotesToBonfire (level changes to BONFIRE, bonfire created)

        Note: Default threshold is 10 UU, heat_score threshold is 50
              With fuel_weight=1, need 50 fuels or more UUs
        """
        # Arrange: Set a lower threshold for testing (3 UU)
        await test_redis.set("config:threshold:bonfire_uu", "3")
        await test_redis.set("config:threshold:heat_score", "3")

        # Create a spark
        spark = await self._create_spark(spark_collection, "spark-bonfire-1")

        # Act: Add fuel from 3 different users (meets UU threshold)
        # With fuel_weight=1, 3 fuels = heat_score 3
        await self._add_fuel_from_user(test_client, spark.id, "10.1.0.1")
        await self._add_fuel_from_user(test_client, spark.id, "10.1.0.2")
        response = await self._add_fuel_from_user(test_client, spark.id, "10.1.0.3")

        # Assert: Response indicates bonfire promotion
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["promoted"] is True
        assert data["current_level"] == SparkLevel.BONFIRE.value
        assert data["bonfire_created"] is True

        # Assert: Spark level updated
        spark_doc = await spark_collection.find_one({"id": spark.id})
        assert spark_doc["level"] == SparkLevel.BONFIRE.value

        # Assert: Bonfire created in database
        bonfire_doc = await bonfire_collection.find_one({"spark_id": spark.id})
        assert bonfire_doc is not None
        assert bonfire_doc["content"] == "Test content for promotion"
        assert bonfire_doc["field_id"] == "sakurazaka46"

    @pytest.mark.asyncio
    async def test_addFuel_whenAntiTroll_twoUsersCantPromoteToBonfire(
        self,
        test_client: AsyncClient,
        spark_collection: Any,
        fuel_history_collection: Any,
        bonfire_collection: Any,
        test_redis: Redis,  # type: ignore[type-arg]
    ) -> None:
        """
        Action: addFuel
        Condition: whenAntiTroll (only 2 users, even with high fuel count)
        Result: twoUsersCantPromoteToBonfire (stays at KINDLING, no bonfire)

        Spec: Anti-troll logic - 1vs1 cannot promote to bonfire
              Even with heat_score requirement met, UU < threshold prevents promotion.
        """
        # Arrange: Set threshold to 5 UU (2 users can never meet this)
        # With only 2 users, even adding fuel won't reach 5 UU
        await test_redis.set("config:threshold:bonfire_uu", "5")
        await test_redis.set("config:threshold:heat_score", "10")

        # Create a spark already at KINDLING level with high fuel
        spark = await self._create_spark(
            spark_collection,
            "spark-antitroll-1",
            level=SparkLevel.KINDLING,
            fuel_count=100,  # High fuel count = high heat_score
        )

        # Pre-populate fuel history for 2 users (simulating 2 people already fueled)
        await fuel_history_collection.insert_many([
            {"spark_id": spark.id, "user_hash": "hash-user-1", "created_at": datetime.now(UTC)},
            {"spark_id": spark.id, "user_hash": "hash-user-2", "created_at": datetime.now(UTC)},
        ])

        # Act: Add fuel from a 3rd user - still won't reach 5 UU threshold
        response = await self._add_fuel_from_user(test_client, spark.id, "10.2.0.1")

        # Assert: No promotion to bonfire (3 UU < 5 UU threshold)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # Promotion may occur (to kindling at most), but bonfire not created
        assert data["bonfire_created"] is False

        # Assert: No bonfire in database
        bonfire_doc = await bonfire_collection.find_one({"spark_id": spark.id})
        assert bonfire_doc is None

    # ==========================================================================
    # Bonfire TTL Extension Tests
    # ==========================================================================

    @pytest.mark.asyncio
    async def test_addFuel_whenBonfireExists_extendsTTL(
        self,
        test_client: AsyncClient,
        spark_collection: Any,
        fuel_history_collection: Any,
        bonfire_collection: Any,
        test_redis: Redis,  # type: ignore[type-arg]
    ) -> None:
        """
        Action: addFuel (to a spark that's already a bonfire)
        Condition: whenBonfireExists (spark is level BONFIRE)
        Result: extendsTTL (bonfire decay_at extended by fuel extension minutes)

        Spec: Fuel extends bonfire by 10 minutes (default)
        """
        # Arrange: Set extension time
        await test_redis.set("config:decay:bonfire_fuel_minutes", "10")

        # Create a spark at BONFIRE level
        spark = await self._create_spark(
            spark_collection,
            "spark-extend-1",
            level=SparkLevel.BONFIRE,
        )

        # Create corresponding bonfire
        original_decay = datetime.now(UTC) + timedelta(hours=1)
        await bonfire_collection.insert_one({
            "id": "bonfire-extend-1",
            "spark_id": spark.id,
            "content": spark.content,
            "unique_user_count": 10,
            "heat_score": 100,
            "field_id": "sakurazaka46",
            "created_at": datetime.now(UTC),
            "decay_at": original_decay,
        })

        # Act: Add fuel to bonfire
        response = await self._add_fuel_from_user(test_client, spark.id, "10.3.0.1")

        # Assert: Success response
        assert response.status_code == status.HTTP_200_OK

        # Assert: Bonfire TTL extended
        bonfire_doc = await bonfire_collection.find_one({"spark_id": spark.id})
        assert bonfire_doc is not None
        # decay_at should be extended by 10 minutes from original
        new_decay = bonfire_doc["decay_at"].replace(tzinfo=UTC)
        expected_decay = original_decay + timedelta(minutes=10)
        # Allow 1 second tolerance for test execution time
        assert abs((new_decay - expected_decay).total_seconds()) < 1

    # ==========================================================================
    # Get Active Bonfires Tests
    # ==========================================================================

    @pytest.mark.asyncio
    async def test_getBonfires_whenActiveBonfiresExist_returnsList(
        self,
        test_client: AsyncClient,
        bonfire_collection: Any,
    ) -> None:
        """
        Action: getBonfires (GET /api/bonfires)
        Condition: whenActiveBonfiresExist (multiple active bonfires)
        Result: returnsList (list of active bonfires)
        """
        # Arrange: Create active bonfires
        now = datetime.now(UTC)
        await bonfire_collection.insert_many([
            {
                "id": "bonfire-active-1",
                "spark_id": "spark-1",
                "content": "Bonfire 1",
                "unique_user_count": 10,
                "heat_score": 50,
                "field_id": "sakurazaka46",
                "created_at": now - timedelta(hours=1),
                "decay_at": now + timedelta(hours=2),  # Active
            },
            {
                "id": "bonfire-active-2",
                "spark_id": "spark-2",
                "content": "Bonfire 2",
                "unique_user_count": 15,
                "heat_score": 75,
                "field_id": "sakurazaka46",
                "created_at": now - timedelta(minutes=30),
                "decay_at": now + timedelta(hours=3),  # Active
            },
        ])

        # Act
        response = await test_client.get(
            "/api/bonfires", params={"field_id": "sakurazaka46"}
        )

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["count"] == 2
        assert len(data["bonfires"]) == 2

        # Verify bonfire data
        bonfire_ids = [b["id"] for b in data["bonfires"]]
        assert "bonfire-active-1" in bonfire_ids
        assert "bonfire-active-2" in bonfire_ids

    @pytest.mark.asyncio
    async def test_getBonfires_whenDecayedBonfiresExist_excludesDecayed(
        self,
        test_client: AsyncClient,
        bonfire_collection: Any,
    ) -> None:
        """
        Action: getBonfires
        Condition: whenDecayedBonfiresExist (some bonfires past decay_at)
        Result: excludesDecayed (only active bonfires returned)
        """
        # Arrange: Create mixed bonfires (active and decayed)
        now = datetime.now(UTC)
        await bonfire_collection.insert_many([
            {
                "id": "bonfire-still-active",
                "spark_id": "spark-active",
                "content": "Active bonfire",
                "unique_user_count": 10,
                "heat_score": 50,
                "field_id": "sakurazaka46",
                "created_at": now - timedelta(hours=1),
                "decay_at": now + timedelta(hours=1),  # Still active
            },
            {
                "id": "bonfire-already-decayed",
                "spark_id": "spark-decayed",
                "content": "Decayed bonfire",
                "unique_user_count": 5,
                "heat_score": 30,
                "field_id": "sakurazaka46",
                "created_at": now - timedelta(hours=5),
                "decay_at": now - timedelta(hours=1),  # Already decayed
            },
        ])

        # Act
        response = await test_client.get(
            "/api/bonfires", params={"field_id": "sakurazaka46"}
        )

        # Assert: Only active bonfire returned
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["count"] == 1
        assert data["bonfires"][0]["id"] == "bonfire-still-active"

    @pytest.mark.asyncio
    async def test_getBonfires_whenNoBonfires_returnsEmptyList(
        self,
        test_client: AsyncClient,
        bonfire_collection: Any,
    ) -> None:
        """
        Action: getBonfires
        Condition: whenNoBonfires (no bonfires in database)
        Result: returnsEmptyList (empty array)
        """
        # Arrange: No bonfires (clean state from fixture)

        # Act
        response = await test_client.get(
            "/api/bonfires", params={"field_id": "sakurazaka46"}
        )

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["count"] == 0
        assert data["bonfires"] == []

"""Unit tests for Spark entity."""

from datetime import UTC, datetime, timedelta

from app.domain.model.spark import Spark


class TestSpark:
    """Test suite for Spark entity."""

    def test_create_whenValidInput_returnsSparkWithCorrectFields(self) -> None:
        """Test creating a spark with valid input returns correct fields."""
        # Arrange
        spark_id = "test-id"
        content = "Test spark content"
        user_hash = "test-hash"
        visible_duration_minutes = 10
        ttl_days = 30

        # Act
        spark = Spark.create(
            spark_id=spark_id,
            content=content,
            user_hash=user_hash,
            visible_duration_minutes=visible_duration_minutes,
            ttl_days=ttl_days,
        )

        # Assert
        assert spark.id == spark_id
        assert spark.content == content
        assert spark.user_hash == user_hash
        assert isinstance(spark.created_at, datetime)
        assert isinstance(spark.visible_until, datetime)
        assert isinstance(spark.expire_at, datetime)

    def test_create_whenValidInput_calculatesVisibleUntilCorrectly(self) -> None:
        """Test that visible_until is calculated correctly."""
        # Arrange
        visible_duration_minutes = 10
        ttl_days = 30
        before = datetime.now(UTC)

        # Act
        spark = Spark.create(
            spark_id="test-id",
            content="test",
            user_hash="hash",
            visible_duration_minutes=visible_duration_minutes,
            ttl_days=ttl_days,
        )
        after = datetime.now(UTC)

        # Assert
        expected_min = before + timedelta(minutes=visible_duration_minutes)
        expected_max = after + timedelta(minutes=visible_duration_minutes)
        assert expected_min <= spark.visible_until <= expected_max

    def test_create_whenValidInput_calculatesExpireAtCorrectly(self) -> None:
        """Test that expire_at is calculated correctly."""
        # Arrange
        visible_duration_minutes = 10
        ttl_days = 30
        before = datetime.now(UTC)

        # Act
        spark = Spark.create(
            spark_id="test-id",
            content="test",
            user_hash="hash",
            visible_duration_minutes=visible_duration_minutes,
            ttl_days=ttl_days,
        )
        after = datetime.now(UTC)

        # Assert
        expected_min = before + timedelta(days=ttl_days)
        expected_max = after + timedelta(days=ttl_days)
        assert expected_min <= spark.expire_at <= expected_max

    def test_create_whenDifferentDurations_calculatesTimestampsIndependently(
        self,
    ) -> None:
        """Test that different durations create different timestamps."""
        # Act
        spark1 = Spark.create(
            spark_id="id1",
            content="test",
            user_hash="hash",
            visible_duration_minutes=10,
            ttl_days=30,
        )
        spark2 = Spark.create(
            spark_id="id2",
            content="test",
            user_hash="hash",
            visible_duration_minutes=20,
            ttl_days=60,
        )

        # Assert
        assert spark1.visible_until < spark2.visible_until
        assert spark1.expire_at < spark2.expire_at

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
        decay_after_seconds = 600
        vanish_after_days = 30

        # Act
        spark = Spark.create(
            spark_id=spark_id,
            content=content,
            user_hash=user_hash,
            decay_after_seconds=decay_after_seconds,
            vanish_after_days=vanish_after_days,
        )

        # Assert
        assert spark.id == spark_id
        assert spark.content == content
        assert spark.user_hash == user_hash
        assert isinstance(spark.created_at, datetime)
        assert isinstance(spark.decay_at, datetime)
        assert isinstance(spark.vanish_at, datetime)

    def test_create_whenValidInput_calculatesDecayAtCorrectly(self) -> None:
        """Test that decay_at is calculated correctly."""
        # Arrange
        decay_after_seconds = 600
        vanish_after_days = 30
        before = datetime.now(UTC)

        # Act
        spark = Spark.create(
            spark_id="test-id",
            content="test",
            user_hash="hash",
            decay_after_seconds=decay_after_seconds,
            vanish_after_days=vanish_after_days,
        )
        after = datetime.now(UTC)

        # Assert
        expected_min = before + timedelta(seconds=decay_after_seconds)
        expected_max = after + timedelta(seconds=decay_after_seconds)
        assert expected_min <= spark.decay_at <= expected_max

    def test_create_whenValidInput_calculatesVanishAtCorrectly(self) -> None:
        """Test that vanish_at is calculated correctly."""
        # Arrange
        decay_after_seconds = 600
        vanish_after_days = 30
        before = datetime.now(UTC)

        # Act
        spark = Spark.create(
            spark_id="test-id",
            content="test",
            user_hash="hash",
            decay_after_seconds=decay_after_seconds,
            vanish_after_days=vanish_after_days,
        )
        after = datetime.now(UTC)

        # Assert
        expected_min = before + timedelta(days=vanish_after_days)
        expected_max = after + timedelta(days=vanish_after_days)
        assert expected_min <= spark.vanish_at <= expected_max

    def test_create_whenDifferentDurations_calculatesTimestampsIndependently(
        self,
    ) -> None:
        """Test that different durations create different timestamps."""
        # Act
        spark1 = Spark.create(
            spark_id="id1",
            content="test",
            user_hash="hash",
            decay_after_seconds=600,
            vanish_after_days=30,
        )
        spark2 = Spark.create(
            spark_id="id2",
            content="test",
            user_hash="hash",
            decay_after_seconds=1200,
            vanish_after_days=60,
        )

        # Assert
        assert spark1.decay_at < spark2.decay_at
        assert spark1.vanish_at < spark2.vanish_at

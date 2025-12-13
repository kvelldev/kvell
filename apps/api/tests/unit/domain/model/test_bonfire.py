"""Unit tests for Bonfire entity."""

from datetime import UTC, datetime

from freezegun import freeze_time

from app.domain.model.bonfire import Bonfire


class TestBonfire:
    """Tests for Bonfire entity."""

    # Creation tests

    @freeze_time("2024-01-01 12:00:00")
    def test_create_withDefaultDecayHours_setsCorrectTimestamps(self) -> None:
        """Create bonfire with default 3 hour TTL."""
        bonfire = Bonfire.create(
            spark_id="spark-1",
            content="Test content",
            unique_user_count=10,
            heat_score=50,
        )

        assert bonfire.id == "spark-1"
        assert bonfire.spark_id == "spark-1"
        assert bonfire.content == "Test content"
        assert bonfire.unique_user_count == 10
        assert bonfire.heat_score == 50
        assert bonfire.created_at == datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC)
        assert bonfire.decay_at == datetime(2024, 1, 1, 15, 0, 0, tzinfo=UTC)

    @freeze_time("2024-01-01 12:00:00")
    def test_create_withCustomDecayHours_setsCorrectTimestamps(self) -> None:
        """Create bonfire with custom TTL."""
        bonfire = Bonfire.create(
            spark_id="spark-1",
            content="Test content",
            unique_user_count=10,
            heat_score=50,
            initial_decay_hours=6,
        )

        assert bonfire.decay_at == datetime(2024, 1, 1, 18, 0, 0, tzinfo=UTC)

    # Fuel extension tests

    @freeze_time("2024-01-01 12:00:00")
    def test_extendByFuel_addsMinutesToDecayAt(self) -> None:
        """Extend by fuel adds minutes to current decay_at."""
        bonfire = Bonfire.create(
            spark_id="spark-1",
            content="Test",
            unique_user_count=10,
            heat_score=50,
            initial_decay_hours=1,
        )
        # decay_at = 13:00

        extended = bonfire.extend_by_fuel(extension_minutes=10)

        # Should add 10 minutes to decay_at (not from now)
        assert extended.decay_at == datetime(2024, 1, 1, 13, 10, 0, tzinfo=UTC)

    @freeze_time("2024-01-01 12:00:00")
    def test_extendByFuel_preservesOtherFields(self) -> None:
        """Extend by fuel preserves all other fields."""
        bonfire = Bonfire.create(
            spark_id="spark-1",
            content="Test",
            unique_user_count=10,
            heat_score=50,
        )

        extended = bonfire.extend_by_fuel(extension_minutes=10)

        assert extended.id == bonfire.id
        assert extended.spark_id == bonfire.spark_id
        assert extended.content == bonfire.content
        assert extended.unique_user_count == bonfire.unique_user_count
        assert extended.heat_score == bonfire.heat_score
        assert extended.created_at == bonfire.created_at

    # Reply extension tests

    @freeze_time("2024-01-01 12:00:00")
    def test_extendByReply_whenRemainingTTLShort_extendsFromNow(self) -> None:
        """Extend by reply when remaining TTL is shorter than extension."""
        bonfire = Bonfire(
            id="spark-1",
            spark_id="spark-1",
            content="Test",
            unique_user_count=10,
            heat_score=50,
            created_at=datetime(2024, 1, 1, 10, 0, 0, tzinfo=UTC),
            decay_at=datetime(2024, 1, 1, 12, 30, 0, tzinfo=UTC),  # 30 min remaining
        )

        extended = bonfire.extend_by_reply(extension_hours=3)

        # Should extend to now + 3 hours = 15:00
        assert extended.decay_at == datetime(2024, 1, 1, 15, 0, 0, tzinfo=UTC)

    @freeze_time("2024-01-01 12:00:00")
    def test_extendByReply_whenRemainingTTLLong_doesNotExtend(self) -> None:
        """Do not extend when remaining TTL is longer than extension."""
        bonfire = Bonfire(
            id="spark-1",
            spark_id="spark-1",
            content="Test",
            unique_user_count=10,
            heat_score=50,
            created_at=datetime(2024, 1, 1, 10, 0, 0, tzinfo=UTC),
            decay_at=datetime(2024, 1, 1, 20, 0, 0, tzinfo=UTC),  # 8 hours remaining
        )

        extended = bonfire.extend_by_reply(extension_hours=3)

        # Should NOT extend (8h > 3h)
        assert extended.decay_at == datetime(2024, 1, 1, 20, 0, 0, tzinfo=UTC)

    @freeze_time("2024-01-01 12:00:00")
    def test_extendByReply_withCustomCurrentTime_usesProvidedTime(self) -> None:
        """Extension uses provided current_time for calculation."""
        bonfire = Bonfire(
            id="spark-1",
            spark_id="spark-1",
            content="Test",
            unique_user_count=10,
            heat_score=50,
            created_at=datetime(2024, 1, 1, 10, 0, 0, tzinfo=UTC),
            decay_at=datetime(2024, 1, 1, 12, 30, 0, tzinfo=UTC),
        )

        custom_time = datetime(2024, 1, 1, 14, 0, 0, tzinfo=UTC)
        extended = bonfire.extend_by_reply(
            extension_hours=3,
            current_time=custom_time,
        )

        # Should extend to custom_time + 3 hours = 17:00
        assert extended.decay_at == datetime(2024, 1, 1, 17, 0, 0, tzinfo=UTC)

    # is_active tests

    @freeze_time("2024-01-01 12:00:00")
    def test_isActive_beforeDecayAt_returnsTrue(self) -> None:
        """Bonfire is active before decay_at."""
        bonfire = Bonfire(
            id="spark-1",
            spark_id="spark-1",
            content="Test",
            unique_user_count=10,
            heat_score=50,
            created_at=datetime(2024, 1, 1, 10, 0, 0, tzinfo=UTC),
            decay_at=datetime(2024, 1, 1, 15, 0, 0, tzinfo=UTC),
        )

        assert bonfire.is_active is True

    @freeze_time("2024-01-01 15:00:00")
    def test_isActive_atDecayAt_returnsFalse(self) -> None:
        """Bonfire is not active at exact decay_at time."""
        bonfire = Bonfire(
            id="spark-1",
            spark_id="spark-1",
            content="Test",
            unique_user_count=10,
            heat_score=50,
            created_at=datetime(2024, 1, 1, 10, 0, 0, tzinfo=UTC),
            decay_at=datetime(2024, 1, 1, 15, 0, 0, tzinfo=UTC),
        )

        assert bonfire.is_active is False

    @freeze_time("2024-01-01 16:00:00")
    def test_isActive_afterDecayAt_returnsFalse(self) -> None:
        """Bonfire is not active after decay_at."""
        bonfire = Bonfire(
            id="spark-1",
            spark_id="spark-1",
            content="Test",
            unique_user_count=10,
            heat_score=50,
            created_at=datetime(2024, 1, 1, 10, 0, 0, tzinfo=UTC),
            decay_at=datetime(2024, 1, 1, 15, 0, 0, tzinfo=UTC),
        )

        assert bonfire.is_active is False

    # Immutability test

    def test_bonfire_isFrozen(self) -> None:
        """Bonfire model is immutable."""
        bonfire = Bonfire.create(
            spark_id="spark-1",
            content="Test",
            unique_user_count=10,
            heat_score=50,
        )

        # Direct attribute modification should fail silently or raise
        # For frozen Pydantic models, the object is simply not modified
        original_content = bonfire.content
        try:
            bonfire.content = "Modified"  # type: ignore[misc]
        except Exception:
            pass  # Expected for frozen model
        assert bonfire.content == original_content

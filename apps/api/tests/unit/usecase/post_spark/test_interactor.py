"""Unit tests for PostSparkInteractor."""

from unittest.mock import AsyncMock, Mock

import pytest

from app.domain.exception import AppError
from app.domain.model.bonfire import Bonfire
from app.domain.model.spark import Spark
from app.usecase.dto.spark_dto import PostSparkInput, SparkOutput
from app.usecase.post_spark.interactor import PostSparkInteractor

pytestmark = pytest.mark.asyncio


class TestPostSparkInteractor:
    """Test suite for PostSparkInteractor."""

    @pytest.fixture
    def mock_spark_repository(self) -> AsyncMock:
        """Create mock spark repository."""
        return AsyncMock()

    @pytest.fixture
    def mock_identity_provider(self) -> Mock:
        """Create mock identity provider."""
        mock = Mock()
        mock.get_user_hash.return_value = "test-user-hash"
        return mock

    @pytest.fixture
    def mock_rate_limiter(self) -> AsyncMock:
        """Create mock rate limiter."""
        mock = AsyncMock()
        mock.check_and_increment.return_value = True  # Default: within limit
        return mock

    @pytest.fixture
    def mock_logger(self) -> Mock:
        """Create mock logger."""
        return Mock()

    @pytest.fixture
    def mock_pubsub_gateway(self) -> AsyncMock:
        """Create mock pub/sub gateway."""
        return AsyncMock()

    @pytest.fixture
    def mock_bonfire_repository(self) -> AsyncMock:
        """Create mock bonfire repository."""
        return AsyncMock()

    @pytest.fixture
    def interactor(
        self,
        mock_spark_repository: AsyncMock,
        mock_identity_provider: Mock,
        mock_rate_limiter: AsyncMock,
        mock_logger: Mock,
        mock_pubsub_gateway: AsyncMock,
        mock_bonfire_repository: AsyncMock,
    ) -> PostSparkInteractor:
        """Create PostSparkInteractor instance."""
        return PostSparkInteractor(
            spark_repository=mock_spark_repository,
            identity_provider=mock_identity_provider,
            rate_limiter=mock_rate_limiter,
            logger=mock_logger,
            pubsub_gateway=mock_pubsub_gateway,
            bonfire_repository=mock_bonfire_repository,
            max_length=500,
            rate_limit_count=10,
            rate_limit_window_seconds=60,
            decay_after_seconds=600,
            vanish_after_days=30,
            ng_words=["forbidden_word", "bad_word"],
            pubsub_channel="sparks:events",
        )

    async def test_execute_whenValidInput_returnsSparkOutput(
        self,
        interactor: PostSparkInteractor,
        mock_spark_repository: AsyncMock,
    ) -> None:
        """Test execute with valid input returns SparkOutput."""
        # Arrange
        input_data = PostSparkInput(content="Valid spark content")
        ip_address = "192.168.1.1"

        mock_spark = Spark.create(
            spark_id="test-id",
            content=input_data.content,
            user_hash="test-user-hash",
            decay_after_seconds=600,
            vanish_after_days=30,
        )
        mock_spark_repository.save.return_value = mock_spark

        # Act
        result = await interactor.execute(input_data, ip_address)

        # Assert
        assert isinstance(result, SparkOutput)
        assert result.id == "test-id"
        assert result.content == input_data.content
        assert mock_spark_repository.save.called

    async def test_execute_whenContentTooLong_raisesAppError(
        self,
        interactor: PostSparkInteractor,
    ) -> None:
        """Test execute with too long content raises AppError with code 1003."""
        # Arrange
        long_content = "x" * 501  # Over 500 char limit
        input_data = PostSparkInput(content=long_content)
        ip_address = "192.168.1.1"

        # Act & Assert
        with pytest.raises(AppError) as exc_info:
            await interactor.execute(input_data, ip_address)

        assert exc_info.value.internal_code == 1003

    async def test_execute_whenNGWordDetected_raisesAppError(
        self,
        interactor: PostSparkInteractor,
    ) -> None:
        """Test execute with NG word raises AppError with code 1002."""
        # Arrange
        input_data = PostSparkInput(content="This contains forbidden_word here")
        ip_address = "192.168.1.1"

        # Act & Assert
        with pytest.raises(AppError) as exc_info:
            await interactor.execute(input_data, ip_address)

        assert exc_info.value.internal_code == 1002

    async def test_execute_whenNGWordCaseInsensitive_raisesAppError(
        self,
        interactor: PostSparkInteractor,
    ) -> None:
        """Test execute with NG word (case insensitive) raises AppError."""
        # Arrange
        input_data = PostSparkInput(content="This contains FORBIDDEN_WORD here")
        ip_address = "192.168.1.1"

        # Act & Assert
        with pytest.raises(AppError) as exc_info:
            await interactor.execute(input_data, ip_address)

        assert exc_info.value.internal_code == 1002

    async def test_execute_whenRateLimitExceeded_raisesAppError(
        self,
        interactor: PostSparkInteractor,
        mock_rate_limiter: AsyncMock,
    ) -> None:
        """Test execute when rate limit exceeded raises AppError with code 1004."""
        # Arrange
        input_data = PostSparkInput(content="Valid content")
        ip_address = "192.168.1.1"
        mock_rate_limiter.check_and_increment.return_value = False  # Exceeded

        # Act & Assert
        with pytest.raises(AppError) as exc_info:
            await interactor.execute(input_data, ip_address)

        assert exc_info.value.internal_code == 1004

    async def test_execute_whenValid_callsIdentityProviderWithIPAddress(
        self,
        interactor: PostSparkInteractor,
        mock_identity_provider: Mock,
        mock_spark_repository: AsyncMock,
    ) -> None:
        """Test execute calls identity provider with IP address."""
        # Arrange
        input_data = PostSparkInput(content="Valid content")
        ip_address = "192.168.1.1"
        mock_spark = Spark.create(
            spark_id="test-id",
            content=input_data.content,
            user_hash="test-user-hash",
            decay_after_seconds=600,
            vanish_after_days=30,
        )
        mock_spark_repository.save.return_value = mock_spark

        # Act
        await interactor.execute(input_data, ip_address)

        # Assert
        mock_identity_provider.get_user_hash.assert_called_once_with(ip_address)

    async def test_execute_whenValid_callsRateLimiterWithCorrectParams(
        self,
        interactor: PostSparkInteractor,
        mock_rate_limiter: AsyncMock,
        mock_spark_repository: AsyncMock,
    ) -> None:
        """Test execute calls rate limiter with correct parameters."""
        # Arrange
        input_data = PostSparkInput(content="Valid content")
        ip_address = "192.168.1.1"
        mock_spark = Spark.create(
            spark_id="test-id",
            content=input_data.content,
            user_hash="test-user-hash",
            decay_after_seconds=600,
            vanish_after_days=30,
        )
        mock_spark_repository.save.return_value = mock_spark

        # Act
        await interactor.execute(input_data, ip_address)

        # Assert
        mock_rate_limiter.check_and_increment.assert_called_once_with(
            user_hash="test-user-hash",
            limit=10,
            window_seconds=60,
        )

    async def test_execute_whenValid_savesSparkWithCorrectFields(
        self,
        interactor: PostSparkInteractor,
        mock_spark_repository: AsyncMock,
    ) -> None:
        """Test execute saves spark with correct fields."""
        # Arrange
        input_data = PostSparkInput(content="Valid content")
        ip_address = "192.168.1.1"
        mock_spark = Spark.create(
            spark_id="test-id",
            content=input_data.content,
            user_hash="test-user-hash",
            decay_after_seconds=600,
            vanish_after_days=30,
        )
        mock_spark_repository.save.return_value = mock_spark

        # Act
        await interactor.execute(input_data, ip_address)

        # Assert
        assert mock_spark_repository.save.called
        saved_spark = mock_spark_repository.save.call_args[0][0]
        assert saved_spark.content == input_data.content
        assert saved_spark.user_hash == "test-user-hash"

    async def test_execute_whenValid_publishesToPubSubChannel(
        self,
        interactor: PostSparkInteractor,
        mock_spark_repository: AsyncMock,
        mock_pubsub_gateway: AsyncMock,
    ) -> None:
        """Test execute publishes to pub/sub channel after saving."""
        # Arrange
        input_data = PostSparkInput(content="Valid content")
        ip_address = "192.168.1.1"
        mock_spark = Spark.create(
            spark_id="test-id",
            content=input_data.content,
            user_hash="test-user-hash",
            decay_after_seconds=600,
            vanish_after_days=30,
        )
        mock_spark_repository.save.return_value = mock_spark

        # Act
        await interactor.execute(input_data, ip_address)

        # Assert
        mock_pubsub_gateway.publish.assert_called_once()
        call_args = mock_pubsub_gateway.publish.call_args
        assert call_args[0][0] == "sparks:events"  # channel
        published_message = call_args[0][1]  # message
        assert isinstance(published_message, SparkOutput)
        assert published_message.id == "test-id"
        assert published_message.content == input_data.content

    async def test_execute_whenValid_publishesAfterSaving(
        self,
        interactor: PostSparkInteractor,
        mock_spark_repository: AsyncMock,
        mock_pubsub_gateway: AsyncMock,
    ) -> None:
        """Test execute publishes only after successful save."""
        # Arrange
        input_data = PostSparkInput(content="Valid content")
        ip_address = "192.168.1.1"
        mock_spark = Spark.create(
            spark_id="test-id",
            content=input_data.content,
            user_hash="test-user-hash",
            decay_after_seconds=600,
            vanish_after_days=30,
        )
        mock_spark_repository.save.return_value = mock_spark

        # Track call order
        call_order: list[str] = []

        def save_side_effect(_: Spark) -> Spark:
            call_order.append("save")
            return mock_spark

        def publish_side_effect(_channel: str, _message: SparkOutput) -> None:
            call_order.append("publish")

        mock_spark_repository.save.side_effect = save_side_effect
        mock_pubsub_gateway.publish.side_effect = publish_side_effect

        # Act
        await interactor.execute(input_data, ip_address)

        # Assert
        assert call_order == ["save", "publish"]


class TestPostSparkInteractorReply:
    """Test suite for PostSparkInteractor reply functionality."""

    @pytest.fixture
    def mock_spark_repository(self) -> AsyncMock:
        """Create mock spark repository."""
        return AsyncMock()

    @pytest.fixture
    def mock_identity_provider(self) -> Mock:
        """Create mock identity provider."""
        mock = Mock()
        mock.get_user_hash.return_value = "test-user-hash"
        return mock

    @pytest.fixture
    def mock_rate_limiter(self) -> AsyncMock:
        """Create mock rate limiter."""
        mock = AsyncMock()
        mock.check_and_increment.return_value = True
        return mock

    @pytest.fixture
    def mock_logger(self) -> Mock:
        """Create mock logger."""
        return Mock()

    @pytest.fixture
    def mock_pubsub_gateway(self) -> AsyncMock:
        """Create mock pub/sub gateway."""
        return AsyncMock()

    @pytest.fixture
    def mock_bonfire_repository(self) -> AsyncMock:
        """Create mock bonfire repository."""
        return AsyncMock()

    @pytest.fixture
    def interactor(
        self,
        mock_spark_repository: AsyncMock,
        mock_identity_provider: Mock,
        mock_rate_limiter: AsyncMock,
        mock_logger: Mock,
        mock_pubsub_gateway: AsyncMock,
        mock_bonfire_repository: AsyncMock,
    ) -> PostSparkInteractor:
        """Create PostSparkInteractor instance."""
        return PostSparkInteractor(
            spark_repository=mock_spark_repository,
            identity_provider=mock_identity_provider,
            rate_limiter=mock_rate_limiter,
            logger=mock_logger,
            pubsub_gateway=mock_pubsub_gateway,
            bonfire_repository=mock_bonfire_repository,
            max_length=500,
            rate_limit_count=10,
            rate_limit_window_seconds=60,
            decay_after_seconds=600,
            vanish_after_days=30,
            ng_words=["forbidden_word"],
            pubsub_channel="sparks:events",
        )

    @pytest.fixture
    def mock_bonfire(self) -> Bonfire:
        """Create mock bonfire for testing."""
        return Bonfire.create(
            spark_id="bonfire-001",
            content="Parent bonfire content",
            unique_user_count=10,
            heat_score=100,
            initial_decay_hours=3,
        )

    async def test_execute_whenReplyToBonfire_checksBonfireExists(
        self,
        interactor: PostSparkInteractor,
        mock_bonfire_repository: AsyncMock,
        mock_bonfire: Bonfire,
    ) -> None:
        """Test reply checks if parent bonfire exists."""
        # Arrange
        input_data = PostSparkInput(
            content="Reply content",
            parent_bonfire_id="bonfire-001",
        )
        ip_address = "192.168.1.1"
        mock_bonfire_repository.find_by_id.return_value = mock_bonfire

        # Act
        with pytest.raises(Exception):
            # Will fail because spark_repository.save is not mocked
            await interactor.execute(input_data, ip_address)

        # Assert
        mock_bonfire_repository.find_by_id.assert_called_once_with("bonfire-001")

    async def test_execute_whenReplyToBonfireNotFound_raisesAppError(
        self,
        interactor: PostSparkInteractor,
        mock_bonfire_repository: AsyncMock,
    ) -> None:
        """Test reply to non-existent bonfire raises AppError with code 1005."""
        # Arrange
        input_data = PostSparkInput(
            content="Reply content",
            parent_bonfire_id="nonexistent-bonfire",
        )
        ip_address = "192.168.1.1"
        mock_bonfire_repository.find_by_id.return_value = None

        # Act & Assert
        with pytest.raises(AppError) as exc_info:
            await interactor.execute(input_data, ip_address)

        assert exc_info.value.internal_code == 1005

    async def test_execute_whenReplyToBonfire_usesParentDecayAt(
        self,
        interactor: PostSparkInteractor,
        mock_spark_repository: AsyncMock,
        mock_bonfire_repository: AsyncMock,
        mock_bonfire: Bonfire,
    ) -> None:
        """Test reply uses parent bonfire's decay_at."""
        # Arrange
        input_data = PostSparkInput(
            content="Reply content",
            parent_bonfire_id="bonfire-001",
        )
        ip_address = "192.168.1.1"
        mock_bonfire_repository.find_by_id.return_value = mock_bonfire

        mock_spark = Spark.create(
            spark_id="reply-id",
            content=input_data.content,
            user_hash="test-user-hash",
            decay_after_seconds=600,
            vanish_after_days=30,
            parent_bonfire_id="bonfire-001",
            decay_at=mock_bonfire.decay_at,
        )
        mock_spark_repository.save.return_value = mock_spark

        # Act
        await interactor.execute(input_data, ip_address)

        # Assert
        saved_spark = mock_spark_repository.save.call_args[0][0]
        assert saved_spark.parent_bonfire_id == "bonfire-001"
        assert saved_spark.decay_at == mock_bonfire.decay_at

    async def test_execute_whenReplyToBonfire_publishesToBonfireChannel(
        self,
        interactor: PostSparkInteractor,
        mock_spark_repository: AsyncMock,
        mock_pubsub_gateway: AsyncMock,
        mock_bonfire_repository: AsyncMock,
        mock_bonfire: Bonfire,
    ) -> None:
        """Test reply publishes to bonfire-specific channel."""
        # Arrange
        input_data = PostSparkInput(
            content="Reply content",
            parent_bonfire_id="bonfire-001",
        )
        ip_address = "192.168.1.1"
        mock_bonfire_repository.find_by_id.return_value = mock_bonfire

        mock_spark = Spark.create(
            spark_id="reply-id",
            content=input_data.content,
            user_hash="test-user-hash",
            decay_after_seconds=600,
            vanish_after_days=30,
            parent_bonfire_id="bonfire-001",
            decay_at=mock_bonfire.decay_at,
        )
        mock_spark_repository.save.return_value = mock_spark

        # Act
        await interactor.execute(input_data, ip_address)

        # Assert
        mock_pubsub_gateway.publish.assert_called_once()
        call_args = mock_pubsub_gateway.publish.call_args
        assert call_args[0][0] == "bonfire:bonfire-001"  # bonfire-specific channel
        published_message = call_args[0][1]
        assert isinstance(published_message, SparkOutput)
        assert published_message.parent_bonfire_id == "bonfire-001"

    async def test_execute_whenReplyToBonfire_outputIncludesParentBonfireId(
        self,
        interactor: PostSparkInteractor,
        mock_spark_repository: AsyncMock,
        mock_bonfire_repository: AsyncMock,
        mock_bonfire: Bonfire,
    ) -> None:
        """Test reply output includes parent_bonfire_id."""
        # Arrange
        input_data = PostSparkInput(
            content="Reply content",
            parent_bonfire_id="bonfire-001",
        )
        ip_address = "192.168.1.1"
        mock_bonfire_repository.find_by_id.return_value = mock_bonfire

        mock_spark = Spark.create(
            spark_id="reply-id",
            content=input_data.content,
            user_hash="test-user-hash",
            decay_after_seconds=600,
            vanish_after_days=30,
            parent_bonfire_id="bonfire-001",
            decay_at=mock_bonfire.decay_at,
        )
        mock_spark_repository.save.return_value = mock_spark

        # Act
        result = await interactor.execute(input_data, ip_address)

        # Assert
        assert result.parent_bonfire_id == "bonfire-001"

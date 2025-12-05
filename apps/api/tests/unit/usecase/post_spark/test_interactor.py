"""Unit tests for PostSparkInteractor."""

from unittest.mock import AsyncMock, Mock

import pytest

from app.domain.exception import AppError
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
    def interactor(
        self,
        mock_spark_repository: AsyncMock,
        mock_identity_provider: Mock,
        mock_rate_limiter: AsyncMock,
        mock_logger: Mock,
    ) -> PostSparkInteractor:
        """Create PostSparkInteractor instance."""
        return PostSparkInteractor(
            spark_repository=mock_spark_repository,
            identity_provider=mock_identity_provider,
            rate_limiter=mock_rate_limiter,
            logger=mock_logger,
            max_length=500,
            rate_limit_count=10,
            rate_limit_window_seconds=60,
            visible_duration_minutes=10,
            ttl_days=30,
            ng_words=["forbidden_word", "bad_word"],
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
            visible_duration_minutes=10,
            ttl_days=30,
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
            visible_duration_minutes=10,
            ttl_days=30,
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
            visible_duration_minutes=10,
            ttl_days=30,
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
            visible_duration_minutes=10,
            ttl_days=30,
        )
        mock_spark_repository.save.return_value = mock_spark

        # Act
        await interactor.execute(input_data, ip_address)

        # Assert
        assert mock_spark_repository.save.called
        saved_spark = mock_spark_repository.save.call_args[0][0]
        assert saved_spark.content == input_data.content
        assert saved_spark.user_hash == "test-user-hash"

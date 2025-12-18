"""Post Spark UseCase Implementation.

This module implements the business logic for posting a spark.
"""

import uuid
from datetime import datetime

from app.domain.constants import LOG_EVENTS
from app.domain.exception import AppError
from app.domain.model.spark import Spark
from app.domain.repository.bonfire_repository import IBonfireRepository
from app.domain.repository.spark_repository import ISparkRepository
from app.domain.service.identity_provider import IIdentityProvider
from app.domain.service.rate_limiter import IRateLimiter
from app.usecase.dto.spark_dto import PostSparkInput, SparkOutput
from app.usecase.ports.logger import ILogger
from app.usecase.ports.pubsub import IPubSubGateway
from app.usecase.post_spark.interface import IPostSparkUseCase


class PostSparkInteractor(IPostSparkUseCase):
    """Interactor for posting a spark."""

    def __init__(
        self,
        spark_repository: ISparkRepository,
        identity_provider: IIdentityProvider,
        rate_limiter: IRateLimiter,
        logger: ILogger,
        pubsub_gateway: IPubSubGateway,
        bonfire_repository: IBonfireRepository,
        max_length: int,
        rate_limit_count: int,
        rate_limit_window_seconds: int,
        decay_after_seconds: int,
        vanish_after_days: int,
        ng_words: list[str],
        pubsub_channel: str,
    ) -> None:
        """Initialize the interactor.

        Args:
            spark_repository: Repository for spark persistence
            identity_provider: Provider for user hash generation
            rate_limiter: Rate limiter for preventing spam
            logger: Logger for structured logging
            pubsub_gateway: Gateway for pub/sub messaging
            bonfire_repository: Repository for bonfire operations
            max_length: Maximum character length for content
            rate_limit_count: Maximum posts per window
            rate_limit_window_seconds: Rate limit window in seconds
            decay_after_seconds: Duration in seconds until spark decays
            vanish_after_days: Days until physical deletion
            ng_words: List of prohibited words
            pubsub_channel: Redis pub/sub channel name

        """
        self.spark_repository = spark_repository
        self.identity_provider = identity_provider
        self.rate_limiter = rate_limiter
        self.logger = logger
        self.pubsub_gateway = pubsub_gateway
        self.bonfire_repository = bonfire_repository
        self.max_length = max_length
        self.rate_limit_count = rate_limit_count
        self.rate_limit_window_seconds = rate_limit_window_seconds
        self.decay_after_seconds = decay_after_seconds
        self.vanish_after_days = vanish_after_days
        self.ng_words = ng_words
        self.pubsub_channel = pubsub_channel

    async def execute(
        self,
        input_data: PostSparkInput,
        ip_address: str,
    ) -> SparkOutput:
        """Execute the post spark use case.

        Args:
            input_data: Input data containing spark content
            ip_address: Client IP address for user identification

        Returns:
            The created spark details

        Raises:
            AppError: If validation fails or rate limit is exceeded

        """
        self.logger.info(
            LOG_EVENTS.SPARK_POST_STARTED,
            "Starting spark post",
            context={"content_length": len(input_data.content)},
        )

        # Validate content length
        if len(input_data.content) > self.max_length:
            self.logger.warning(
                LOG_EVENTS.SPARK_VALIDATION_FAILED,
                "Content length exceeds limit",
                context={
                    "content_length": len(input_data.content),
                    "max_length": self.max_length,
                },
            )
            raise AppError(internal_code=1003)

        # Check for NG words
        content_lower = input_data.content.lower()
        # TODO@Gaomond: O(N * M) Operation. (N: NGワード数, M: 本文長)
        for ng_word in self.ng_words:
            if ng_word.lower() in content_lower:
                self.logger.warning(
                    LOG_EVENTS.SPARK_NG_WORD_DETECTED,
                    "NG word detected in content",
                    context={"ng_word": ng_word},
                )
                raise AppError(internal_code=1002)

        # Generate user hash
        user_hash = self.identity_provider.get_user_hash(ip_address)

        # Check rate limit
        within_limit = await self.rate_limiter.check_and_increment(
            user_hash=user_hash,
            limit=self.rate_limit_count,
            window_seconds=self.rate_limit_window_seconds,
        )

        if not within_limit:
            self.logger.warning(
                LOG_EVENTS.SPARK_RATE_LIMIT_EXCEEDED,
                "Rate limit exceeded",
                context={"user_hash": user_hash},
            )
            raise AppError(internal_code=1004)

        # Handle reply case: check parent bonfire and get its decay_at
        parent_bonfire_id = input_data.parent_bonfire_id
        decay_at: datetime | None = None

        if parent_bonfire_id:
            bonfire = await self.bonfire_repository.find_by_id(parent_bonfire_id)
            if bonfire is None:
                self.logger.warning(
                    LOG_EVENTS.BONFIRE_NOT_FOUND,
                    "Parent bonfire not found for reply",
                    context={"bonfire_id": parent_bonfire_id},
                )
                raise AppError(internal_code=1005)
            decay_at = bonfire.decay_at

        # Create spark entity
        spark = Spark.create(
            spark_id=str(uuid.uuid4()),
            content=input_data.content,
            user_hash=user_hash,
            decay_after_seconds=self.decay_after_seconds,
            vanish_after_days=self.vanish_after_days,
            parent_bonfire_id=parent_bonfire_id,
            decay_at=decay_at,
        )

        # Save to repository
        saved_spark = await self.spark_repository.save(spark)

        # Map to output DTO
        spark_output = SparkOutput(
            id=saved_spark.id,
            content=saved_spark.content,
            parent_bonfire_id=saved_spark.parent_bonfire_id,
            created_at=saved_spark.created_at,
            decay_at=saved_spark.decay_at,
        )

        # Determine publish channel: bonfire-specific for replies, global for sparks
        if parent_bonfire_id:
            channel = f"bonfire:{parent_bonfire_id}"
        else:
            channel = self.pubsub_channel

        # Publish to Redis pub/sub for real-time streaming
        await self.pubsub_gateway.publish(channel, spark_output)

        self.logger.info(
            LOG_EVENTS.SPARK_POST_SUCCESS,
            "Spark posted successfully",
            context={
                "spark_id": saved_spark.id,
                "is_reply": parent_bonfire_id is not None,
            },
        )

        return spark_output

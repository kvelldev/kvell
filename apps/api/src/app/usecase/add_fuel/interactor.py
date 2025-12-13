"""Add Fuel Interactor.

This module implements the business logic for adding fuel to sparks.
"""

from datetime import UTC, datetime

from pymongo.errors import PyMongoError
from tenacity import (
    AsyncRetrying,
    RetryCallState,
    retry_if_exception,
    stop_after_attempt,
    wait_exponential,
)

from app.domain.constants import LOG_EVENTS
from app.domain.exception import AppError
from app.domain.model.spark import SparkLevel
from app.domain.repository.spark_repository import ISparkRepository
from app.domain.service.bonfire_service import BonfireService
from app.usecase.add_fuel.interface import (
    AddFuelInput,
    AddFuelOutput,
    IAddFuelUseCase,
)
from app.usecase.check_promotion.interface import (
    CheckPromotionInput,
    ICheckPromotionUseCase,
)
from app.usecase.ports.logger import ILogger
from app.usecase.ports.pubsub import IPubSubGateway


def _is_transient_transaction_error(exception: BaseException) -> bool:
    """Check if exception is a MongoDB TransientTransactionError.

    Args:
        exception: The exception to check

    Returns:
        True if this is a transient transaction error that can be retried

    """
    # If it's an AppError, check the cause
    if isinstance(exception, AppError):
        cause = exception.cause
        if cause and isinstance(cause, PyMongoError):
            return cause.has_error_label("TransientTransactionError")
        return False

    # Direct PyMongoError check
    if isinstance(exception, PyMongoError):
        return exception.has_error_label("TransientTransactionError")

    return False


class AddFuelInteractor(IAddFuelUseCase):
    """Interactor for adding fuel to a spark."""

    MAX_RETRY_ATTEMPTS = 3
    RETRY_WAIT_MIN_SECONDS = 0.01  # 10ms
    RETRY_WAIT_MAX_SECONDS = 1.0  # 1s

    def __init__(
        self,
        spark_repository: ISparkRepository,
        check_promotion: ICheckPromotionUseCase,
        bonfire_service: BonfireService,
        pubsub: IPubSubGateway,
        logger: ILogger,
    ) -> None:
        """Initialize the interactor.

        Args:
            spark_repository: Repository for spark operations
            check_promotion: UseCase for checking promotions
            bonfire_service: Service for bonfire operations
            pubsub: PubSub gateway for broadcasting events
            logger: Logger for structured logging

        """
        self.spark_repository = spark_repository
        self.check_promotion = check_promotion
        self.bonfire_service = bonfire_service
        self.pubsub = pubsub
        self.logger = logger

    async def execute(self, input_data: AddFuelInput) -> AddFuelOutput:
        """Add fuel to a spark.

        Business rules:
        1. Spark must exist (else error 1005)
        2. Spark must not be decayed (else error 1001)
        3. Users cannot fuel their own sparks (success, no increment)
        4. Users can only fuel a spark once (idempotent, no increment)
        5. After fuel added: check promotion (Spark/Kindling) or extend (Bonfire)

        Args:
            input_data: Input data containing spark_id and user_hash

        Returns:
            Output indicating success and promotion status

        Raises:
            AppError: If spark not found (1005) or already decayed (1001)

        """
        self.logger.info(
            LOG_EVENTS.FUEL_ADD_STARTED,
            "Add fuel request received",
            context={
                "spark_id": input_data.spark_id,
                "user_hash": input_data.user_hash,
            },
        )

        # 1. Find the spark
        spark = await self.spark_repository.find_by_id(input_data.spark_id)

        if spark is None:
            self.logger.warning(
                LOG_EVENTS.FUEL_SPARK_NOT_FOUND,
                "Spark not found",
                context={"spark_id": input_data.spark_id},
            )
            raise AppError(internal_code=1005)

        # 2. Check if spark is still active (not decayed)
        now = datetime.now(UTC)
        if spark.decay_at <= now:
            self.logger.warning(
                LOG_EVENTS.FUEL_SPARK_DECAYED,
                "Spark has already decayed",
                context={
                    "spark_id": input_data.spark_id,
                    "decay_at": spark.decay_at.isoformat(),
                    "now": now.isoformat(),
                },
            )
            raise AppError(internal_code=1001)

        # 3. Check if user is trying to fuel their own spark
        if spark.user_hash == input_data.user_hash:
            self.logger.info(
                LOG_EVENTS.FUEL_SELF_SPARK,
                "User attempted to fuel their own spark (skipped)",
                context={
                    "spark_id": input_data.spark_id,
                    "user_hash": input_data.user_hash,
                },
            )
            # Return success to show UI effect, but don't increment count
            return AddFuelOutput(success=True)

        # 4. Try to add fuel with retry logic for transient transaction errors
        fuel_added = await self._try_add_fuel_with_retry(
            input_data.spark_id,
            input_data.user_hash,
        )

        if not fuel_added:
            self.logger.info(
                LOG_EVENTS.FUEL_ALREADY_ADDED,
                "User already fueled this spark (idempotent)",
                context={
                    "spark_id": input_data.spark_id,
                    "user_hash": input_data.user_hash,
                },
            )
            return AddFuelOutput(success=True)

        self.logger.info(
            LOG_EVENTS.FUEL_ADD_SUCCESS,
            "Fuel added successfully",
            context={
                "spark_id": input_data.spark_id,
                "fuel_added": fuel_added,
            },
        )

        # 5. Check status and process accordingly
        return await self._process_after_fuel(input_data.spark_id, spark.level)

    async def _process_after_fuel(
        self,
        spark_id: str,
        current_level: SparkLevel,
    ) -> AddFuelOutput:
        """Process promotion or extension after fuel is added.

        Args:
            spark_id: ID of the spark
            current_level: Current level of the spark

        Returns:
            Output with promotion/extension status

        """
        # If already Bonfire, extend TTL
        if current_level == SparkLevel.BONFIRE:
            return await self._extend_bonfire(spark_id)

        # Otherwise, check for promotion (Spark/Kindling)
        return await self._check_and_promote(spark_id)

    async def _check_and_promote(self, spark_id: str) -> AddFuelOutput:
        """Check and execute promotion for Spark/Kindling.

        Args:
            spark_id: ID of the spark to check

        Returns:
            Output with promotion status

        """
        promotion_result = await self.check_promotion.execute(
            CheckPromotionInput(spark_id=spark_id)
        )

        return AddFuelOutput(
            success=True,
            promoted=promotion_result.promoted,
            previous_level=promotion_result.previous_level,
            current_level=promotion_result.current_level,
            bonfire_created=promotion_result.bonfire_created,
        )

    async def _extend_bonfire(self, spark_id: str) -> AddFuelOutput:
        """Extend bonfire TTL when fuel is added.

        Args:
            spark_id: ID of the original spark (now bonfire)

        Returns:
            Output indicating success (no promotion since already bonfire)

        """
        bonfire = await self.bonfire_service.find_by_spark_id(spark_id)

        if bonfire is None:
            self.logger.warning(
                LOG_EVENTS.BONFIRE_NOT_FOUND,
                "Bonfire not found for spark",
                context={"spark_id": spark_id},
            )
            return AddFuelOutput(success=True)

        extended_bonfire, was_extended = await self.bonfire_service.extend_by_fuel(
            bonfire
        )

        if was_extended:
            self.logger.info(
                LOG_EVENTS.BONFIRE_EXTENDED,
                "Bonfire TTL extended by fuel",
                context={
                    "bonfire_id": bonfire.id,
                    "spark_id": spark_id,
                    "new_decay_at": extended_bonfire.decay_at.isoformat(),
                },
            )

            # Broadcast extension event
            await self.pubsub.publish(
                "bonfire_events",
                {
                    "type": "bonfire_extended",
                    "bonfire_id": bonfire.id,
                    "spark_id": spark_id,
                    "new_decay_at": extended_bonfire.decay_at.isoformat(),
                    "timestamp": datetime.now(UTC).isoformat(),
                },
            )

        return AddFuelOutput(success=True)

    async def _try_add_fuel_with_retry(
        self,
        spark_id: str,
        user_hash: str,
    ) -> bool:
        """Try to add fuel with automatic retry on transient transaction errors.

        Uses tenacity to retry on MongoDB TransientTransactionError with
        exponential backoff.

        Args:
            spark_id: The spark ID to add fuel to
            user_hash: The user hash attempting to add fuel

        Returns:
            True if fuel was added (first time), False if user already fueled

        Raises:
            AppError: If database operation fails after all retries

        """

        def _before_sleep(retry_state: RetryCallState) -> None:
            """Log before each retry attempt."""
            attempt_number = retry_state.attempt_number
            exception = retry_state.outcome.exception() if retry_state.outcome else None
            self.logger.warning(
                LOG_EVENTS.FUEL_RETRY_ATTEMPT,
                (
                    f"Retrying add fuel due to transient error "
                    f"(attempt {attempt_number}/{self.MAX_RETRY_ATTEMPTS})"
                ),
                context={
                    "spark_id": spark_id,
                    "user_hash": user_hash,
                    "attempt": attempt_number,
                    "exception": str(exception) if exception else None,
                },
            )

        try:
            # Use AsyncRetrying for async functions
            async for attempt in AsyncRetrying(
                retry=retry_if_exception(_is_transient_transaction_error),
                stop=stop_after_attempt(self.MAX_RETRY_ATTEMPTS),
                wait=wait_exponential(
                    min=self.RETRY_WAIT_MIN_SECONDS,
                    max=self.RETRY_WAIT_MAX_SECONDS,
                ),
                before_sleep=_before_sleep,
                reraise=True,
            ):
                with attempt:
                    return await self.spark_repository.try_add_fuel(
                        spark_id,
                        user_hash,
                    )
        except AppError as e:
            # If all retries exhausted, log and re-raise
            if _is_transient_transaction_error(e.cause) if e.cause else False:
                self.logger.exception(
                    LOG_EVENTS.FUEL_RETRY_EXHAUSTED,
                    (
                        f"Failed to add fuel after "
                        f"{self.MAX_RETRY_ATTEMPTS} retry attempts"
                    ),
                    error=e,
                    context={
                        "spark_id": spark_id,
                        "user_hash": user_hash,
                        "max_attempts": self.MAX_RETRY_ATTEMPTS,
                    },
                )
            raise

        # This should never be reached due to reraise=True
        msg = "Unexpected state: retry exhausted without exception"
        raise RuntimeError(msg)

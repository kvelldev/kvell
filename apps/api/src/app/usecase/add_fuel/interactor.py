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
from app.domain.repository.spark_repository import ISparkRepository
from app.usecase.add_fuel.interface import (
    AddFuelInput,
    AddFuelOutput,
    IAddFuelUseCase,
)
from app.usecase.ports.logger import ILogger


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
        logger: ILogger,
    ) -> None:
        """Initialize the interactor.

        Args:
            spark_repository: Repository for spark operations
            logger: Logger for structured logging

        """
        self.spark_repository = spark_repository
        self.logger = logger

    async def execute(self, input_data: AddFuelInput) -> AddFuelOutput:
        """Add fuel to a spark.

        Business rules:
        1. Spark must exist (else error 1005)
        2. Spark must not be decayed (else error 1001)
        3. Users cannot fuel their own sparks (success, no increment)
        4. Users can only fuel a spark once (idempotent, no increment)

        Args:
            input_data: Input data containing spark_id and user_hash

        Returns:
            Output indicating success (without revealing fuel count)

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
        else:
            self.logger.info(
                LOG_EVENTS.FUEL_ADD_SUCCESS,
                "Fuel added successfully",
                context={
                    "spark_id": input_data.spark_id,
                    "fuel_added": fuel_added,
                },
            )

        # Always return success (UI effect is shown regardless)
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

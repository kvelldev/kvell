"""Check Promotion Interactor.

This module implements the business logic for checking and executing
spark promotions (Spark -> Kindling -> Bonfire).
"""

from datetime import UTC, datetime, timedelta

from app.domain.constants import (
    BONFIRE_INITIAL_TTL_HOURS,
    FUEL_WEIGHT,
    KINDLING_DECAY_HOURS,
    KINDLING_THRESHOLD_UU,
    LOG_EVENTS,
    REPLY_WEIGHT,
)
from app.domain.exception import AppError
from app.domain.model.bonfire import Bonfire
from app.domain.model.spark import SparkLevel
from app.domain.model.spark_engagement import SparkEngagement
from app.domain.repository.bonfire_repository import IBonfireRepository
from app.domain.repository.spark_repository import ISparkRepository
from app.domain.repository.threshold_config_repository import IThresholdConfigRepository
from app.domain.service.ignition_service import IgnitionService
from app.usecase.check_promotion.interface import (
    CheckPromotionInput,
    CheckPromotionOutput,
    ICheckPromotionUseCase,
)
from app.usecase.ports.logger import ILogger
from app.usecase.ports.pubsub import IPubSubGateway


class CheckPromotionInteractor(ICheckPromotionUseCase):
    """Interactor for checking and executing spark promotions."""

    def __init__(
        self,
        spark_repository: ISparkRepository,
        bonfire_repository: IBonfireRepository,
        threshold_config: IThresholdConfigRepository,
        ignition_service: IgnitionService,
        pubsub: IPubSubGateway,
        logger: ILogger,
    ) -> None:
        """Initialize the interactor.

        Args:
            spark_repository: Repository for spark operations
            bonfire_repository: Repository for bonfire operations
            threshold_config: Repository for threshold configuration
            ignition_service: Domain service for promotion logic
            pubsub: PubSub gateway for broadcasting events
            logger: Logger for structured logging

        """
        self.spark_repository = spark_repository
        self.bonfire_repository = bonfire_repository
        self.threshold_config = threshold_config
        self.ignition_service = ignition_service
        self.pubsub = pubsub
        self.logger = logger

    async def execute(self, input_data: CheckPromotionInput) -> CheckPromotionOutput:
        """Check and execute spark promotion.

        Promotion Flow:
        1. Fetch spark and engagement metrics
        2. Get current thresholds from config
        3. Use IgnitionService to determine if promotion should occur
        4. If promoting to Kindling: extend TTL
        5. If promoting to Bonfire: create Bonfire entity
        6. Broadcast promotion event via PubSub

        Args:
            input_data: Input containing spark_id

        Returns:
            Output indicating promotion result

        Raises:
            AppError: If spark not found (1005)

        """
        self.logger.info(
            LOG_EVENTS.PROMOTION_CHECK_STARTED,
            "Checking promotion for spark",
            context={"spark_id": input_data.spark_id},
        )

        # 1. Find the spark
        spark = await self.spark_repository.find_by_id(input_data.spark_id)
        if spark is None:
            self.logger.warning(
                LOG_EVENTS.BONFIRE_NOT_FOUND,
                "Spark not found for promotion check",
                context={"spark_id": input_data.spark_id},
            )
            raise AppError(internal_code=1005)

        previous_level = spark.level

        # 2. Get engagement metrics with fixed weights
        engagement = await self.spark_repository.get_engagement(
            input_data.spark_id,
            fuel_weight=FUEL_WEIGHT,
            reply_weight=REPLY_WEIGHT,
        )
        if engagement is None:
            # Spark exists but has no engagement yet - return early
            self.logger.info(
                LOG_EVENTS.PROMOTION_NOT_NEEDED,
                "No engagement for spark, skipping promotion check",
                context={"spark_id": input_data.spark_id},
            )
            return CheckPromotionOutput(
                spark_id=input_data.spark_id,
                promoted=False,
                previous_level=previous_level,
                current_level=previous_level,
                bonfire_created=False,
            )

        # 3. Get dynamic thresholds from Redis
        bonfire_threshold = await self.threshold_config.get_bonfire_threshold_uu()
        heat_threshold = await self.threshold_config.get_heat_score_threshold()

        # 4. Check promotion using domain service
        promotion_result = self.ignition_service.check_promotion(
            current_level=previous_level,
            engagement=engagement,
            kindling_threshold_uu=KINDLING_THRESHOLD_UU,
            bonfire_threshold_uu=bonfire_threshold,
            heat_score_threshold=heat_threshold,
        )

        if not promotion_result.should_promote:
            self.logger.info(
                LOG_EVENTS.PROMOTION_NOT_NEEDED,
                "No promotion needed",
                context={
                    "spark_id": input_data.spark_id,
                    "reason": promotion_result.reason,
                },
            )
            return CheckPromotionOutput(
                spark_id=input_data.spark_id,
                promoted=False,
                previous_level=previous_level,
                current_level=previous_level,
                bonfire_created=False,
            )

        # 5. Execute promotion
        bonfire_created = False

        if promotion_result.target_level == SparkLevel.KINDLING:
            await self._promote_to_kindling(input_data.spark_id)
        elif promotion_result.target_level == SparkLevel.BONFIRE:
            await self._promote_to_bonfire(
                spark_id=input_data.spark_id,
                field_id=spark.field_id,
                content=spark.content,
                engagement=engagement,
            )
            bonfire_created = True

        # 6. Update spark level
        await self.spark_repository.update_level(
            input_data.spark_id,
            promotion_result.target_level,
        )

        # 7. Broadcast promotion event
        await self._broadcast_promotion(
            spark_id=input_data.spark_id,
            new_level=promotion_result.target_level,
            bonfire_created=bonfire_created,
        )

        return CheckPromotionOutput(
            spark_id=input_data.spark_id,
            promoted=True,
            previous_level=previous_level,
            current_level=promotion_result.target_level,
            bonfire_created=bonfire_created,
        )

    async def _promote_to_kindling(self, spark_id: str) -> None:
        """Promote spark to kindling (extend TTL).

        Args:
            spark_id: ID of the spark to promote

        """
        new_decay_at = datetime.now(UTC) + timedelta(hours=KINDLING_DECAY_HOURS)

        await self.spark_repository.update_decay_at(spark_id, new_decay_at)

        self.logger.info(
            LOG_EVENTS.PROMOTION_TO_KINDLING,
            "Spark promoted to kindling",
            context={
                "spark_id": spark_id,
                "new_decay_at": new_decay_at.isoformat(),
            },
        )

    async def _promote_to_bonfire(
        self,
        spark_id: str,
        field_id: str,
        content: str,
        engagement: SparkEngagement,
    ) -> None:
        """Promote spark to bonfire (create Bonfire entity).

        Args:
            spark_id: ID of the spark to promote
            content: Spark content
            engagement: Engagement metrics

        """
        bonfire = Bonfire.create(
            spark_id=spark_id,
            field_id=field_id,
            content=content,
            unique_user_count=engagement.unique_user_count,
            heat_score=engagement.heat_score,
            initial_decay_hours=BONFIRE_INITIAL_TTL_HOURS,
        )

        await self.bonfire_repository.save(bonfire)

        self.logger.info(
            LOG_EVENTS.PROMOTION_TO_BONFIRE,
            "Spark promoted to bonfire",
            context={
                "spark_id": spark_id,
                "bonfire_id": bonfire.id,
                "unique_user_count": engagement.unique_user_count,
                "heat_score": engagement.heat_score,
            },
        )

    async def _broadcast_promotion(
        self,
        spark_id: str,
        new_level: SparkLevel,
        bonfire_created: bool,
    ) -> None:
        """Broadcast promotion event via PubSub.

        Args:
            spark_id: ID of the promoted spark
            new_level: New level after promotion
            bonfire_created: Whether a bonfire was created

        """
        # Calculate new specific decay_at based on level
        # Note: Ideally we should pass the actual new decay_at from the modification methods
        # but for now we'll fetch or estimate it.
        # Since we just updated it in step 6 (update_level), we might need to fetch it again
        # or pass it from _promote_to_kindling/_promote_to_bonfire.
        # However, to keep it simple and consistent with the plan, let's fetch the updated spark.
        spark = await self.spark_repository.find_by_id(spark_id)
        if not spark:
            return

        event_data = {
            "type": "spark_updated",
            "spark_id": spark_id,
            "level": new_level.value,
            "decay_at": spark.decay_at.isoformat().replace("+00:00", "Z"),
            "bonfire_id": spark.id if bonfire_created else None,
        }

        channel = f"timeline:{spark.field_id}"
        await self.pubsub.publish(channel, event_data)

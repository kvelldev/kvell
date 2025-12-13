"""Dependency Injection Configuration.

This module defines FastAPI dependencies for dependency injection.
Following the Dependency Inversion Principle, dependencies are injected
through FastAPI's Depends mechanism, making testing easier through
dependency_overrides.
"""

from typing import Any

from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorDatabase
from redis.asyncio import Redis

from app.adapter.gateways.mongo_bonfire_repository import MongoBonfireRepository
from app.adapter.gateways.mongo_health_repository import MongoHealthRepository
from app.adapter.gateways.mongo_spark_repository import MongoSparkRepository
from app.adapter.gateways.redis_pubsub_gateway import RedisPubSubGateway
from app.adapter.gateways.redis_rate_limiter import RedisRateLimiter
from app.adapter.gateways.redis_threshold_config import RedisThresholdConfigRepository
from app.adapter.gateways.simple_ip_provider import SimpleIPProvider
from app.adapter.infra.database import Database
from app.adapter.infra.logger import JsonLogger
from app.adapter.infra.redis_client import RedisClient
from app.adapter.infra.settings import settings
from app.domain.repository.bonfire_repository import IBonfireRepository
from app.domain.repository.health_repository import IHealthRepository
from app.domain.repository.spark_repository import ISparkRepository
from app.domain.repository.threshold_config_repository import IThresholdConfigRepository
from app.domain.service.identity_provider import IIdentityProvider
from app.domain.service.ignition_service import IgnitionService
from app.domain.service.rate_limiter import IRateLimiter
from app.domain.service.bonfire_service import BonfireService
from app.usecase.add_fuel.interactor import AddFuelInteractor
from app.usecase.add_fuel.interface import IAddFuelUseCase
from app.usecase.check_promotion.interactor import CheckPromotionInteractor
from app.usecase.check_promotion.interface import ICheckPromotionUseCase
from app.usecase.get_bonfires.interactor import GetActiveBonfiresInteractor
from app.usecase.get_bonfires.interface import IGetActiveBonfiresUseCase
from app.usecase.health_check.interactor import HealthCheckInteractor
from app.usecase.health_check.interface import IHealthCheckUseCase
from app.usecase.ports.logger import ILogger
from app.usecase.ports.pubsub import IPubSubGateway
from app.usecase.post_spark.interactor import PostSparkInteractor
from app.usecase.post_spark.interface import IPostSparkUseCase
from app.usecase.stream_timeline.interactor import StreamTimelineInteractor
from app.usecase.stream_timeline.interface import IStreamTimelineUseCase


def get_db() -> AsyncIOMotorDatabase[Any]:
    """Get the database instance.

    This is the base dependency that provides the MongoDB connection.
    Can be overridden in tests to use a different database.

    Returns:
        MongoDB database instance

    """
    return Database.get_database()


def get_logger() -> ILogger:
    """Get the logger instance.

    This dependency provides the application logger.
    Can be overridden in tests to use a mock logger.

    Returns:
        Logger instance

    """
    return JsonLogger(service_name="kvell-api")


def get_health_repository(
    db: AsyncIOMotorDatabase[Any] = Depends(get_db),
    logger: ILogger = Depends(get_logger),
) -> IHealthRepository:
    """Get the health repository instance.

    This dependency chains from get_db() and provides the health repository.
    Can be overridden in tests to use a mock repository.

    Args:
        db: MongoDB database instance (injected)
        logger: Logger instance (injected)

    Returns:
        Health repository instance

    """
    return MongoHealthRepository(db, logger)


def get_health_usecase(
    repo: IHealthRepository = Depends(get_health_repository),
    logger: ILogger = Depends(get_logger),
) -> IHealthCheckUseCase:
    """Get the health check use case instance.

    This dependency chains from get_health_repository() and provides
    the use case interactor. Can be overridden in tests to use a mock use case.

    Args:
        repo: Health repository instance (injected)
        logger: Logger instance (injected)

    Returns:
        Health check use case instance

    """
    return HealthCheckInteractor(repo, logger)


# Spark Dependencies


def get_redis() -> Redis:  # type: ignore[type-arg]
    """Get the Redis client instance.

    Returns:
        Redis client instance

    """
    return RedisClient.get_client()


def get_spark_repository(
    db: AsyncIOMotorDatabase[Any] = Depends(get_db),
    logger: ILogger = Depends(get_logger),
) -> ISparkRepository:
    """Get the spark repository instance.

    Args:
        db: MongoDB database instance (injected)
        logger: Logger instance (injected)

    Returns:
        Spark repository instance

    """
    return MongoSparkRepository(db, logger)


def get_identity_provider() -> IIdentityProvider:
    """Get the identity provider instance.

    Returns:
        Identity provider instance

    """
    return SimpleIPProvider(secret_key=settings.identity_secret_key)


def get_rate_limiter(
    redis: Redis = Depends(get_redis),  # type: ignore[type-arg]
) -> IRateLimiter:
    """Get the rate limiter instance.

    Args:
        redis: Redis client instance (injected)

    Returns:
        Rate limiter instance

    """
    return RedisRateLimiter(redis)


def get_pubsub_gateway(
    redis: Redis = Depends(get_redis),  # type: ignore[type-arg]
    logger: ILogger = Depends(get_logger),
) -> IPubSubGateway:
    """Get the pub/sub gateway instance.

    Args:
        redis: Redis client instance (injected)
        logger: Logger instance (injected)

    Returns:
        Pub/sub gateway instance

    """
    return RedisPubSubGateway(redis, logger)


def get_post_spark_usecase(
    spark_repository: ISparkRepository = Depends(get_spark_repository),
    identity_provider: IIdentityProvider = Depends(get_identity_provider),
    rate_limiter: IRateLimiter = Depends(get_rate_limiter),
    logger: ILogger = Depends(get_logger),
    pubsub_gateway: IPubSubGateway = Depends(get_pubsub_gateway),
) -> IPostSparkUseCase:
    """Get the post spark use case instance.

    Args:
        spark_repository: Spark repository instance (injected)
        identity_provider: Identity provider instance (injected)
        rate_limiter: Rate limiter instance (injected)
        logger: Logger instance (injected)
        pubsub_gateway: Pub/sub gateway instance (injected)

    Returns:
        Post spark use case instance

    """
    return PostSparkInteractor(
        spark_repository=spark_repository,
        identity_provider=identity_provider,
        rate_limiter=rate_limiter,
        logger=logger,
        pubsub_gateway=pubsub_gateway,
        max_length=settings.spark_max_length,
        rate_limit_count=settings.spark_rate_limit_count,
        rate_limit_window_seconds=settings.spark_rate_limit_window_seconds,
        decay_after_seconds=settings.spark_decay_after_seconds,
        vanish_after_days=settings.spark_vanish_after_days,
        ng_words=settings.spark_ng_words_list,
        pubsub_channel="sparks:events",
    )


def get_stream_timeline_usecase(
    spark_repository: ISparkRepository = Depends(get_spark_repository),
    pubsub_gateway: IPubSubGateway = Depends(get_pubsub_gateway),
    logger: ILogger = Depends(get_logger),
) -> IStreamTimelineUseCase:
    """Get the stream timeline use case instance.

    Args:
        spark_repository: Spark repository instance (injected)
        pubsub_gateway: Pub/sub gateway instance (injected)
        logger: Logger instance (injected)

    Returns:
        Stream timeline use case instance

    """
    return StreamTimelineInteractor(
        spark_repository=spark_repository,
        pubsub_gateway=pubsub_gateway,
        logger=logger,
        active_spark_seconds=settings.spark_decay_after_seconds,
        pubsub_channel="sparks:events",
    )


# Bonfire Dependencies


def get_bonfire_repository(
    db: AsyncIOMotorDatabase[Any] = Depends(get_db),
    logger: ILogger = Depends(get_logger),
) -> IBonfireRepository:
    """Get the bonfire repository instance.

    Args:
        db: MongoDB database instance (injected)
        logger: Logger instance (injected)

    Returns:
        Bonfire repository instance

    """
    return MongoBonfireRepository(db, logger)


def get_threshold_config(
    redis: Redis = Depends(get_redis),  # type: ignore[type-arg]
    logger: ILogger = Depends(get_logger),
) -> IThresholdConfigRepository:
    """Get the threshold config repository instance.

    Args:
        redis: Redis client instance (injected)
        logger: Logger instance (injected)

    Returns:
        Threshold config repository instance

    """
    return RedisThresholdConfigRepository(redis, logger)


def get_ignition_service() -> IgnitionService:
    """Get the ignition service instance.

    Returns:
        Ignition service instance

    """
    return IgnitionService()


def get_check_promotion_usecase(
    spark_repository: ISparkRepository = Depends(get_spark_repository),
    bonfire_repository: IBonfireRepository = Depends(get_bonfire_repository),
    threshold_config: IThresholdConfigRepository = Depends(get_threshold_config),
    ignition_service: IgnitionService = Depends(get_ignition_service),
    pubsub: IPubSubGateway = Depends(get_pubsub_gateway),
    logger: ILogger = Depends(get_logger),
) -> ICheckPromotionUseCase:
    """Get the check promotion use case instance.

    Args:
        spark_repository: Spark repository instance (injected)
        bonfire_repository: Bonfire repository instance (injected)
        threshold_config: Threshold config repository instance (injected)
        ignition_service: Ignition service instance (injected)
        pubsub: PubSub gateway instance (injected)
        logger: Logger instance (injected)

    Returns:
        Check promotion use case instance

    """
    return CheckPromotionInteractor(
        spark_repository=spark_repository,
        bonfire_repository=bonfire_repository,
        threshold_config=threshold_config,
        ignition_service=ignition_service,
        pubsub=pubsub,
        logger=logger,
    )


def get_get_bonfires_usecase(
    bonfire_repository: IBonfireRepository = Depends(get_bonfire_repository),
    logger: ILogger = Depends(get_logger),
) -> IGetActiveBonfiresUseCase:
    """Get the get active bonfires use case instance.

    Args:
        bonfire_repository: Bonfire repository instance (injected)
        logger: Logger instance (injected)

    Returns:
        Get active bonfires use case instance

    """
    return GetActiveBonfiresInteractor(
        bonfire_repository=bonfire_repository,
        logger=logger,
    )


def get_bonfire_service(
    bonfire_repository: IBonfireRepository = Depends(get_bonfire_repository),
) -> BonfireService:
    """Get the bonfire service instance.

    Args:
        bonfire_repository: Bonfire repository instance (injected)

    Returns:
        Bonfire service instance

    """
    return BonfireService(
        bonfire_repository=bonfire_repository,
    )


# Add Fuel (depends on Bonfire services)


def get_add_fuel_usecase(
    spark_repository: ISparkRepository = Depends(get_spark_repository),
    check_promotion: ICheckPromotionUseCase = Depends(get_check_promotion_usecase),
    bonfire_service: BonfireService = Depends(get_bonfire_service),
    pubsub: IPubSubGateway = Depends(get_pubsub_gateway),
    logger: ILogger = Depends(get_logger),
) -> IAddFuelUseCase:
    """Get the add fuel use case instance.

    Args:
        spark_repository: Spark repository instance (injected)
        check_promotion: Check promotion use case (injected)
        bonfire_service: Bonfire service (injected)
        pubsub: PubSub gateway instance (injected)
        logger: Logger instance (injected)

    Returns:
        Add fuel use case instance

    """
    return AddFuelInteractor(
        spark_repository=spark_repository,
        check_promotion=check_promotion,
        bonfire_service=bonfire_service,
        pubsub=pubsub,
        logger=logger,
    )

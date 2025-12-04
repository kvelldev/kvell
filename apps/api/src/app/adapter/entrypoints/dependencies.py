"""Dependency Injection Configuration.

This module defines FastAPI dependencies for dependency injection.
Following the Dependency Inversion Principle, dependencies are injected
through FastAPI's Depends mechanism, making testing easier through
dependency_overrides.
"""

from typing import Any

from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.adapter.gateways.mongo_health_repository import MongoHealthRepository
from app.adapter.infra.database import Database
from app.adapter.infra.logger import JsonLogger
from app.domain.repository.health_repository import IHealthRepository
from app.usecase.health_check.interactor import HealthCheckInteractor
from app.usecase.health_check.interface import IHealthCheckUseCase
from app.usecase.ports.logger import ILogger


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

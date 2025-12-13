"""FastAPI Application Entry Point.

This module initializes the FastAPI application with CORS and database connection.
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pymongo.errors import PyMongoError

from app.adapter.entrypoints.bonfire_router import router as bonfire_router
from app.adapter.entrypoints.error_handler import app_error_handler
from app.adapter.entrypoints.health_router import router as health_router
from app.adapter.entrypoints.spark_router import router as spark_router
from app.adapter.gateways.mongo_bonfire_repository import MongoBonfireRepository
from app.adapter.gateways.mongo_spark_repository import MongoSparkRepository
from app.adapter.infra.database import Database
from app.adapter.infra.logger import JsonLogger
from app.adapter.infra.redis_client import RedisClient
from app.adapter.infra.settings import settings
from app.domain.constants import LOG_EVENTS
from app.domain.exception import AppError

if TYPE_CHECKING:
    from app.usecase.ports.logger import ILogger


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """Application lifespan manager.

    Args:
        _app: FastAPI application instance

    Yields:
        None

    """
    logger: ILogger = JsonLogger(service_name="kvell-api")

    # Startup
    logger.info(LOG_EVENTS.APP_STARTUP, "Kvell API starting up")
    try:
        Database.connect()
        logger.info(LOG_EVENTS.APP_STARTUP, "Database connected")
    except (PyMongoError, OSError, ConnectionError) as e:
        logger.exception(
            LOG_EVENTS.APP_STARTUP,
            "Database connection failed",
            error=e,
        )
        raise

    try:
        await RedisClient.connect()
        logger.info(LOG_EVENTS.APP_STARTUP, "Redis connected")
    except (OSError, ConnectionError) as e:
        logger.exception(
            LOG_EVENTS.APP_STARTUP,
            "Redis connection failed",
            error=e,
        )
        raise

    # Create indexes for all collections
    try:
        db = Database.get_database()

        # Spark indexes (includes TTL for automatic deletion)
        spark_repo = MongoSparkRepository(db, logger)
        await spark_repo.ensure_indexes()
        logger.info(LOG_EVENTS.APP_STARTUP, "Spark indexes created")

        # Bonfire indexes (includes TTL for automatic deletion)
        bonfire_repo = MongoBonfireRepository(db, logger)
        await bonfire_repo.ensure_indexes()
        logger.info(LOG_EVENTS.APP_STARTUP, "Bonfire indexes created")

    except PyMongoError as e:
        logger.exception(
            LOG_EVENTS.APP_STARTUP,
            "Failed to create indexes",
            error=e,
        )
        # Critical for TTL and performance - raise to prevent startup
        raise

    yield

    # Shutdown
    logger.info(LOG_EVENTS.APP_SHUTDOWN, "Kvell API shutting down")
    try:
        Database.disconnect()
        logger.info(LOG_EVENTS.APP_SHUTDOWN, "Database disconnected")
    except (PyMongoError, OSError, ConnectionError) as e:
        logger.exception(
            LOG_EVENTS.APP_SHUTDOWN,
            "Database disconnection error",
            error=e,
        )

    try:
        await RedisClient.disconnect()
        logger.info(LOG_EVENTS.APP_SHUTDOWN, "Redis disconnected")
    except (OSError, ConnectionError) as e:
        logger.exception(
            LOG_EVENTS.APP_SHUTDOWN,
            "Redis disconnection error",
            error=e,
        )


# Create FastAPI application
app = FastAPI(
    title="Kvell API",
    description="Kvell Backend API",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register exception handlers using decorator pattern


@app.exception_handler(AppError)
async def handle_app_error(_request: Request, exc: AppError) -> JSONResponse:
    """Handle AppError exceptions.

    Args:
        _request: FastAPI request (unused but required by signature)
        exc: Application error

    Returns:
        JSON response with appropriate HTTP status

    """
    return await app_error_handler(_request, exc)


# Register routers
app.include_router(health_router)
app.include_router(spark_router)
app.include_router(bonfire_router)


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint.

    Returns:
        Welcome message

    """
    return {"message": "Welcome to Kvell API"}

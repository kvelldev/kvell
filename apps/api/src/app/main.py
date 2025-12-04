"""FastAPI Application Entry Point.

This module initializes the FastAPI application with CORS and database connection.
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.adapter.constants import LOG_EVENTS
from app.adapter.entrypoints.error_handler import app_error_handler
from app.adapter.entrypoints.health_router import router as health_router
from app.adapter.infra.database import Database
from app.adapter.infra.logger import JsonLogger
from app.adapter.infra.settings import settings
from app.domain.exception import AppError
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
    except Exception as e:
        logger.error(
            LOG_EVENTS.APP_STARTUP,
            "Database connection failed",
            error=e,
        )
        raise

    yield

    # Shutdown
    logger.info(LOG_EVENTS.APP_SHUTDOWN, "Kvell API shutting down")
    try:
        Database.disconnect()
        logger.info(LOG_EVENTS.APP_SHUTDOWN, "Database disconnected")
    except Exception as e:
        logger.error(
            LOG_EVENTS.APP_SHUTDOWN,
            "Database disconnection error",
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


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint.

    Returns:
        Welcome message

    """
    return {"message": "Welcome to Kvell API"}

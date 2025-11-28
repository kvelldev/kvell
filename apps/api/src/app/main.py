"""FastAPI Application Entry Point.

This module initializes the FastAPI application with CORS and database connection.
"""

import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from adapter.entrypoints.health_router import router as health_router
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from infra.database import Database

# Load environment variables
load_dotenv()


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """Application lifespan manager.

    Args:
        _app: FastAPI application instance

    Yields:
        None

    """
    # Startup
    Database.connect()
    yield
    # Shutdown
    Database.disconnect()


# Create FastAPI application
app = FastAPI(
    title="Kvell API",
    description="Kvell Backend API",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS Configuration
origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(health_router)


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint.

    Returns:
        Welcome message

    """
    return {"message": "Welcome to Kvell API"}

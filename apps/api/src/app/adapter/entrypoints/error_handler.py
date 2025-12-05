"""Global error handler for FastAPI.

Converts application errors to appropriate HTTP responses.
"""

from typing import TYPE_CHECKING, Any

from fastapi import Request, status
from fastapi.responses import JSONResponse

from app.adapter.constants import INTERNAL_TO_HTTP_MAP
from app.adapter.infra.logger import JsonLogger
from app.domain.constants import LOG_EVENTS
from app.domain.exception import AppError

if TYPE_CHECKING:
    from app.usecase.ports.logger import ILogger


async def app_error_handler(_request: Request, exc: AppError) -> JSONResponse:
    """Handle application errors and convert to HTTP responses.

    Args:
        _request: FastAPI request object (unused but required by signature)
        exc: Application error

    Returns:
        JSON response with appropriate HTTP status code

    """
    # Logger instantiation (DI not available in exception handler)
    logger: ILogger = JsonLogger(service_name="kvell-api")

    # Map internal status code to HTTP status code
    http_status = INTERNAL_TO_HTTP_MAP.get(
        exc.internal_code,
        status.HTTP_500_INTERNAL_SERVER_ERROR,
    )

    # Log the error
    logger.error(
        LOG_EVENTS.UNHANDLED_ERROR,
        f"Application error occurred: {exc!s}",
        error=exc.cause if exc.cause else exc,
        context={
            "internal_code": exc.internal_code,
            "http_status": http_status,
            "error_context": exc.context,
        },
    )

    # Build error response
    error_response: dict[str, Any] = {
        "error": {
            "code": exc.internal_code,
            "message": str(exc),
        },
    }

    # Add context if available (for debugging in non-production)
    if exc.context:
        error_response["error"]["context"] = exc.context

    return JSONResponse(
        status_code=http_status,
        content=error_response,
    )

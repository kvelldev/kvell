"""Global error handler for FastAPI.

Converts application errors to appropriate HTTP responses.
"""

from typing import Any

from fastapi import Request, status
from fastapi.responses import JSONResponse

from app.adapter.constants import INTERNAL_TO_HTTP_MAP
from app.domain.exception import AppError


async def app_error_handler(_request: Request, exc: AppError) -> JSONResponse:
    """Handle application errors and convert to HTTP responses.

    Args:
        _request: FastAPI request object (unused but required by signature)
        exc: Application error

    Returns:
        JSON response with appropriate HTTP status code

    """
    # Map internal status code to HTTP status code
    http_status = INTERNAL_TO_HTTP_MAP.get(
        exc.internal_code,
        status.HTTP_500_INTERNAL_SERVER_ERROR,
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

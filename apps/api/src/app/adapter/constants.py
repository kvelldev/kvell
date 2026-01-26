"""HTTP status code mapping constants.

Maps internal status codes to HTTP status codes.
"""

from typing import Final

from fastapi import status

from app.domain.constants import InternalStatusCode

HttpStatusCode = int

INTERNAL_TO_HTTP_MAP: Final[dict[InternalStatusCode, HttpStatusCode]] = {
    # Success
    200: status.HTTP_200_OK,
    201: status.HTTP_201_CREATED,
    204: status.HTTP_204_NO_CONTENT,
    # Domain Logic Errors -> 4xx Errors
    1001: status.HTTP_410_GONE,
    1002: status.HTTP_422_UNPROCESSABLE_CONTENT,
    1003: status.HTTP_422_UNPROCESSABLE_CONTENT,
    1004: status.HTTP_429_TOO_MANY_REQUESTS,
    1005: status.HTTP_404_NOT_FOUND,
    # Infrastructure Errors -> 500 Internal Server Error
    2001: status.HTTP_500_INTERNAL_SERVER_ERROR,
    2002: status.HTTP_500_INTERNAL_SERVER_ERROR,
    # Fallback
    500: status.HTTP_500_INTERNAL_SERVER_ERROR,
}

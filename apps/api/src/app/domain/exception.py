"""Domain exception definitions.

Defines application-specific exceptions with internal status codes.
"""

from contextlib import suppress
from typing import Any

from app.domain.constants import INTERNAL_STATUSES, InternalStatusCode


class AppError(Exception):
    """Base application error with internal status code.

    This exception carries an internal status code that will be mapped
    to an HTTP status code at the adapter layer.
    """

    def __init__(
        self,
        internal_code: InternalStatusCode,
        context: dict[str, Any] | None = None,
        cause: Exception | None = None,
    ) -> None:
        """Initialize the application error.

        Args:
            internal_code: Internal status code
            context: Additional context information
            cause: Original exception if this is wrapping another error

        """
        self.internal_code = internal_code
        self.context = context or {}
        self.cause = cause

        # Get message from internal status
        message = INTERNAL_STATUSES.get(
            internal_code,
            INTERNAL_STATUSES[500],
        )

        # Format message with context if it contains placeholders
        if context:
            with suppress(KeyError, ValueError):
                message = message.format(**context)

        super().__init__(message)

    def __str__(self) -> str:
        """Return string representation of the error.

        Returns:
            Formatted error message with context

        """
        base_msg = super().__str__()
        if self.context:
            return f"{base_msg} (context: {self.context})"
        return base_msg

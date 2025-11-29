"""Logger port interface.

Defines the interface for application logging.
Technical details (Sentry, CloudWatch, Console, etc.) are implemented
in the adapter layer.
"""

from abc import ABC, abstractmethod
from typing import Any


class ILogger(ABC):
    """Logger port interface for application logging.

    Technical details (Sentry, CloudWatch, Console, etc.) are implemented
    in the adapter layer.
    """

    @abstractmethod
    def info(
        self, event_id: str, message: str, context: dict[str, Any] | None = None
    ) -> None:
        """Log informational event.

        Args:
            event_id: Event identifier
            message: Log message
            context: Additional context data

        """

    @abstractmethod
    def warn(
        self, event_id: str, message: str, context: dict[str, Any] | None = None
    ) -> None:
        """Log warning event.

        Warning indicates a state that requires attention but is not an error.

        Args:
            event_id: Event identifier
            message: Log message
            context: Additional context data

        """

    @abstractmethod
    def error(
        self,
        event_id: str,
        message: str,
        error: Exception | None = None,
        context: dict[str, Any] | None = None,
    ) -> None:
        """Log error event.

        In production environment, this triggers notification to error tracking tools.

        Args:
            event_id: Event identifier
            message: Log message
            error: Exception object if available
            context: Additional context data

        """

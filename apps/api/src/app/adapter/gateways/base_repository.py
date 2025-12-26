"""Base Repository.

This module defines the base repository class with common utility methods.
"""

from datetime import UTC, datetime


class BaseRepository:
    """Base repository with common utility methods."""

    @staticmethod
    def _ensure_utc(dt: datetime) -> datetime:
        """Ensure the datetime is timezone-aware (UTC).

        MongoDB returns timezone-naive datetimes representing UTC.
        This method attaches the UTC timezone if it's missing.

        Args:
            dt: The datetime to process

        Returns:
            Timezone-aware datetime (UTC)

        """
        if dt.tzinfo is None:
            return dt.replace(tzinfo=UTC)
        return dt

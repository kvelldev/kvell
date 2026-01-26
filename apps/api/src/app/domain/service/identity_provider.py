"""Identity Provider Interface.

This module defines the interface for generating anonymous user identifiers.
"""

from abc import ABC, abstractmethod


class IIdentityProvider(ABC):
    """Interface for generating anonymous user identifiers."""

    @abstractmethod
    def get_user_hash(self, ip_address: str) -> str:
        """Generate an anonymous user hash from IP address.

        The hash should be rotated daily to prevent long-term tracking.

        Args:
            ip_address: Client IP address

        Returns:
            Anonymized user hash

        """

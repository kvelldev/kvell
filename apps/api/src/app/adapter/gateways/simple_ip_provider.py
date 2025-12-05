"""Simple IP-based Identity Provider Implementation.

This module implements user identification using IP address hashing with daily rotation.
"""

import hashlib
from datetime import UTC, datetime

from app.domain.service.identity_provider import IIdentityProvider


class SimpleIPProvider(IIdentityProvider):
    """Simple IP-based identity provider with daily rotation.

    Generates anonymous user hash from IP address + current date + secret key.
    The hash changes daily to prevent long-term tracking.
    """

    def __init__(self, secret_key: str) -> None:
        """Initialize the provider.

        Args:
            secret_key: Secret key for HMAC hashing

        """
        self.secret_key = secret_key

    def get_user_hash(self, ip_address: str) -> str:
        """Generate an anonymous user hash from IP address.

        The hash includes the current date, so it rotates daily.

        Args:
            ip_address: Client IP address

        Returns:
            Anonymized user hash (hex string)

        """
        # Get current date string (UTC) for daily rotation
        current_date = datetime.now(UTC).strftime("%Y-%m-%d")

        # Combine IP + Date + Secret
        message = f"{ip_address}:{current_date}:{self.secret_key}"

        # Generate SHA256 hash
        return hashlib.sha256(message.encode()).hexdigest()

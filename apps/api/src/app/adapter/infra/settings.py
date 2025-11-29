"""Application settings using pydantic-settings.

This module provides type-safe environment variable management.
Missing required variables will cause startup to fail with clear error messages.
"""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        frozen=True,
    )

    # MongoDB Configuration
    mongo_uri: str = Field(
        default="mongodb://localhost:27017",
        description="MongoDB connection URI",
    )
    mongo_db: str = Field(
        default="kvell",
        description="MongoDB database name",
    )

    # CORS Configuration
    cors_origins: str = Field(
        default="http://localhost:5173",
        description="Comma-separated list of allowed CORS origins",
    )

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS origins into a list.

        Returns:
            List of allowed CORS origins

        """
        return [origin.strip() for origin in self.cors_origins.split(",")]


# Global settings instance (singleton)
settings = Settings()

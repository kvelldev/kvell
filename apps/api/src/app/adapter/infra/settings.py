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
        default="mongodb://localhost:27017/?replicaSet=rs0",
        description="MongoDB connection URI (with replica set for transactions)",
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

    # Redis Configuration
    redis_uri: str = Field(
        default="redis://localhost:6379",
        description="Redis connection URI",
    )

    # Spark Configuration
    spark_max_length: int = Field(
        default=500,
        description="Maximum character length for spark content",
    )
    spark_rate_limit_count: int = Field(
        default=10,
        description="Maximum number of sparks allowed per rate limit window",
    )
    spark_rate_limit_window_seconds: int = Field(
        default=60,
        description="Rate limit window duration in seconds",
    )
    spark_decay_after_seconds: int = Field(
        default=60,
        description="Duration in seconds until a spark decays (becomes invisible)",
    )
    spark_vanish_after_days: int = Field(
        default=30,
        description="Days until spark vanishes (physical deletion via MongoDB TTL)",
    )
    spark_ng_words: str = Field(
        default="forbidden_word",
        description="Comma-separated list of prohibited words",
    )
    identity_secret_key: str = Field(
        default="kvell-secret-key-change-in-production",
        description="Secret key for generating user hash",
    )

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS origins into a list.

        Returns:
            List of allowed CORS origins

        """
        return [origin.strip() for origin in self.cors_origins.split(",")]

    @property
    def spark_ng_words_list(self) -> list[str]:
        """Parse NG words into a list.

        Returns:
            List of prohibited words

        """
        return [word.strip() for word in self.spark_ng_words.split(",") if word.strip()]


# Global settings instance (singleton)
settings = Settings()

/**
 * Application Settings
 *
 * Type-safe environment variable management for frontend.
 * Follows the same pattern as backend settings.py.
 */

/**
 * Application settings loaded from environment variables.
 */
class Settings {
  /**
   * Maximum character length for spark content.
   * Maps to backend's spark_max_length setting.
   */
  readonly sparkMaxLength: number;

  /**
   * Maximum number of sparks allowed per rate limit window.
   * Maps to backend's spark_rate_limit_count setting.
   */
  readonly sparkRateLimitCount: number;

  /**
   * Rate limit window duration in seconds.
   * Maps to backend's spark_rate_limit_window_seconds setting.
   */
  readonly sparkRateLimitWindowSeconds: number;

  /**
   * Duration in minutes that a spark remains visible.
   * Maps to backend's spark_visible_duration_minutes setting.
   */
  readonly sparkVisibleDurationMinutes: number;

  /**
   * Time to live in days before spark is physically deleted.
   * Maps to backend's spark_ttl_days setting.
   */
  readonly sparkTtlDays: number;

  constructor() {
    // Load from Vite environment variables with defaults matching backend
    this.sparkMaxLength = this.parseNumber(
      import.meta.env.VITE_SPARK_MAX_LENGTH as string | undefined,
      500,
    );
    this.sparkRateLimitCount = this.parseNumber(
      import.meta.env.VITE_SPARK_RATE_LIMIT_COUNT as string | undefined,
      10,
    );
    this.sparkRateLimitWindowSeconds = this.parseNumber(
      import.meta.env.VITE_SPARK_RATE_LIMIT_WINDOW_SECONDS as
        | string
        | undefined,
      60,
    );
    this.sparkVisibleDurationMinutes = this.parseNumber(
      import.meta.env.VITE_SPARK_VISIBLE_DURATION_MINUTES as string | undefined,
      10,
    );
    this.sparkTtlDays = this.parseNumber(
      import.meta.env.VITE_SPARK_TTL_DAYS as string | undefined,
      30,
    );

    // Freeze to prevent modifications (immutable)
    Object.freeze(this);
  }

  /**
   * Parse environment variable as number with fallback.
   * @param value - Environment variable value
   * @param defaultValue - Default value if parsing fails
   * @returns Parsed number or default value
   */
  private parseNumber(value: string | undefined, defaultValue: number): number {
    if (!value) return defaultValue;
    const parsed = Number(value);
    return Number.isNaN(parsed) ? defaultValue : parsed;
  }
}

/**
 * Global settings instance (singleton).
 */
export const settings = new Settings();

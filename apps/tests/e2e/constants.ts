/**
 * E2E Test Constants
 *
 * Centralizes database-related constants for E2E testing.
 * DO NOT import these constants into frontend code (apps/web).
 */

/**
 * MongoDB Database Collections
 */
export const DB_COLLECTIONS = {
  HEALTH_MESSAGES: 'health_messages',
  SPARKS: 'sparks',
} as const;

/**
 * MongoDB Connection Settings
 */
export const MONGO_URL = process.env.MONGO_URL || 'mongodb://localhost:27017';
export const DB_NAME = 'kvell';

/**
 * Timeline E2E Test Constants
 */
export const TIMELINE_TEST_CONSTANTS = {
  // System Configuration
  SPARK_LIFETIME_MINUTES: 10,
  COOLING_THRESHOLD_MINUTES: 3,
  LEGAL_RETENTION_DAYS: 30,

  // Test Data Generation
  TEST_SPARK_COUNT: 20, // Number of sparks to exceed screen height
  TEST_SPARK_INTERVAL_MS: 10000, // Time interval between test sparks

  // Timing Tolerances
  SCROLL_BOTTOM_TOLERANCE_PX: 10,
  TIME_COMPARISON_TOLERANCE_MS: 1000,
  ANIMATION_DURATION_MS: 3000,
  SHORT_WAIT_MS: 500,
  EXPIRATION_WAIT_MS: 6000,

  // Visual Effect Thresholds
  WHITE_TEXT_RGB_MIN: 200, // Minimum RGB value for white text
  GRAY_TEXT_RGB_MAX: 200, // Maximum RGB value for gray text
  OPACITY_THRESHOLD: 1.0,

  // Test Spark IDs
  FRESH_SPARK_ID: 'test-fresh-spark',
  SPARK_ID_PREFIX: 'test-spark-',
  EXPIRING_SPARK_USER_HASH: 'test-user-hash-expiring',
  FRESH_SPARK_USER_HASH: 'test-user-hash-fresh',

  // Expiration Test
  EXPIRING_SPARK_VISIBLE_DURATION_MS: 5000,
} as const;

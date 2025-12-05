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
} as const;

/**
 * MongoDB Connection Settings
 */
export const MONGO_URL = process.env.MONGO_URL || 'mongodb://localhost:27017';
export const DB_NAME = 'kvell';

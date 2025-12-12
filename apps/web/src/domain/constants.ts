export const internalStatuses = {
  // Sucess
  200: "OK",
  201: "Created",
  204: "No Content",
  // Client Errors
  400: "Bad Request",
  401: "Unauthorized",
  403: "Forbidden",
  404: "Not Found",
  409: "Conflict",
  422: "Unprocessable Entity",
  // Business Logic Errors
  1001: "Invalid email format.",
  // Server Errors
  500: "Internal Server Error",
} as const;

/**
 * Type representing valid internal status codes.
 */
export type InternalStatusCodes = keyof typeof internalStatuses;

/**
 * Log Event IDs for structured logging.
 * Use these constants in logger calls for testable, consistent event tracking.
 */
export const LOG_EVENTS = {
  // Health Check
  HEALTH_CHECK: {
    FETCH_START: "HEALTH_FETCH_START",
    FETCH_SUCCESS: "HEALTH_FETCH_SUCCESS",
    FETCH_ERROR: "HEALTH_FETCH_ERROR",
    SAVE_START: "HEALTH_SAVE_START",
    SAVE_SUCCESS: "HEALTH_SAVE_SUCCESS",
    SAVE_ERROR: "HEALTH_SAVE_ERROR",
  },
  // Spark Post
  SPARK: {
    POST_START: "SPARK_POST_START",
    POST_SUCCESS: "SPARK_POST_SUCCESS",
    POST_ERROR: "SPARK_POST_ERROR",
  },
  // Add Fuel (薪をくべる)
  ADD_FUEL: {
    START: "ADD_FUEL_START",
    SUCCESS: "ADD_FUEL_SUCCESS",
    ERROR: "ADD_FUEL_ERROR",
    HAPTIC_NOT_SUPPORTED: "ADD_FUEL_HAPTIC_NOT_SUPPORTED",
  },
} as const;

/**
 * Spark cooling threshold ratio
 * Sparks with less than this percentage of their total lifetime remaining
 * will display as "cooling" (ash)
 *
 * This value is derived from the BDD specification:
 * "システムの '冷却閾値' は 'Decay time' に対して '30%' の割合である"
 */
export const COOLING_THRESHOLD_RATIO = 0.3;

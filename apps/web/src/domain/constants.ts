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
} as const;

/**
 * Spark cooling threshold in milliseconds (3 minutes)
 * Sparks with less than this remaining lifetime will display as "cooling" (ash)
 */
export const COOLING_THRESHOLD_MS = 3 * 60 * 1000;

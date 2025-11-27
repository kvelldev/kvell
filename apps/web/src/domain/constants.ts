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
 *
 */
export type InternalStatusCodes = keyof typeof internalStatuses;

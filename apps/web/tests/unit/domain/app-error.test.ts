/**
 * AppError Domain Tests
 *
 * Unit tests for AppError class.
 */

import { describe, it, expect } from "vitest";
import AppError from "@/domain/appError";

describe("AppError", () => {
  it("should create an error with status code and default message", () => {
    const error = new AppError(404);

    expect(error).toBeInstanceOf(AppError);
    expect(error).toBeInstanceOf(Error);
    expect(error.status).toBe(404);
    expect(error.message).toBe("Not Found");
    expect(error.name).toBe("AppError");
  });

  it("should create an error with custom message", () => {
    const error = new AppError(500, "Custom error message");

    expect(error.status).toBe(500);
    expect(error.message).toBe("Custom error message");
  });

  it("should store the cause error when provided", () => {
    const cause = new Error("Original error");
    const error = new AppError(500, "Wrapped error", { cause });

    expect(error.cause).toBe(cause);
    expect(error.cause?.message).toBe("Original error");
  });

  it("should store context when provided", () => {
    const context = { userId: "123", action: "saveData" };
    const error = new AppError(500, "Error with context", { context });

    expect(error.context).toEqual(context);
  });

  it("should store both cause and context", () => {
    const cause = new Error("Original error");
    const context = { key: "value" };
    const error = new AppError(500, "Complex error", { cause, context });

    expect(error.cause).toBe(cause);
    expect(error.context).toEqual(context);
  });

  it("should handle all common HTTP status codes", () => {
    const statusCodes = [200, 201, 204, 400, 401, 403, 404, 409, 422, 500];

    for (const status of statusCodes) {
      const error = new AppError(status as never);
      expect(error.status).toBe(status);
      expect(error.message).toBeTruthy();
    }
  });

  it("should handle business logic error codes", () => {
    const error = new AppError(1001);

    expect(error.status).toBe(1001);
    expect(error.message).toBe("Invalid email format.");
  });
});

/**
 * API Client Adapter Tests
 *
 * Unit tests for apiClient utility.
 */

import { describe, it, expect, beforeEach, vi } from "vitest";
import { apiClient } from "./apiClient";
import AppError from "@/domain/appError";

// Mock fetch
globalThis.fetch = vi.fn();

describe("apiClient", () => {
  beforeEach(() => {
    vi.resetAllMocks();
  });

  it("should successfully fetch JSON data", async () => {
    const mockData = { id: "1", name: "Test" };
    (globalThis.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
      ok: true,
      status: 200,
      json: async () => mockData,
    });

    const result = await apiClient<typeof mockData>("/api/test");

    expect(result).toEqual(mockData);
    expect(globalThis.fetch).toHaveBeenCalledTimes(1);
    const callArgs = (globalThis.fetch as ReturnType<typeof vi.fn>).mock
      .calls[0];
    expect(callArgs[0]).toBe("http://localhost:8000/api/test");
    expect(callArgs[1].headers).toBeInstanceOf(Headers);
    expect(callArgs[1].headers.get("Content-Type")).toBe("application/json");
  });

  it("should handle POST requests with body", async () => {
    const mockData = { success: true };
    const requestBody = { message: "test" };

    (globalThis.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
      ok: true,
      status: 200,
      json: async () => mockData,
    });

    const result = await apiClient<typeof mockData>("/api/test", {
      method: "POST",
      body: JSON.stringify(requestBody),
    });

    expect(result).toEqual(mockData);
    expect(globalThis.fetch).toHaveBeenCalledWith(
      "http://localhost:8000/api/test",
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify(requestBody),
      }),
    );
  });

  it("should return null for 204 No Content", async () => {
    (globalThis.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
      ok: true,
      status: 204,
    });

    const result = await apiClient<null>("/api/test");

    expect(result).toBeNull();
  });

  it("should throw AppError on HTTP error status", async () => {
    (globalThis.fetch as ReturnType<typeof vi.fn>).mockResolvedValue({
      ok: false,
      status: 404,
      statusText: "Not Found",
    });

    try {
      await apiClient("/api/test");
      expect.fail("Should have thrown an error");
    } catch (error) {
      expect(error).toBeInstanceOf(AppError);
      expect((error as AppError).status).toBe(404);
      expect((error as AppError).message).toBe("API Error: Not Found");
    }
  });

  it("should throw AppError on network error", async () => {
    (globalThis.fetch as ReturnType<typeof vi.fn>).mockRejectedValueOnce(
      new Error("Network failure"),
    );

    await expect(apiClient("/api/test")).rejects.toThrow(AppError);
    await expect(apiClient("/api/test")).rejects.toMatchObject({
      status: 500,
      message: "Network Error",
    });
  });

  it("should preserve AppError if already thrown", async () => {
    const appError = new AppError(400, "Bad Request");
    (globalThis.fetch as ReturnType<typeof vi.fn>).mockRejectedValueOnce(appError);

    await expect(apiClient("/api/test")).rejects.toThrow(appError);
  });

  it("should merge custom headers", async () => {
    const mockData = { success: true };
    (globalThis.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
      ok: true,
      status: 200,
      json: async () => mockData,
    });

    await apiClient("/api/test", {
      headers: { Authorization: "Bearer token" },
    });

    expect(globalThis.fetch).toHaveBeenCalledTimes(1);
    const callArgs = (globalThis.fetch as ReturnType<typeof vi.fn>).mock
      .calls[0];
    expect(callArgs[0]).toBe("http://localhost:8000/api/test");
    expect(callArgs[1].headers).toBeInstanceOf(Headers);
    expect(callArgs[1].headers.get("Content-Type")).toBe("application/json");
    expect(callArgs[1].headers.get("Authorization")).toBe("Bearer token");
  });
});

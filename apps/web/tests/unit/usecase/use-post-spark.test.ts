/**
 * usePostSpark UseCase Unit Test
 *
 * Tests the business logic of posting a spark.
 * Mocks the repository layer to isolate the UseCase logic.
 */

import { renderHook, waitFor } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { usePostSpark } from "@/usecase/usePostSpark";
import type { ISparkRepository } from "@/domain/repository/sparkRepository";
import type { ILogger } from "@/usecase/ports/ILogger";
import type { Spark } from "@/domain/model/spark";
import { LOG_EVENTS } from "@/domain/constants";

describe("usePostSpark", () => {
  // Mock instances
  let mockRepository: ISparkRepository;
  let mockLogger: ILogger;

  beforeEach(() => {
    // Create fresh mocks before each test
    mockRepository = {
      postSpark: vi.fn(),
      addFuel: vi.fn(),
    };

    mockLogger = {
      info: vi.fn(),
      error: vi.fn(),
    };
  });

  it("should successfully post a spark and log events", async () => {
    // Arrange: Setup mock return value with dynamic timestamps
    const now = new Date();
    const visibleUntil = new Date(now.getTime() + 10 * 60 * 1000); // +10 minutes
    const mockSpark: Spark = {
      id: "spark-123",
      content: "Test spark content",
      createdAt: now.toISOString(),
      decayAt: visibleUntil.toISOString(),
    };
    vi.mocked(mockRepository.postSpark).mockResolvedValue(mockSpark);

    // Act: Render hook and trigger mutation
    const { result } = renderHook(() =>
      usePostSpark(mockRepository, mockLogger),
    );

    // Trigger post spark
    const postPromise = result.current.postSpark({
      content: "Test spark content",
    });

    // Wait for mutation to complete
    await waitFor(() => {
      expect(result.current.isPosting).toBe(false);
    });
    const postedSpark = await postPromise;

    // Assert: Verify repository was called correctly
    expect(mockRepository.postSpark).toHaveBeenCalledTimes(1);
    expect(mockRepository.postSpark).toHaveBeenCalledWith({
      content: "Test spark content",
    });

    // Assert: Verify logger was called with correct events
    expect(mockLogger.info).toHaveBeenCalledWith("Posting spark", {
      event: LOG_EVENTS.SPARK.POST_START,
      contentLength: 18,
    });
    expect(mockLogger.info).toHaveBeenCalledWith("Successfully posted spark", {
      event: LOG_EVENTS.SPARK.POST_SUCCESS,
      sparkId: "spark-123",
    });

    // Assert: Verify returned spark
    expect(postedSpark).toEqual(mockSpark);
    expect(result.current.error).toBeNull();
  });

  it("should handle posting error and log error event", async () => {
    // Arrange: Setup mock to throw error
    const mockError = new Error("Network error");
    vi.mocked(mockRepository.postSpark).mockRejectedValue(mockError);

    // Act: Render hook and trigger mutation
    const { result } = renderHook(() =>
      usePostSpark(mockRepository, mockLogger),
    );

    // Trigger post spark (expect it to fail)
    // Catch the error to prevent unhandled promise rejection
    const postPromise = result.current
      .postSpark({ content: "Test content" })
      .catch(() => {
        // Error is expected, do nothing
      });

    // Wait for promise to settle
    await postPromise;

    // Wait for mutation to complete and error state to be set
    await waitFor(() => {
      expect(result.current.isPosting).toBe(false);
      expect(result.current.error).toBeTruthy();
    });

    // Assert: Verify error logger was called
    expect(mockLogger.error).toHaveBeenCalledWith(mockError, {
      event: LOG_EVENTS.SPARK.POST_ERROR,
      context: "usePostSpark",
      contentLength: 12,
    });

    // Assert: Verify error state
    expect(result.current.error).toBeTruthy();
  });

  it("should track isPosting state during mutation", async () => {
    // Arrange: Setup mock with delay and dynamic timestamps
    const now = new Date();
    const visibleUntil = new Date(now.getTime() + 10 * 60 * 1000); // +10 minutes
    const mockSpark: Spark = {
      id: "spark-456",
      content: "Test content",
      createdAt: now.toISOString(),
      decayAt: visibleUntil.toISOString(),
    };
    vi.mocked(mockRepository.postSpark).mockImplementation(
      () =>
        new Promise((resolve) => {
          setTimeout(() => {
            resolve(mockSpark);
          }, 100);
        }),
    );

    // Act: Render hook and trigger mutation
    const { result } = renderHook(() =>
      usePostSpark(mockRepository, mockLogger),
    );

    // Initial state
    expect(result.current.isPosting).toBe(false);

    // Trigger post
    const postPromise = result.current.postSpark({ content: "Test content" });

    // Should be posting immediately after trigger
    await waitFor(() => {
      expect(result.current.isPosting).toBe(true);
    });

    // Wait for completion
    await postPromise;

    // Should not be posting after completion
    await waitFor(() => {
      expect(result.current.isPosting).toBe(false);
    });
  });
});

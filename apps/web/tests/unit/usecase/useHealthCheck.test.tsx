/**
 * Health Check UseCase Tests
 *
 * Unit tests for useHealthCheck hooks.
 * Tests business logic layer with mocked repository.
 */

import { describe, it, expect, beforeEach, vi } from "vitest";
import { renderHook, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";
import { SWRConfig } from "swr";
import {
  useFetchLatestHealthMessage,
  useSaveHealthMessage,
} from "@/usecase/useHealthCheck";
import type { IHealthRepository } from "@/domain/repository/healthRepository";
import type { HealthMessage } from "@/domain/model/health";
import type { ILogger } from "@/usecase/ports/ILogger";
import { LOG_EVENTS } from "@/domain/constants";

// Mock logger
const mockLogger: ILogger = {
  info: vi.fn(),
  error: vi.fn(),
};

// Mock repository
const mockRepository: IHealthRepository = {
  getLatest: vi.fn(),
  saveMessage: vi.fn(),
};

// Wrapper component for hooks (SWR only - no LoggerProvider needed)
const createWrapper = () => {
  return ({ children }: { children: ReactNode }) => (
    <SWRConfig value={{ provider: () => new Map() }}>{children}</SWRConfig>
  );
};

describe("useFetchLatestHealthMessage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("should fetch and return latest health message", async () => {
    const mockMessage: HealthMessage = {
      id: "123",
      message: "Test message",
      createdAt: "2024-01-01T00:00:00Z",
    };

    vi.mocked(mockRepository.getLatest).mockResolvedValueOnce(mockMessage);

    const { result } = renderHook(
      () => useFetchLatestHealthMessage(mockRepository, mockLogger),
      {
        wrapper: createWrapper(),
      },
    );

    // Initially loading
    expect(result.current.isLoading).toBe(true);
    expect(result.current.message).toBeNull();

    // Wait for data to load
    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.message).toEqual(mockMessage);
    expect(result.current.isError).toBe(false);
    expect(mockRepository.getLatest).toHaveBeenCalledOnce();
    expect(mockLogger.info).toHaveBeenCalledWith(expect.any(String), {
      event: LOG_EVENTS.HEALTH_CHECK.FETCH_START,
    });
    expect(mockLogger.info).toHaveBeenCalledWith(expect.any(String), {
      event: LOG_EVENTS.HEALTH_CHECK.FETCH_SUCCESS,
      hasData: true,
    });
  });

  it("should return null when no message exists", async () => {
    vi.mocked(mockRepository.getLatest).mockResolvedValueOnce(null);

    const { result } = renderHook(
      () => useFetchLatestHealthMessage(mockRepository, mockLogger),
      {
        wrapper: createWrapper(),
      },
    );

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.message).toBeNull();
    expect(result.current.isError).toBe(false);
  });

  it("should handle fetch error", async () => {
    const error = new Error("Network error");
    vi.mocked(mockRepository.getLatest).mockRejectedValueOnce(error);

    const { result } = renderHook(
      () => useFetchLatestHealthMessage(mockRepository, mockLogger),
      {
        wrapper: createWrapper(),
      },
    );

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.isError).toBe(true);
    expect(result.current.error).toEqual(error);
    expect(mockLogger.error).toHaveBeenCalledWith(
      error,
      expect.objectContaining({
        event: LOG_EVENTS.HEALTH_CHECK.FETCH_ERROR,
      }),
    );
  });
});

describe("useSaveHealthMessage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("should save message successfully", async () => {
    const inputMessage = "New test message";
    const savedMessage: HealthMessage = {
      id: "456",
      message: inputMessage,
      createdAt: "2024-01-01T00:00:00Z",
    };

    vi.mocked(mockRepository.saveMessage).mockResolvedValueOnce(savedMessage);

    const { result } = renderHook(
      () => useSaveHealthMessage(mockRepository, mockLogger),
      {
        wrapper: createWrapper(),
      },
    );

    expect(result.current.isSaving).toBe(false);

    // Trigger save
    await result.current.saveMessage(inputMessage);

    await waitFor(() => {
      expect(result.current.isSaving).toBe(false);
    });

    expect(mockRepository.saveMessage).toHaveBeenCalledWith(inputMessage);
    expect(mockLogger.info).toHaveBeenCalledWith(expect.any(String), {
      event: LOG_EVENTS.HEALTH_CHECK.SAVE_START,
      message: inputMessage,
    });
    expect(mockLogger.info).toHaveBeenCalledWith(expect.any(String), {
      event: LOG_EVENTS.HEALTH_CHECK.SAVE_SUCCESS,
      id: savedMessage.id,
    });
  });

  it("should handle save error", async () => {
    const inputMessage = "Test message";
    const error = new Error("Save failed");
    vi.mocked(mockRepository.saveMessage).mockRejectedValueOnce(error);

    const { result } = renderHook(
      () => useSaveHealthMessage(mockRepository, mockLogger),
      {
        wrapper: createWrapper(),
      },
    );

    await expect(result.current.saveMessage(inputMessage)).rejects.toThrow(
      "Save failed",
    );

    await waitFor(() => {
      expect(result.current.error).toEqual(error);
    });

    expect(mockLogger.error).toHaveBeenCalledWith(
      error,
      expect.objectContaining({
        event: LOG_EVENTS.HEALTH_CHECK.SAVE_ERROR,
      }),
    );
  });
});

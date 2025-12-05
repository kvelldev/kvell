/**
 * HealthCheckPage Tests
 *
 * Unit tests for HealthCheckPage component (Smart Component).
 * Tests logic wiring with mocked UseCases.
 */

import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { HealthCheckPage } from "@/components/pages/HealthCheckPage";
import * as useHealthCheckHooks from "@/usecase/useHealthCheck";
import type { HealthMessage } from "@/domain/model/health";

// Mock useLogger hook
vi.mock("@/components/useLogger", () => ({
  useLogger: vi.fn(() => ({
    info: vi.fn(),
    error: vi.fn(),
  })),
}));

// Mock repository
vi.mock("@/adapter/repository/healthRepository", () => ({
  healthRepository: {
    getLatest: vi.fn(),
    saveMessage: vi.fn(),
  },
}));

describe("HealthCheckPage", () => {
  const mockFetchHook = {
    message: null,
    isLoading: false,
    isError: false,
    error: undefined,
    refetch: vi.fn(),
  };

  const mockSaveHook = {
    saveMessage: vi.fn(),
    isSaving: false,
    error: null,
  };

  beforeEach(() => {
    vi.clearAllMocks();
    vi.spyOn(
      useHealthCheckHooks,
      "useFetchLatestHealthMessage",
    ).mockReturnValue(mockFetchHook);
    vi.spyOn(useHealthCheckHooks, "useSaveHealthMessage").mockReturnValue(
      mockSaveHook,
    );
  });

  it("should render HealthCheckMonitor with initial state", () => {
    render(<HealthCheckPage />);

    expect(screen.getByText("System Health Check")).toBeInTheDocument();
    expect(
      screen.getByPlaceholderText("Enter a test message..."),
    ).toBeInTheDocument();
  });

  it("should handle input changes", () => {
    render(<HealthCheckPage />);

    const input = screen.getByPlaceholderText("Enter a test message...");
    fireEvent.change(input, { target: { value: "test message" } });

    expect(input).toHaveValue("test message");
  });

  it("should call saveMessage and clear input on save", async () => {
    const mockMessage: HealthMessage = {
      id: "123",
      message: "test message",
      createdAt: "2024-01-01T00:00:00Z",
    };
    const mockSave = vi.fn().mockResolvedValue(mockMessage);
    vi.spyOn(useHealthCheckHooks, "useSaveHealthMessage").mockReturnValue({
      ...mockSaveHook,
      saveMessage: mockSave,
    });

    render(<HealthCheckPage />);

    const input = screen.getByPlaceholderText("Enter a test message...");
    fireEvent.change(input, { target: { value: "test message" } });

    const saveButton = screen.getByText("Save to DB");
    fireEvent.click(saveButton);

    await waitFor(() => {
      expect(mockSave).toHaveBeenCalledWith("test message");
    });

    // Input should be cleared after save
    expect(input).toHaveValue("");
  });

  it("should not save when input is empty", () => {
    const mockSave = vi.fn();
    vi.spyOn(useHealthCheckHooks, "useSaveHealthMessage").mockReturnValue({
      ...mockSaveHook,
      saveMessage: mockSave,
    });

    render(<HealthCheckPage />);

    const saveButton = screen.getByText("Save to DB");
    expect(saveButton).toBeDisabled();
  });

  it("should not save when input is only whitespace", () => {
    const mockSave = vi.fn();
    vi.spyOn(useHealthCheckHooks, "useSaveHealthMessage").mockReturnValue({
      ...mockSaveHook,
      saveMessage: mockSave,
    });

    render(<HealthCheckPage />);

    const input = screen.getByPlaceholderText("Enter a test message...");
    fireEvent.change(input, { target: { value: "   " } });

    const saveButton = screen.getByText("Save to DB");
    fireEvent.click(saveButton);

    // Should not call save for whitespace-only input
    expect(mockSave).not.toHaveBeenCalled();
  });

  it("should call refetch when fetch button is clicked", () => {
    const mockRefetch = vi.fn();
    vi.spyOn(
      useHealthCheckHooks,
      "useFetchLatestHealthMessage",
    ).mockReturnValue({
      ...mockFetchHook,
      refetch: mockRefetch,
    });

    render(<HealthCheckPage />);

    const fetchButton = screen.getByText("Fetch Latest");
    fireEvent.click(fetchButton);

    expect(mockRefetch).toHaveBeenCalledOnce();
  });

  it("should show loading state when fetching", () => {
    vi.spyOn(
      useHealthCheckHooks,
      "useFetchLatestHealthMessage",
    ).mockReturnValue({
      ...mockFetchHook,
      isLoading: true,
    });

    render(<HealthCheckPage />);

    expect(screen.getByText("Loading...")).toBeInTheDocument();
  });

  it("should show loading state when saving", () => {
    vi.spyOn(useHealthCheckHooks, "useSaveHealthMessage").mockReturnValue({
      ...mockSaveHook,
      isSaving: true,
    });

    render(<HealthCheckPage />);

    expect(screen.getByText("Loading...")).toBeInTheDocument();
  });

  it("should display error from fetch hook", () => {
    const error = new Error("Fetch failed");
    vi.spyOn(
      useHealthCheckHooks,
      "useFetchLatestHealthMessage",
    ).mockReturnValue({
      ...mockFetchHook,
      error,
    });

    render(<HealthCheckPage />);

    expect(screen.getByText("Error")).toBeInTheDocument();
    expect(screen.getByText("Fetch failed")).toBeInTheDocument();
  });

  it("should display error from save hook", () => {
    const error = new Error("Save failed");
    vi.spyOn(useHealthCheckHooks, "useSaveHealthMessage").mockReturnValue({
      ...mockSaveHook,
      error,
    });

    render(<HealthCheckPage />);

    expect(screen.getByText("Error")).toBeInTheDocument();
    expect(screen.getByText("Save failed")).toBeInTheDocument();
  });

  it("should display message when available", () => {
    const message: HealthMessage = {
      id: "123",
      message: "Health check success response",
      createdAt: "2024-01-01T00:00:00Z",
    };

    vi.spyOn(
      useHealthCheckHooks,
      "useFetchLatestHealthMessage",
    ).mockReturnValue({
      ...mockFetchHook,
      message,
    });

    render(<HealthCheckPage />);

    expect(screen.getByText("Success")).toBeInTheDocument();
    expect(
      screen.getByText(/Health check success response/),
    ).toBeInTheDocument();
    expect(screen.getByText(/ID: 123/)).toBeInTheDocument();
  });
});

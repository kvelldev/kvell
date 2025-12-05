/**
 * SparkPostPage (Smart Component) Unit Test
 *
 * Tests the wiring logic of the page component.
 * Mocks UseCase hooks to isolate the Page's responsibility.
 */

import { render, screen, waitFor } from "@testing-library/react";
import { userEvent } from "@testing-library/user-event";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { BrowserRouter } from "react-router-dom";
import { SparkPostPage } from "@/components/pages/SparkPostPage";
import * as usePostSparkModule from "@/usecase/usePostSpark";
import * as useLoggerModule from "@/components/useLogger";
import type { ILogger } from "@/usecase/ports/ILogger";

// Mock modules
vi.mock("@/usecase/usePostSpark");
vi.mock("@/components/useLogger");

describe("SparkPostPage", () => {
  let mockLogger: ILogger;

  beforeEach(() => {
    // Setup mock logger
    mockLogger = {
      info: vi.fn(),
      error: vi.fn(),
    };
    vi.mocked(useLoggerModule.useLogger).mockReturnValue(mockLogger);
  });

  it("should render the form correctly", () => {
    // Mock usePostSpark to return initial state
    vi.mocked(usePostSparkModule.usePostSpark).mockReturnValue({
      postSpark: vi.fn(),
      isPosting: false,
      error: null,
    });

    render(
      <BrowserRouter>
        <SparkPostPage />
      </BrowserRouter>,
    );

    // Verify form elements are rendered
    expect(
      screen.getByRole("heading", { name: "種火を投げる" }),
    ).toBeInTheDocument();
    expect(screen.getByTestId("spark-input")).toBeInTheDocument();
    expect(screen.getByTestId("spark-submit-button")).toBeInTheDocument();
  });

  it("should pass isPosting state to form when posting", () => {
    // Mock usePostSpark to return posting state
    vi.mocked(usePostSparkModule.usePostSpark).mockReturnValue({
      postSpark: vi.fn(),
      isPosting: true,
      error: null,
    });

    render(
      <BrowserRouter>
        <SparkPostPage />
      </BrowserRouter>,
    );

    // Submit button should be disabled and show posting text
    expect(screen.getByTestId("spark-submit-button")).toBeDisabled();
    expect(screen.getByTestId("spark-submit-button")).toHaveTextContent(
      "投稿中...",
    );
  });

  it("should pass error state to form when error occurs", () => {
    const testError = new Error("Test error");
    // Mock usePostSpark to return error state
    vi.mocked(usePostSparkModule.usePostSpark).mockReturnValue({
      postSpark: vi.fn(),
      isPosting: false,
      error: testError,
    });

    render(
      <BrowserRouter>
        <SparkPostPage />
      </BrowserRouter>,
    );

    // Error should be displayed
    expect(screen.getByTestId("spark-error")).toBeInTheDocument();
    expect(screen.getByTestId("spark-error")).toHaveTextContent(
      "エラー: Test error",
    );
  });

  it("should call postSpark and clear input on successful submit", async () => {
    const user = userEvent.setup();
    const mockPostSpark = vi.fn().mockResolvedValue({
      id: "spark-123",
      content: "Test content",
      createdAt: "2025-12-05T00:00:00Z",
    });

    // Mock usePostSpark
    vi.mocked(usePostSparkModule.usePostSpark).mockReturnValue({
      postSpark: mockPostSpark,
      isPosting: false,
      error: null,
    });

    render(
      <BrowserRouter>
        <SparkPostPage />
      </BrowserRouter>,
    );

    // Type content
    const textarea = screen.getByTestId("spark-input");
    await user.type(textarea, "Test spark content");

    // Click submit
    const submitButton = screen.getByTestId("spark-submit-button");
    await user.click(submitButton);

    // Wait for async operation
    await waitFor(() => {
      expect(mockPostSpark).toHaveBeenCalledTimes(1);
    });

    // Verify postSpark was called with correct content
    expect(mockPostSpark).toHaveBeenCalledWith({
      content: "Test spark content",
    });

    // Input should be cleared after successful submit
    await waitFor(() => {
      expect(textarea).toHaveValue("");
    });
  });

  it("should not clear input when submit fails", async () => {
    const user = userEvent.setup();
    const mockPostSpark = vi.fn().mockRejectedValue(new Error("Network error"));

    // Mock usePostSpark with error
    vi.mocked(usePostSparkModule.usePostSpark).mockReturnValue({
      postSpark: mockPostSpark,
      isPosting: false,
      error: new Error("Network error"),
    });

    render(
      <BrowserRouter>
        <SparkPostPage />
      </BrowserRouter>,
    );

    // Type content
    const textarea = screen.getByTestId("spark-input");
    await user.type(textarea, "Test content");

    // Click submit
    const submitButton = screen.getByTestId("spark-submit-button");
    await user.click(submitButton);

    // Wait for async operation
    await waitFor(() => {
      expect(mockPostSpark).toHaveBeenCalled();
    });

    // Input should NOT be cleared on failure
    expect(textarea).toHaveValue("Test content");
  });

  it("should not submit when content is empty", () => {
    const mockPostSpark = vi.fn();

    vi.mocked(usePostSparkModule.usePostSpark).mockReturnValue({
      postSpark: mockPostSpark,
      isPosting: false,
      error: null,
    });

    render(
      <BrowserRouter>
        <SparkPostPage />
      </BrowserRouter>,
    );

    // Submit button should be disabled when empty
    const submitButton = screen.getByTestId("spark-submit-button");
    expect(submitButton).toBeDisabled();

    // Verify postSpark is never called
    expect(mockPostSpark).not.toHaveBeenCalled();
  });

  it("should trim whitespace before submitting", async () => {
    const user = userEvent.setup();
    const mockPostSpark = vi.fn().mockResolvedValue({
      id: "spark-123",
      content: "Test content",
      createdAt: "2025-12-05T00:00:00Z",
    });

    vi.mocked(usePostSparkModule.usePostSpark).mockReturnValue({
      postSpark: mockPostSpark,
      isPosting: false,
      error: null,
    });

    render(
      <BrowserRouter>
        <SparkPostPage />
      </BrowserRouter>,
    );

    // Type content with leading/trailing whitespace
    const textarea = screen.getByTestId("spark-input");
    await user.type(textarea, "  Test content  ");

    // Click submit
    const submitButton = screen.getByTestId("spark-submit-button");
    await user.click(submitButton);

    await waitFor(() => {
      expect(mockPostSpark).toHaveBeenCalledWith({
        content: "Test content", // Should be trimmed
      });
    });
  });
});

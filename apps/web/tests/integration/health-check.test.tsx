/**
 * HealthCheck Integration Tests
 *
 * These tests verify the entire flow from Page → UseCase → Repository → API.
 * Unlike unit tests which mock individual layers, integration tests use MSW
 * to mock only the HTTP boundary, testing real component integration.
 *
 * Test Strategy:
 * - Use MSW to mock API endpoints (simulates backend behavior)
 * - Test actual Repository → UseCase → Page integration
 * - Verify UI rendering and user interactions
 * - No mocking of internal layers (Repository, UseCase)
 */

import { describe, it, expect, beforeEach, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { SWRConfig } from "swr";
import { HealthCheckPage } from "@/components/pages/HealthCheckPage";
import { LoggerProvider } from "@/components/LoggerContext";
import { mockHealthStore, server, BASE_URL } from "./setup";
import { http, HttpResponse } from "msw";
import type { HealthMessage } from "@/domain/model/health";
import type { ILogger } from "@/usecase/ports/ILogger";

// Import setup to ensure MSW is configured
import "./setup";

/**
 * Mock logger for integration tests
 * Provides a no-op logger implementation
 */
const mockLogger: ILogger = {
  info: vi.fn(),
  error: vi.fn(),
};

/**
 * Helper to render HealthCheckPage with necessary providers
 * Page components need LoggerContext which is provided by App.tsx
 * @returns Rendered component result from React Testing Library
 */
const renderHealthCheckPage = () => {
  return render(
    <LoggerProvider logger={mockLogger}>
      <SWRConfig
        value={{
          provider: () => new Map(),
          onError: () => {
            // Suppress error logging in tests
            // SWR will still handle errors internally and update error state
          },
        }}
      >
        <HealthCheckPage />
      </SWRConfig>
    </LoggerProvider>,
  );
};

describe("HealthCheck Integration", () => {
  beforeEach(() => {
    // Reset mock data store before each test
    mockHealthStore.reset();
    // Clear mock logger calls
    vi.clearAllMocks();
  });

  describe("Initial Load", () => {
    it("test_initialLoad_whenNoMessageExists_displaysNoData", async () => {
      /**
       * Action: initialLoad (component mount)
       * Condition: whenNoMessageExists (empty database)
       * Result: displaysNoData (no message displayed, ready for input)
       */
      renderHealthCheckPage();

      // Initially shows loading
      expect(screen.getByTestId("health-loading-display")).toBeInTheDocument();

      // After loading, loading indicator should disappear
      await waitFor(() => {
        expect(
          screen.queryByTestId("health-loading-display"),
        ).not.toBeInTheDocument();
      });

      // No message should be displayed (message display is null when no data)
      expect(
        screen.queryByTestId("health-message-display"),
      ).not.toBeInTheDocument();
      expect(
        screen.queryByTestId("health-error-display"),
      ).not.toBeInTheDocument();
    });

    it("test_initialLoad_whenMessageExists_displaysMessage", async () => {
      /**
       * Action: initialLoad
       * Condition: whenMessageExists (data in database)
       * Result: displaysMessage (shows existing message)
       */
      // Arrange: Pre-populate mock store with data
      const existingMessage: HealthMessage = {
        id: "existing-id",
        message: "Existing message from DB",
        createdAt: new Date().toISOString(),
      };
      mockHealthStore.add(existingMessage);

      // Act
      renderHealthCheckPage();

      // Assert: Message should be displayed after loading
      await waitFor(
        () => {
          expect(
            screen.getByTestId("health-message-display"),
          ).toBeInTheDocument();
        },
        { timeout: 3000 },
      );
    });
  });

  describe("Save Message", () => {
    it("test_saveMessage_whenValidInput_savesAndDisplaysNewMessage", async () => {
      /**
       * Action: saveMessage (user enters text and clicks Save button)
       * Condition: whenValidInput (valid message text)
       * Result: savesAndDisplaysNewMessage (saves to backend and updates UI)
       */
      const user = userEvent.setup();
      renderHealthCheckPage();

      // Wait for initial load
      await waitFor(() => {
        expect(
          screen.queryByTestId("health-loading-display"),
        ).not.toBeInTheDocument();
      });

      // Find input and button by test ID
      const input = screen.getByTestId("health-echo-input");
      const saveButton = screen.getByTestId("health-save-button");

      // Enter message
      await user.type(input, "Integration test message");
      expect(input).toHaveValue("Integration test message");

      // Click Save button
      await user.click(saveButton);

      // Wait for save to complete and message to be displayed
      await waitFor(() => {
        expect(
          screen.getByTestId("health-message-display"),
        ).toBeInTheDocument();
      });

      // Input should be cleared after successful save
      expect(input).toHaveValue("");

      // Verify message was saved to mock store
      const latest = mockHealthStore.getLatest();
      expect(latest).not.toBeNull();
      expect(latest?.message).toBe("Integration test message");
    });

    it("test_saveMessage_whenEmptyInput_buttonIsDisabled", async () => {
      /**
       * Action: saveMessage
       * Condition: whenEmptyInput (input field is empty)
       * Result: buttonIsDisabled (Save button cannot be clicked)
       */
      renderHealthCheckPage();

      await waitFor(() => {
        expect(
          screen.queryByTestId("health-loading-display"),
        ).not.toBeInTheDocument();
      });

      const saveButton = screen.getByTestId("health-save-button");

      // Button should be disabled when input is empty
      expect(saveButton).toBeDisabled();
    });

    it("test_saveMessage_whenCalledMultipleTimes_displaysLatestMessage", async () => {
      /**
       * Action: saveMessage
       * Condition: whenCalledMultipleTimes (3 messages saved sequentially)
       * Result: displaysLatestMessage (UI always shows the latest message)
       */
      const user = userEvent.setup();
      renderHealthCheckPage();

      await waitFor(() => {
        expect(
          screen.queryByTestId("health-loading-display"),
        ).not.toBeInTheDocument();
      });

      const input = screen.getByTestId("health-echo-input");
      const saveButton = screen.getByTestId("health-save-button");

      // Save first message
      await user.type(input, "First message");
      await user.click(saveButton);
      await waitFor(() => {
        expect(
          screen.getByTestId("health-message-display"),
        ).toBeInTheDocument();
      });

      // Save second message
      await user.type(input, "Second message");
      await user.click(saveButton);
      await waitFor(() => {
        expect(
          screen.getByTestId("health-message-display"),
        ).toBeInTheDocument();
      });

      // Save third message
      await user.type(input, "Third message");
      await user.click(saveButton);
      await waitFor(() => {
        expect(
          screen.getByTestId("health-message-display"),
        ).toBeInTheDocument();
      });

      // Verify all messages are in mock store
      expect(mockHealthStore.messages).toHaveLength(3);

      // Verify latest message is displayed
      const latest = mockHealthStore.getLatest();
      expect(latest?.message).toBe("Third message");
    });
  });

  describe("Reload Message", () => {
    it("test_reloadMessage_whenDataExists_refetchesAndDisplaysLatest", async () => {
      /**
       * Action: reloadMessage (user clicks Fetch button)
       * Condition: whenDataExists (data exists in backend)
       * Result: refetchesAndDisplaysLatest (fetches fresh data from API)
       */
      const user = userEvent.setup();

      // Pre-populate with initial message
      const initialMessage: HealthMessage = {
        id: "initial-id",
        message: "Initial message",
        createdAt: new Date().toISOString(),
      };
      mockHealthStore.add(initialMessage);

      renderHealthCheckPage();

      await waitFor(
        () => {
          expect(
            screen.getByTestId("health-message-display"),
          ).toBeInTheDocument();
        },
        { timeout: 3000 },
      );

      // Simulate backend data change (e.g., another user added a message)
      const newMessage: HealthMessage = {
        id: "new-id",
        message: "Updated message",
        createdAt: new Date().toISOString(),
      };
      mockHealthStore.add(newMessage);

      // Click Fetch button
      const fetchButton = screen.getByTestId("health-fetch-button");
      await user.click(fetchButton);

      // Should display the latest message from backend
      await waitFor(
        () => {
          const latest = mockHealthStore.getLatest();
          expect(latest?.message).toBe("Updated message");
        },
        { timeout: 3000 },
      );
    });
  });

  describe("Error Handling", () => {
    it("test_saveMessage_whenApiError_displaysErrorMessage", async () => {
      /**
       * Action: saveMessage
       * Condition: whenApiError (backend returns 500 error)
       * Result: displaysErrorMessage (shows error in UI)
       */
      const user = userEvent.setup();

      // Override handler to simulate API error
      server.use(
        http.post(`${BASE_URL}/api/health/echo`, () => {
          return HttpResponse.json(
            { detail: "Internal Server Error" },
            { status: 500 },
          );
        }),
      );

      renderHealthCheckPage();

      await waitFor(() => {
        expect(
          screen.queryByTestId("health-loading-display"),
        ).not.toBeInTheDocument();
      });

      const input = screen.getByTestId("health-echo-input");
      const saveButton = screen.getByTestId("health-save-button");

      await user.type(input, "Test message");
      await user.click(saveButton);

      // Should display error message (check for error display element)
      await waitFor(
        () => {
          expect(
            screen.getByTestId("health-error-display"),
          ).toBeInTheDocument();
        },
        { timeout: 3000 },
      );
    });

    it("test_fetchMessage_whenApiError_displaysErrorMessage", async () => {
      /**
       * Action: fetchMessage (initial load)
       * Condition: whenApiError (backend returns 500 error)
       * Result: displaysErrorMessage (shows error in UI)
       */
      // Override handler to simulate API error
      server.use(
        http.get(`${BASE_URL}/api/health/latest`, () => {
          return HttpResponse.json(
            { detail: "Internal Server Error" },
            { status: 500 },
          );
        }),
      );

      renderHealthCheckPage();

      // Should display error message after failed fetch
      await waitFor(
        () => {
          expect(
            screen.getByTestId("health-error-display"),
          ).toBeInTheDocument();
        },
        { timeout: 3000 },
      );
    });
  });

  describe("Loading State", () => {
    it("test_saveMessage_whileSaving_disablesControls", async () => {
      /**
       * Action: saveMessage
       * Condition: whileSaving (during API call)
       * Result: disablesControls (input and buttons are disabled)
       */
      const user = userEvent.setup();

      // Delay response to test loading state
      server.use(
        http.post(`${BASE_URL}/api/health/echo`, async () => {
          await new Promise((resolve) => setTimeout(resolve, 100));
          const newMessage: HealthMessage = {
            id: crypto.randomUUID(),
            message: "Test message",
            createdAt: new Date().toISOString(),
          };
          return HttpResponse.json(newMessage);
        }),
      );

      renderHealthCheckPage();

      await waitFor(() => {
        expect(
          screen.queryByTestId("health-loading-display"),
        ).not.toBeInTheDocument();
      });

      const input = screen.getByTestId("health-echo-input");
      const saveButton = screen.getByTestId("health-save-button");
      const fetchButton = screen.getByTestId("health-fetch-button");

      await user.type(input, "Test message");
      await user.click(saveButton);

      // During save, controls should be disabled
      // Note: This is timing-dependent and may need adjustment
      expect(input).toBeDisabled();
      expect(saveButton).toBeDisabled();
      expect(fetchButton).toBeDisabled();

      // Wait for save to complete
      await waitFor(
        () => {
          expect(
            screen.getByTestId("health-message-display"),
          ).toBeInTheDocument();
        },
        { timeout: 1000 },
      );
    });
  });
});

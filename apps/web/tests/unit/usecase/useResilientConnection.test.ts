import { renderHook, act } from "@testing-library/react";
import { vi, describe, it, expect, beforeEach, afterEach } from "vitest";
import { useResilientConnection } from "@/usecase/useResilientConnection";
import type { ITimelineRepository } from "@/domain/repository/timelineRepository";
import { ReadyState } from "react-use-websocket";

// Mock react-use-websocket
const mockUseWebSocket = vi.fn();
vi.mock("react-use-websocket", async (importOriginal) => {
  const actual = await importOriginal<typeof import("react-use-websocket")>();
  return {
    ...actual,
    __esModule: true,
    default: (...args: any[]) => mockUseWebSocket(...args),
  };
});

describe("useResilientConnection", () => {
  let repository: ITimelineRepository;
  let onMessageMock: ReturnType<typeof vi.fn>;
  let parseMessageMock: ReturnType<typeof vi.fn>;

  // Helper to simulate hook return values
  const setMockState = (
    readyState: ReadyState,
    lastMessage: MessageEvent | null = null,
  ) => {
    mockUseWebSocket.mockReturnValue({
      lastMessage,
      readyState,
    });
  };

  beforeEach(() => {
    vi.useFakeTimers();
    onMessageMock = vi.fn();
    parseMessageMock = vi.fn();

    repository = {
      connectionUrl: "ws://test.com",
      parseMessage: parseMessageMock,
    } as unknown as ITimelineRepository;

    // Default mock: connecting
    setMockState(ReadyState.CONNECTING);
  });

  afterEach(() => {
    vi.clearAllTimers();
    vi.restoreAllMocks();
  });

  it("should initially be disconnected (during initial connecting phase)", () => {
    setMockState(ReadyState.CONNECTING);

    // First render with CONNECTING (retryCount=0)
    const { result } = renderHook(() =>
      useResilientConnection(repository, onMessageMock),
    );

    expect(result.current.type).toBe("disconnected");
  });

  it("should be connected when readyState is OPEN", () => {
    setMockState(ReadyState.OPEN);

    const { result } = renderHook(() =>
      useResilientConnection(repository, onMessageMock),
    );

    expect(result.current.type).toBe("connected");
  });

  it("should handle incoming messages", () => {
    setMockState(ReadyState.OPEN, { data: "test-message" } as MessageEvent);
    parseMessageMock.mockReturnValue({ type: "mapped-event" });

    renderHook(() => useResilientConnection(repository, onMessageMock));

    expect(repository.parseMessage).toHaveBeenCalledWith("test-message");
    expect(onMessageMock).toHaveBeenCalledWith({ type: "mapped-event" });
  });

  it("should show reconnecting status with attempt count", () => {
    // 1. Start connected
    setMockState(ReadyState.OPEN);
    const { result, rerender } = renderHook(() =>
      useResilientConnection(repository, onMessageMock),
    );
    expect(result.current.type).toBe("connected");

    // Capture the onClose callback passed to useWebSocket
    const options =
      mockUseWebSocket.mock.calls[mockUseWebSocket.mock.calls.length - 1][1];

    // 2. Simulate connection close (trigger onClose)
    act(() => {
      options.onClose();
    });

    // 3. Change state to CONNECTING (reconnecting)
    setMockState(ReadyState.CONNECTING);
    rerender();

    expect(result.current.type).toBe("reconnecting");
    if (result.current.type === "reconnecting") {
      expect(result.current.attempt).toBe(1);
    }

    // 4. Simulate fail again
    act(() => {
      // Library would call duplicate onClose or similar depending on flow,
      // but here we just simulate the retry loop logic manually triggering onClose
      // In reality, useWebSocket triggers reconnectInterval then tries to connect.
      // If it fails, onClose is called again.
      options.onClose();
    });

    setMockState(ReadyState.CONNECTING);
    rerender();

    if (result.current.type === "reconnecting") {
      expect(result.current.attempt).toBe(2);
    }
  });

  it("should error after max retries", () => {
    setMockState(ReadyState.OPEN);
    const { result, rerender } = renderHook(() =>
      useResilientConnection(repository, onMessageMock),
    );

    const getLastOptions = () =>
      mockUseWebSocket.mock.calls[mockUseWebSocket.mock.calls.length - 1][1];

    // Fail 3 times
    act(() => {
      getLastOptions().onClose();
    }); // count -> 1
    act(() => {
      getLastOptions().onClose();
    }); // count -> 2
    act(() => {
      getLastOptions().onClose();
    }); // count -> 3

    setMockState(ReadyState.CLOSED);
    rerender();

    // With count=3 (MAX_RETRIES), and state CLOSED/CLOSING
    expect(result.current.type).toBe("error");
  });

  it("should reset retry count on successful open", () => {
    setMockState(ReadyState.OPEN);
    const { result, rerender } = renderHook(() =>
      useResilientConnection(repository, onMessageMock),
    );

    const getLastOptions = () =>
      mockUseWebSocket.mock.calls[mockUseWebSocket.mock.calls.length - 1][1];

    // Fail once
    act(() => {
      getLastOptions().onClose();
    });
    setMockState(ReadyState.CONNECTING);
    rerender();

    if (result.current.type === "reconnecting") {
      expect(result.current.attempt).toBe(1);
    }

    // Connect successfully
    act(() => {
      getLastOptions().onOpen();
    });
    setMockState(ReadyState.OPEN);
    rerender();

    expect(result.current.type).toBe("connected");

    // Fail again
    act(() => {
      getLastOptions().onClose();
    });
    setMockState(ReadyState.CONNECTING);
    rerender();

    // Should be attempt 1 again
    if (result.current.type === "reconnecting") {
      expect(result.current.attempt).toBe(1);
    }
  });
});

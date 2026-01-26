import { vi, describe, it, expect, beforeEach, afterEach } from "vitest";

describe("debug timers", () => {
  beforeEach(() => {
    vi.useFakeTimers();
    vi.setSystemTime(new Date(2024, 0, 1));
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it("should advance Date.now() when timers are advanced", () => {
    const start = Date.now();
    expect(start).toBe(new Date(2024, 0, 1).getTime());

    vi.advanceTimersByTime(2000);

    const end = Date.now();
    expect(end - start).toBe(2000);
  });
});

import { renderHook, act } from "@testing-library/react";
import { vi, describe, it, expect, beforeEach, afterEach } from "vitest";
import { useSparkBatcher } from "@/usecase/useSparkBatcher";
import type { TimelineEvent } from "@/domain/model/timelineEvent";
import type { Spark } from "@/domain/model/spark";

describe("useSparkBatcher", () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.clearAllTimers();
  });

  const mockSpark: Spark = {
    id: "1",
    content: "Hello",
    userHash: "abc",
    createdAt: new Date().toISOString(),
    decayAt: new Date(Date.now() + 10000).toISOString(),
  };

  it("should buffer events and process them in batch", () => {
    const { result } = renderHook(() => useSparkBatcher());

    const event: TimelineEvent = {
      type: "spark_posted",
      data: mockSpark,
    };

    act(() => {
      result.current.pushEvent(event);
    });

    // Validating buffer... State shouldn't change yet
    expect(result.current.sparks).toHaveLength(0);

    // Advance time
    act(() => {
      vi.advanceTimersByTime(200);
    });

    expect(result.current.sparks).toHaveLength(1);
    expect(result.current.sparks[0].id).toBe("1");
  });

  it("should deduplicate sparks", () => {
    const { result } = renderHook(() => useSparkBatcher());

    const event: TimelineEvent = { type: "spark_posted", data: mockSpark };

    act(() => {
      result.current.pushEvent(event);
      result.current.pushEvent(event); // Same event
      vi.advanceTimersByTime(200);
    });

    expect(result.current.sparks).toHaveLength(1);
  });

  it("should update spark", () => {
    const { result } = renderHook(() => useSparkBatcher());

    // Initial spark
    act(() => {
      result.current.pushEvent({ type: "spark_posted", data: mockSpark });
      vi.advanceTimersByTime(200);
    });

    // Update event
    const newDecay = new Date(Date.now() + 20000).toISOString();
    const updateEvent: TimelineEvent = {
      type: "spark_updated",
      spark_id: "1",
      level: "kindling",
      decay_at: newDecay,
    };

    act(() => {
      result.current.pushEvent(updateEvent);
      vi.advanceTimersByTime(200);
    });

    expect(result.current.sparks[0].decayAt).toBe(newDecay);
  });

  it("should remove spark on bonfire promotion and trigger callback", () => {
    const onPromoted = vi.fn();
    const { result } = renderHook(() => useSparkBatcher(onPromoted));

    // Initial
    act(() => {
      result.current.pushEvent({ type: "spark_posted", data: mockSpark });
      vi.advanceTimersByTime(200);
    });

    // Promote
    const promoteEvent: TimelineEvent = {
      type: "spark_updated",
      spark_id: "1",
      level: "bonfire",
      decay_at: new Date().toISOString(),
    };

    act(() => {
      result.current.pushEvent(promoteEvent);
      vi.advanceTimersByTime(200);
    });

    expect(result.current.sparks).toHaveLength(0);

    // Wait for next tick/timeout inside effect
    act(() => {
      vi.advanceTimersByTime(1);
    });
    expect(onPromoted).toHaveBeenCalled();
  });
});

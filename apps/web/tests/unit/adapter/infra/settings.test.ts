/**
 * Settings Unit Test
 *
 * Validates settings loading and default values.
 */

import { describe, it, expect } from "vitest";
import { settings } from "@/adapter/infra/settings";

describe("Settings", () => {
  it("should load default spark configuration", () => {
    // Verify all settings have valid default values
    expect(settings.sparkMaxLength).toBe(500);
    expect(settings.sparkRateLimitCount).toBe(10);
    expect(settings.sparkRateLimitWindowSeconds).toBe(60);
    expect(settings.sparkVisibleDurationMinutes).toBe(10);
    expect(settings.sparkTtlDays).toBe(30);
  });

  it("should be immutable (frozen)", () => {
    // Settings should be frozen to prevent modifications
    expect(Object.isFrozen(settings)).toBe(true);

    // Attempting to modify should throw in strict mode (which tests run in)
    expect(() => {
      // @ts-expect-error - Testing immutability
      settings.sparkMaxLength = 999;
    }).toThrow();

    // Value should remain unchanged
    expect(settings.sparkMaxLength).toBe(500);
  });

  it("should have positive numeric values", () => {
    expect(settings.sparkMaxLength).toBeGreaterThan(0);
    expect(settings.sparkRateLimitCount).toBeGreaterThan(0);
    expect(settings.sparkRateLimitWindowSeconds).toBeGreaterThan(0);
    expect(settings.sparkVisibleDurationMinutes).toBeGreaterThan(0);
    expect(settings.sparkTtlDays).toBeGreaterThan(0);
  });
});

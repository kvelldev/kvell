import { detectSparkImage } from "@/domain/service/sparkUrlService";
import { describe, it, expect } from "vitest";
import {
  generatePollutedTestCases,
  generateYouTubeTestCases,
  type URLTestCase,
} from "./fixtures/urlTestCases";

describe("sparkUrlService", () => {
  const directImageCases = generatePollutedTestCases();
  const youtubeCases = generateYouTubeTestCases();
  const allCases = [...directImageCases, ...youtubeCases];

  describe("detectSparkImage (Data-Driven)", () => {
    it.each(allCases)("$name", ({ input, expected }: URLTestCase) => {
      expect(detectSparkImage(input)).toEqual(expected);
    });
  });

  describe("detectSparkImage (Edge Cases)", () => {
    it("returns null for generic image links not in allowlist", () => {
      const input = "Check this https://example.com/image.jpg";
      expect(detectSparkImage(input)).toBeNull();
    });

    it("returns null for non-image links", () => {
      const input = "Check this https://sakurazaka46.com/news/";
      expect(detectSparkImage(input)).toBeNull();
    });

    it("returns null for empty content", () => {
      expect(detectSparkImage("")).toBeNull();
    });

    it("returns first valid image if multiple present", () => {
      // Should pick the first valid one
      const input =
        "Line 1 https://sakurazaka46.com/1.jpg Line 2 https://pbs.twimg.com/media/2.jpg";
      expect(detectSparkImage(input)).toEqual({
        primaryUrl: "https://sakurazaka46.com/1.jpg",
      });
    });

    it("handles concatenated URLs robustly", () => {
      const input =
        "https://sakurazaka46.com/1.jpghttps://sakurazaka46.com/2.jpg";
      expect(detectSparkImage(input)).toEqual({
        primaryUrl: "https://sakurazaka46.com/1.jpg",
      });
    });
  });
});

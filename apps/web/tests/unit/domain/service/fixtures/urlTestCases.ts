/**
 * Test fixtures for sparkUrlService
 *
 * Defines valid URLs and contamination suffixes to generate data-driven test cases.
 */

export const validDirectImageUrls = [
  "https://sakurazaka46.com/images/14/1da/abc.jpg",
  "https://nogizaka46.com/files/46/diary/n46/member/moblog/202301/moblog_12345.jpg",
  "https://pbs.twimg.com/media/F_xxxxx.jpg",
  "https://pbs.twimg.com/media/G_yyyyy.png?format=jpg&name=large",
  "https://instagram.fxxx1-1.fna.fbcdn.net/v/t51.2885-15/e35/p1080x1080/123_456.jpg",
];

export const validYouTubeUrls = [
  {
    input: "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    videoId: "dQw4w9WgXcQ",
  },
  {
    input: "https://youtu.be/dQw4w9WgXcQ",
    videoId: "dQw4w9WgXcQ",
  },
  {
    input: "https://www.youtube.com/watch?v=dQw4w9WgXcQ&feature=youtu.be",
    videoId: "dQw4w9WgXcQ",
  },
];

export const pollutionSuffixes = ["!", "?", ".", ",", ")", "...", "!?", ")."];

export interface DetectedImage {
  primaryUrl: string;
  fallbackUrl?: string;
}

export interface URLTestCase {
  name: string;
  input: string;
  expected: DetectedImage | null;
}

/**
 * Generates test cases by combining valid URLs with pollution suffixes.
 */
export const generatePollutedTestCases = (): URLTestCase[] => {
  const cases: URLTestCase[] = [];

  // Direct Image URLs
  validDirectImageUrls.forEach((url) => {
    const expected = { primaryUrl: url };

    // 1. Clean
    cases.push({
      name: `[Direct] Clean: ${url}`,
      input: url,
      expected: expected,
    });

    // 2. Polluted
    pollutionSuffixes.forEach((suffix) => {
      cases.push({
        name: `[Direct] Polluted with '${suffix}': ${url}`,
        input: `${url}${suffix}`,
        expected: expected,
      });
    });

    // 3. Embedded in text
    cases.push({
      name: `[Direct] Embedded in text: ${url}`,
      input: `Check this out: ${url} !`,
      expected: expected,
    });

    // 4. Concatenated (Edge case)
    // "url1.jpghttps://url2.jpg" -> "url1.jpg"
    cases.push({
      name: `[Direct] Concatenated: ${url}`,
      input: `${url}https://example.com/next`,
      expected: expected,
    });
  });

  return cases;
};

/**
 * Generates test cases for YouTube URLs (Clean & Polluted)
 * Note: YouTube URLs are transformed to thumbnail URLs
 */
export const generateYouTubeTestCases = (): URLTestCase[] => {
  const cases: URLTestCase[] = [];

  validYouTubeUrls.forEach(({ input, videoId }) => {
    const expected = {
      primaryUrl: `https://img.youtube.com/vi/${videoId}/maxresdefault.jpg`,
      fallbackUrl: `https://img.youtube.com/vi/${videoId}/hqdefault.jpg`,
    };

    // 1. Clean
    cases.push({
      name: `[YouTube] Clean: ${input}`,
      input: input,
      expected: expected,
    });

    // 2. Polluted
    pollutionSuffixes.forEach((suffix) => {
      cases.push({
        name: `[YouTube] Polluted with '${suffix}': ${input}`,
        input: `${input}${suffix}`,
        expected: expected,
      });
    });

    // 3. With Params (time, etc) - regex should handle if match logic is good
    // "https://youtu.be/ID?t=1s"
    const inputWithParam = `${input}?t=10s`;
    cases.push({
      name: `[YouTube] With Params: ${inputWithParam}`,
      input: inputWithParam,
      expected: expected,
    });
  });

  return cases;
};

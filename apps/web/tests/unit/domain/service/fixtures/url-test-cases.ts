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
  // TV Stations
  "https://statics.tver.jp/images/content/12345.jpg",
  "https://www.nhk.jp/static/assets/images/icon.png", // NHK short domain
  "https://www.nhk.or.jp/common/images/logo.png",
  "https://www.tv-asahi.co.jp/common/images/logo.jpg",
  "https://tv-tokyo.imgix.net/txcms/media/pg/L/82/95/9d7b2b1c13133706d74285b246a6.jpg?auto=format,compress&w=793&h=447&fill=blur&fit=fill&dpr=2",
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

/**
 * Detected image result interface
 */
export interface DetectedImage {
  primaryUrl: string;
  fallbackUrl?: string;
}

/**
 * URL Test Case interface
 */
export interface URLTestCase {
  name: string;
  input: string;
  expected: DetectedImage | null;
}

/**
 * Generates test cases by combining valid URLs with pollution suffixes.
 * @returns Array of URLTestCase
 */
export const generatePollutedTestCases = (): URLTestCase[] => {
  return validDirectImageUrls.flatMap((url) => {
    const expected = { primaryUrl: url };

    return [
      // 1. Clean
      {
        name: `[Direct] Clean: ${url}`,
        input: url,
        expected,
      },
      // 2. Polluted
      ...pollutionSuffixes.map((suffix) => ({
        name: `[Direct] Polluted with '${suffix}': ${url}`,
        input: `${url}${suffix}`,
        expected,
      })),
      // 3. Embedded in text
      {
        name: `[Direct] Embedded in text: ${url}`,
        input: `Check this out: ${url} !`,
        expected,
      },
      // 4. Concatenated (Edge case)
      {
        name: `[Direct] Concatenated: ${url}`,
        input: `${url}https://example.com/next`,
        expected,
      },
    ];
  });
};

/**
 * Generates test cases for YouTube URLs (Clean & Polluted)
 * Note: YouTube URLs are transformed to thumbnail URLs
 * @returns Array of URLTestCase
 */
export const generateYouTubeTestCases = (): URLTestCase[] => {
  return validYouTubeUrls.flatMap(({ input, videoId }) => {
    const expected = {
      primaryUrl: `https://img.youtube.com/vi/${videoId}/maxresdefault.jpg`,
      fallbackUrl: `https://img.youtube.com/vi/${videoId}/hqdefault.jpg`,
    };

    return [
      // 1. Clean
      {
        name: `[YouTube] Clean: ${input}`,
        input,
        expected,
      },
      // 2. Polluted
      ...pollutionSuffixes.map((suffix) => ({
        name: `[YouTube] Polluted with '${suffix}': ${input}`,
        input: `${input}${suffix}`,
        expected,
      })),
      // 3. With Params (time, etc)
      {
        name: `[YouTube] With Params: ${input}?t=10s`,
        input: `${input}?t=10s`,
        expected,
      },
    ];
  });
};

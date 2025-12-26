/**
 * Spark URL Service
 *
 * Handles logic for detecting and acting upon URLs within spark content.
 * Enforces the strict "Allowlist Policy" for image rendering.
 */

/**
 * Regex patterns for allowlisted domains and extensions.
 *
 * Rules:
 * 1. Must start with http:// or https://
 * 2. Must match specific domains OR specific extensions
 */
const ALLOWLIST_PATTERNS = [
  // Official Domains (Sakurazaka, Nogizaka, BokuAo)
  /^https?:\/\/(?:Basic\.)?sakurazaka46\.com\/.*(?:\.jpg|\.jpeg|\.png|\.gif|\.webp)/i,
  /^https?:\/\/(?:Basic\.)?nogizaka46\.com\/.*(?:\.jpg|\.jpeg|\.png|\.gif|\.webp)/i,
  /^https?:\/\/(?:Basic\.)?bokuao\.com\/.*(?:\.jpg|\.jpeg|\.png|\.gif|\.webp)/i,

  // Twitter/X Images (pbs.twimg.com)
  // Example: https://pbs.twimg.com/media/XXXXX.jpg
  // Note: Matches URL with or without query params, but strictly checks domain
  /^https?:\/\/pbs\.twimg\.com\/media\/[a-zA-Z0-9_-]+(?:\?format=[a-z]+|\.[a-z]+)/i,

  // Instagram CDN (cdninstagram.com, fbcdn.net)
  /^https?:\/\/[a-z0-9.-]+\.cdninstagram\.com\/.*(?:\.jpg|\.jpeg|\.png|\.gif|\.webp)/i,
  /^https?:\/\/[a-z0-9.-]+\.fbcdn\.net\/.*(?:\.jpg|\.jpeg|\.png|\.gif|\.webp)/i,

  // General Direct Image Links (Must end with extension, simple check)
  // REMOVED: Allowlist policy only permits specific domains.
  // /^https?:\/\/.*\.(?:jpg|jpeg|png|gif|webp)(?:\?.*)?$/i,
];

// YouTube Video ID Extraction (Special case)
const YOUTUBE_PATTERNS = [
  /youtube\.com\/watch\?v=([a-zA-Z0-9_-]{11})/,
  /youtu\.be\/([a-zA-Z0-9_-]{11})/,
];

/**
 * Detected image result object.
 */
export interface DetectedImage {
  primaryUrl: string;
  fallbackUrl?: string;
}

/**
 * Detects if the spark content contains a renderable image URL.
 * Returns the detected image object or null if none.
 *
 * Strategy:
 * 1. Extract URL-candidates using regex that handles concatenated URLs.
 * 2. Trim trailing punctuation.
 * 3. Check against allowlist patterns.
 * 4. Return the first match with optional fallback.
 *
 * @param content - Spark content text
 * @returns The detected image result or null
 */
export const detectSparkImage = (content: string): DetectedImage | null => {
  if (!content) return null;

  // 1. Regex extraction
  // Matches http(s):// followed by non-whitespace characters.
  // Uses negative lookahead (?!https?://) inside the repetition to stop at the start of a new URL.
  // This handles cases like "url1.jpghttps://url2.jpg"
  const matches = content.match(/https?:\/\/(?:(?!https?:\/\/)[^\s])+/g);
  if (!matches) return null;

  for (const rawUrl of matches) {
    // 2. Clean trailing punctuation
    // Removes !, ?, ., ,, ), and combinations like ...) or !? at the end
    const url = rawUrl.replace(/[!?,.)]+$/, "");

    // 3. Check against all patterns
    for (const pattern of ALLOWLIST_PATTERNS) {
      if (pattern.test(url)) {
        return { primaryUrl: url };
      }
    }

    // Special case: YouTube
    // If it's a YouTube link, we generate the thumbnail URL
    // Primary: maxresdefault (High Res), Fallback: hqdefault (Standard)
    for (const ytPattern of YOUTUBE_PATTERNS) {
      const match = url.match(ytPattern);
      if (match?.[1]) {
        return {
          primaryUrl: `https://img.youtube.com/vi/${match[1]}/maxresdefault.jpg`,
          fallbackUrl: `https://img.youtube.com/vi/${match[1]}/hqdefault.jpg`,
        };
      }
    }
  }

  return null;
};

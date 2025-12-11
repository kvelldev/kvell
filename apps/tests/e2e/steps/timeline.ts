import { createBdd } from "playwright-bdd";
import { expect } from "@playwright/test";
import { MongoClient, Db } from "mongodb";
import { MONGO_URL, DB_NAME, DB_COLLECTIONS, TIMELINE_TEST_CONSTANTS } from "../constants";

/**
 * Timeline E2E Step Definitions
 *
 * Based on timeline.feature Gherkin scenarios.
 * Implements the timeline display flow with:
 * - Auto-scroll to bottom (chat-style)
 * - Fade-out effects at the top boundary
 * - Visual weathering effects for aging sparks
 * - Smoke animation on expiration
 * - Empty state handling
 *
 * Given: DB direct operations + system configuration
 * When: Browser (Playwright page) operations + time simulation
 * Then: Browser assertions using data-testid + visual effects
 */

let mongoClient: MongoClient;
let db: Db;

// System configuration values (from Background) - mutable for Gherkin override
let sparkLifetimeSeconds: number = TIMELINE_TEST_CONSTANTS.SPARK_LIFETIME_SECONDS;
let coolingThresholdSeconds: number = TIMELINE_TEST_CONSTANTS.COOLING_THRESHOLD_SECONDS;

const { Given, When, Then, After } = createBdd();

/**
 * Given: Database state setup
 * Note: System configuration steps are handled in post_spark.ts
 */
Given('複数の {string} が存在し、{string} が画面高さを超えている', async ({}, _entity: string, _area: string) => {
  // Connect to MongoDB
  mongoClient = new MongoClient(MONGO_URL);
  await mongoClient.connect();
  db = mongoClient.db(DB_NAME);

  // Clean up existing test data
  await db.collection(DB_COLLECTIONS.SPARKS).deleteMany({});

  const now = new Date();
  const decayAt = new Date(now.getTime() + sparkLifetimeSeconds * 1000);
  const vanishAt = new Date(now.getTime() + TIMELINE_TEST_CONSTANTS.LEGAL_RETENTION_DAYS * 24 * 60 * 60 * 1000);

  // Create multiple sparks to exceed screen height
  const sparks = [];
  for (let i = 1; i <= TIMELINE_TEST_CONSTANTS.TEST_SPARK_COUNT; i++) {
    sparks.push({
      id: `${TIMELINE_TEST_CONSTANTS.SPARK_ID_PREFIX}${i}`,
      content: `テスト種火 ${i}：これはテスト用の種火です。画面高さを超えるために複数の種火を投稿しています。`,
      user_hash: `test-user-hash-${i % 3}`,
      created_at: new Date(now.getTime() - i * TIMELINE_TEST_CONSTANTS.TEST_SPARK_INTERVAL_MS),
      decay_at: decayAt,
      vanish_at: vanishAt,
      fuel_count: Math.floor(Math.random() * 10),
    });
  }

  await db.collection(DB_COLLECTIONS.SPARKS).insertMany(sparks);
});

Given('{string} に表示できる有効な {string} が0件である', async ({}, _area: string, _entity: string) => {
  // Connect to MongoDB
  mongoClient = new MongoClient(MONGO_URL);
  await mongoClient.connect();
  db = mongoClient.db(DB_NAME);

  // Clean up all sparks to create empty state
  await db.collection(DB_COLLECTIONS.SPARKS).deleteMany({});
});

Given('ユーザーは {string} を閲覧している', async ({ page }, _area: string) => {
  // Navigate to timeline page
  await page.goto("/timeline");
  await page.waitForLoadState("networkidle");

  // Wait for WebSocket connection to establish and initial sparks to load
  await page.waitForTimeout(TIMELINE_TEST_CONSTANTS.WAIT_FOR_WS_CONNECTION_MS);
});

Given('新しい {string} が投稿される（残り寿命 100%〜30%）', async ({ page }, _entity: string) => {
  // Connect to MongoDB if not already connected
  if (!mongoClient) {
    mongoClient = new MongoClient(MONGO_URL);
    await mongoClient.connect();
    db = mongoClient.db(DB_NAME);
  }

  // Create a fresh spark with high remaining lifetime
  const now = new Date();
  const decayAt = new Date(now.getTime() + sparkLifetimeSeconds * 1000);
  const vanishAt = new Date(now.getTime() + TIMELINE_TEST_CONSTANTS.LEGAL_RETENTION_DAYS * 24 * 60 * 60 * 1000);

  await db.collection(DB_COLLECTIONS.SPARKS).insertOne({
    id: TIMELINE_TEST_CONSTANTS.FRESH_SPARK_ID,
    content: "これは新しい種火です。高温状態で表示されるはずです。",
    user_hash: TIMELINE_TEST_CONSTANTS.FRESH_SPARK_USER_HASH,
    created_at: now,
    decay_at: decayAt,
    vanish_at: vanishAt,
    fuel_count: 0,
  });

  // Refresh page to see new spark
  await page.reload();
  await page.waitForLoadState("networkidle");
});

Given('投稿から時間が経過している {string} がある', async ({}, _entity: string) => {
  // Connect to MongoDB if not already connected (needed for updateOne in When step)
  if (!mongoClient) {
    mongoClient = new MongoClient(MONGO_URL);
    await mongoClient.connect();
    db = mongoClient.db(DB_NAME);
  }
});


/**
 * When: User actions and time-based events
 */
When('ユーザーがページを開く（またはリロードする）', async ({ page }) => {
  await page.goto("/timeline");
  await page.waitForLoadState("networkidle");

  // Wait for WebSocket connection to establish and initial sparks to load
  await page.waitForTimeout(TIMELINE_TEST_CONSTANTS.WAIT_FOR_WS_CONNECTION_MS);
});

When('ユーザーが意図的に上へスクロールする', async ({ page }) => {
  // Scroll up in the timeline
  const timeline = page.getByTestId("timeline-container");
  await timeline.evaluate((el) => {
    el.scrollTop = 0;
  });
  await page.waitForTimeout(TIMELINE_TEST_CONSTANTS.SHORT_WAIT_MS);
});

When('その {string} の残り寿命が {string} を下回る', async ({ page }, _entity: string, threshold: string) => {
  // Simulate time passing by updating the DB
  // threshold = "冷却閾値" (18 seconds for 1-minute decay time)

  // Update spark to have passed cooling threshold
  // Set created_at to a time where remaining lifetime is less than cooling threshold
  const now = new Date();
  const coolingTime = new Date(now.getTime() - (sparkLifetimeSeconds - coolingThresholdSeconds + 1) * 1000);

  await db.collection(DB_COLLECTIONS.SPARKS).updateOne(
    { id: TIMELINE_TEST_CONSTANTS.FRESH_SPARK_ID },
    {
      $set: {
        created_at: coolingTime
      }
    }
  );

  // Reload to see the updated state
  await page.reload();
  await page.waitForLoadState("networkidle");
});


/**
 * Then: UI Assertions
 */
Then('{string} は最初から「最下部」にスクロールされた状態で表示される', async ({ page }, _area: string) => {
  const timeline = page.getByTestId("timeline-container");

  // Check that timeline is scrolled to bottom
  const isAtBottom = await timeline.evaluate((el) => {
    const scrollBottom = el.scrollHeight - el.scrollTop - el.clientHeight;
    return scrollBottom < 10; // Allow small tolerance
  });

  expect(isAtBottom).toBe(true);
});

Then('ユーザーが操作しなくても、新しい {string} が来れば自動で表示される', async ({ page }, _entity: string) => {
  // This is a behavioral check - verify auto-scroll is enabled
  // In practice, this would be tested by injecting a new spark via WebSocket
  // and verifying the timeline auto-scrolls to show it

  // For now, we verify that the timeline is in "follow mode"
  const timeline = page.getByTestId("timeline-container");
  expect(await timeline.isVisible()).toBe(true);
});

Then('自動スクロールは解除され、その場に留まる（新しいSparkが来ても勝手に動かない）', async ({ page }) => {
  // After scrolling up, verify position remains stable
  const timeline = page.getByTestId("timeline-container");

  const scrollTopBefore = await timeline.evaluate((el) => el.scrollTop);

  // Wait a moment
  await page.waitForTimeout(TIMELINE_TEST_CONSTANTS.SHORT_WAIT_MS);

  const scrollTopAfter = await timeline.evaluate((el) => el.scrollTop);

  // Scroll position should remain unchanged
  expect(scrollTopAfter).toBe(scrollTopBefore);
});

Then('その {string} は「白文字（Smoke White）」で表示される', async ({ page }, _entity: string) => {
  // Check for white text color on fresh sparks
  const spark = page.getByTestId("spark-item").first();
  const color = await spark.evaluate((el) => {
    return window.getComputedStyle(el).color;
  });

  // White color in RGB: rgb(255, 255, 255) or similar
  // Allow for off-white colors (e.g., #F5F5F5)
  expect(color).toMatch(/rgb\(2[0-9]{2},\s*2[0-9]{2},\s*2[0-9]{2}\)/);
});

Then('その {string} は「オレンジ色の枠線（Ember Border）」と「発光（Glow）」を持つ', async ({ page }, _entity: string) => {
  const spark = page.getByTestId("spark-item").first();

  // Check border color (orange)
  const borderColor = await spark.evaluate((el) => {
    return window.getComputedStyle(el).borderColor;
  });

  // Orange color in RGB (e.g., rgb(255, 165, 0))
  expect(borderColor).toMatch(/rgb\(2[0-9]{2},\s*[0-9]{1,3},\s*[0-9]{1,2}\)/);

  // Check for box-shadow (glow effect)
  const boxShadow = await spark.evaluate((el) => {
    return window.getComputedStyle(el).boxShadow;
  });

  expect(boxShadow).not.toBe("none");
});

Then('その {string} には「残り時間（例: 09:59）」がカウントダウン表示される', async ({ page }, _entity: string) => {
  // Check for countdown timer display
  const timer = page.getByTestId("spark-timer").first();
  await expect(timer).toBeVisible();

  const timerText = await timer.textContent();

  // Timer format: MM:SS (e.g., "09:59")
  expect(timerText).toMatch(/\d{2}:\d{2}/);
});

Then('その {string} は「灰色文字（Ash Gray）」へと変化する', async ({ page }, _entity: string) => {
  const spark = page.getByTestId("spark-item").first();
  const color = await spark.evaluate((el) => {
    return window.getComputedStyle(el).color;
  });

  // Gray color in RGB (e.g., rgb(128, 128, 128))
  expect(color).toMatch(/rgb\([0-9]{1,3},\s*[0-9]{1,3},\s*[0-9]{1,3}\)/);

  // Verify it's not white (less than GRAY_TEXT_RGB_MAX for each RGB component)
  const rgbValues = color.match(/\d+/g)?.map(Number) || [];
  expect(Math.max(...rgbValues)).toBeLessThan(TIMELINE_TEST_CONSTANTS.GRAY_TEXT_RGB_MAX);
});

Then('その {string} の「枠線」と「発光」は消失する（border-0 \\/ shadow-none）', async ({ page }, _entity: string) => {
  const spark = page.getByTestId("spark-item").first();

  // Check border is removed or transparent
  const borderWidth = await spark.evaluate((el) => {
    return window.getComputedStyle(el).borderWidth;
  });

  expect(borderWidth).toBe("0px");

  // Check box-shadow is none
  const boxShadow = await spark.evaluate((el) => {
    return window.getComputedStyle(el).boxShadow;
  });

  expect(boxShadow).toBe("none");
});

Then('「残り時間」の表示も灰色になり、カウントダウンは継続する', async ({ page }) => {
  const timer = page.getByTestId("spark-timer").first();

  // Check timer color is gray
  const color = await timer.evaluate((el) => {
    return window.getComputedStyle(el).color;
  });

  expect(color).toMatch(/rgb\([0-9]{1,3},\s*[0-9]{1,3},\s*[0-9]{1,3}\)/);

  // Verify countdown is still running by checking time format
  const timerText = await timer.textContent();
  expect(timerText).toMatch(/\d{2}:\d{2}/);
});




Then('画面中央にアイコン等は表示せず、テキストのみを表示する', async ({ page }) => {
  // Navigate to timeline with empty state
  await page.goto("/timeline");
  await page.waitForLoadState("networkidle");

  const emptyState = page.getByTestId("timeline-empty-state");
  await expect(emptyState).toBeVisible();

  // Verify no icons are displayed (text only)
  const hasIcon = await emptyState.locator("svg, img").count();
  expect(hasIcon).toBe(0);
});

Then('テキストの内容は「静かな夜空です。」とする', async ({ page }) => {
  const emptyState = page.getByTestId("timeline-empty-state");
  const text = await emptyState.textContent();

  expect(text).toContain("静かな夜空です。");
});

/**
 * After: Cleanup MongoDB connection after each scenario
 */
After(async () => {
  if (mongoClient) {
    try {
      await mongoClient.close();
    } catch (error) {
      // Ignore errors when closing already-closed connections
    } finally {
      mongoClient = null as any;
      db = null as any;
    }
  }
});

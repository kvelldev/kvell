import { createBdd } from 'playwright-bdd';
import { expect } from '@playwright/test';
import { MongoClient, Db } from 'mongodb';
import { MONGO_URL, DB_NAME, DB_COLLECTIONS } from '../constants';

/**
 * Health Check E2E Step Definitions
 *
 * Given: DB direct operations (stable setup)
 * When: Browser (Playwright page) operations
 * Then: Browser assertions using data-testid
 */

let mongoClient: MongoClient;
let db: Db;

const { Given, When, Then, After } = createBdd();

/**
 * Given: Kvellのデータベースが正常に起動している
 */
Given('Kvellのデータベースが正常に起動している', async () => {
  // Connect to MongoDB
  mongoClient = new MongoClient(MONGO_URL);
  await mongoClient.connect();
  db = mongoClient.db(DB_NAME);

  // Verify connection by pinging
  await db.admin().ping();

  // Clean up existing test data
  await db.collection(DB_COLLECTIONS.HEALTH_MESSAGES).deleteMany({});
});

/**
 * Given: データベースにシステムメッセージ "{message}" が登録されている
 */
Given('データベースにシステムメッセージ {string} が登録されている', async ({ }, message: string) => {
  // Insert test data directly to DB with same structure as backend
  const crypto = await import('crypto');
  await db.collection(DB_COLLECTIONS.HEALTH_MESSAGES).insertOne({
    id: crypto.randomUUID(),
    message,
    createdAt: new Date(),
  });
});

/**
 * When: ユーザーがKvellのトップページにアクセスする
 */
When('ユーザーがKvellのトップページにアクセスする', async ({ page }) => {
  await page.goto('/');
  await page.waitForLoadState('networkidle');
});

/**
 * When: ヘルスチェックボタンをクリックする
 */
When('ヘルスチェックボタンをクリックする', async ({ page }) => {
  // Use data-testid as per 31_E2E.md guidelines
  const fetchButton = page.getByTestId('health-fetch-button');
  await fetchButton.click();

  // Wait for message display to appear (more stable than waiting for API response)
  const messageDisplay = page.getByTestId('health-message-display');
  await messageDisplay.waitFor({ state: 'visible', timeout: 60000 });
});

/**
 * Then: 画面上にシステムメッセージ "{expectedMessage}" が表示される
 */
Then('画面上にシステムメッセージ {string} が表示される', async ({ page }, expectedMessage: string) => {
  // Use data-testid for stable assertions
  const messageDisplay = page.getByTestId('health-message-display');

  // Verify the message is visible
  await expect(messageDisplay).toBeVisible();

  // Verify the message content contains the expected text
  await expect(messageDisplay).toContainText(expectedMessage);
});

/**
 * After: Cleanup MongoDB connection after each scenario
 */
After(async () => {
  if (mongoClient) {
    await mongoClient.close();
  }
});

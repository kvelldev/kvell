/**
 * Integration Test Setup
 *
 * Setup MSW (Mock Service Worker) for integration tests.
 * MSW intercepts HTTP requests and provides mocked responses.
 */

import { http, HttpResponse } from "msw";
import { setupServer } from "msw/node";
import { beforeAll, afterAll, afterEach } from "vitest";
import type { HealthMessage } from "@/domain/model/health";

export const BASE_URL = "http://localhost:8000";

/**
 * Mock data store for health messages
 * Simulates database state across test scenarios
 */
export const mockHealthStore = {
  messages: [] as HealthMessage[],
  reset() {
    this.messages = [];
  },
  getLatest(): HealthMessage | null {
    if (this.messages.length === 0) return null;
    return this.messages.at(-1) ?? null;
  },
  add(message: HealthMessage) {
    this.messages.push(message);
  },
};

/**
 * MSW Request Handlers
 * Define mock API endpoints that match backend behavior
 */
export const handlers = [
  // GET /api/health/latest
  http.get(`${BASE_URL}/api/health/latest`, () => {
    const latest = mockHealthStore.getLatest();
    return HttpResponse.json(latest);
  }),

  // POST /api/health/echo
  http.post(`${BASE_URL}/api/health/echo`, async ({ request }) => {
    const body = (await request.json()) as { message: string };

    const newMessage: HealthMessage = {
      id: crypto.randomUUID(),
      message: body.message,
      createdAt: new Date().toISOString(),
    };

    mockHealthStore.add(newMessage);
    return HttpResponse.json(newMessage);
  }),
];

/**
 * MSW Server Instance
 * Intercepts all HTTP requests during tests
 */
export const server = setupServer(...handlers);

// Setup MSW before all tests
beforeAll(() => {
  server.listen({ onUnhandledRequest: "error" });
});

// Reset handlers and mock data after each test
afterEach(() => {
  server.resetHandlers();
  mockHealthStore.reset();
});

// Cleanup after all tests
afterAll(() => {
  server.close();
});

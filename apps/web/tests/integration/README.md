# Frontend Integration Tests

## Overview

This directory contains integration tests for the frontend application. Integration tests verify the complete flow from UI components through business logic to API calls, testing the integration of multiple layers without mocking internal dependencies.

## Test Strategy

### What Are Integration Tests?

Integration tests sit between unit tests and E2E tests:

- **Unit Tests** (`tests/unit/`): Test individual components/functions in isolation with mocked dependencies
- **Integration Tests** (`tests/integration/`): Test multiple layers working together (Page → UseCase → Repository → API)
- **E2E Tests** (`apps/tests/e2e/`): Test the entire system including real backend and browser

### What We Test

Integration tests focus on:

1. **Component Integration**: How Page components integrate with UseCase hooks and UI components
2. **Data Flow**: Data flowing from API → Repository → UseCase → UI
3. **User Interactions**: Actual user actions (typing, clicking) and their effects
4. **State Management**: How SWR caching and state updates work across layers
5. **Error Handling**: How errors propagate through layers and are displayed in UI

### What We Mock

We only mock the **HTTP boundary** using MSW (Mock Service Worker):

- ✅ **Mocked**: HTTP requests/responses (API endpoints)
- ❌ **Not Mocked**: Repository implementations, UseCase hooks, UI components
- ❌ **Not Mocked**: React state management, SWR caching behavior

This approach provides:
- **Realistic Integration**: Tests real component interactions
- **Fast Execution**: No real backend needed (MSW intercepts HTTP)
- **Deterministic**: Controlled API responses, no flakiness

## Technology Stack

- **Test Framework**: Vitest
- **Test Utilities**: React Testing Library, Testing Library User Event
- **API Mocking**: MSW (Mock Service Worker)

## Running Tests

### Run All Tests

```bash
npm test
```

### Run Integration Tests Only

```bash
npm test tests/integration/
```

### Run Specific Test File

```bash
npm test tests/integration/health-check.test.tsx
```

### Watch Mode

```bash
npx vitest tests/integration/ --watch
```

### Coverage

```bash
npm run coverage
```

## File Structure

```
tests/integration/
├── README.md              # This file
├── setup.ts               # MSW configuration and mock data store
└── health-check.test.tsx  # HealthCheck integration tests
```

## Writing Integration Tests

### Test Naming Convention

Follow the naming pattern: `test_<action>_when<Condition>_<result>`

```typescript
it("test_saveMessage_whenValidInput_savesAndDisplaysNewMessage", async () => {
  /**
   * Action: saveMessage (user enters text and clicks Echo button)
   * Condition: whenValidInput (valid message text)
   * Result: savesAndDisplaysNewMessage (saves to backend and updates UI)
   */
  // Test implementation...
});
```

### Test Structure

```typescript
import { describe, it, expect, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { mockHealthStore } from "./setup";
import "./setup"; // Import to ensure MSW is configured

describe("Feature Integration", () => {
  beforeEach(() => {
    mockHealthStore.reset(); // Reset mock data before each test
  });

  it("test_action_whenCondition_result", async () => {
    // Arrange: Setup initial state
    const user = userEvent.setup();
    render(<YourPage />);

    // Act: Perform user actions
    await user.click(screen.getByRole("button"));

    // Assert: Verify results
    await waitFor(() => {
      expect(screen.getByText("Expected Result")).toBeInTheDocument();
    });
  });
});
```

### Key Patterns

#### 1. Wait for Async Updates

Always use `waitFor` when testing async operations (data fetching, mutations):

```typescript
await waitFor(() => {
  expect(screen.getByText("Loaded Data")).toBeInTheDocument();
});
```

#### 2. User Interactions

Use `@testing-library/user-event` for realistic user interactions:

```typescript
const user = userEvent.setup();
await user.type(input, "Test message");
await user.click(button);
```

#### 3. Mock Data Setup

Use `mockHealthStore` to pre-populate data for tests:

```typescript
beforeEach(() => {
  mockHealthStore.add({
    id: "test-id",
    message: "Existing message",
    createdAt: new Date().toISOString(),
  });
});
```

#### 4. Error Simulation

Override MSW handlers to simulate API errors:

```typescript
import { server } from "./setup";
import { http, HttpResponse } from "msw";

server.use(
  http.post("http://localhost:8000/api/health/echo", () => {
    return HttpResponse.json({ detail: "Error" }, { status: 500 });
  }),
);
```

## Common Issues

### Issue: Tests timeout or hang

**Solution**: Ensure you're using `waitFor` for async operations. Check that MSW handlers are defined correctly.

### Issue: "No handler found for request"

**Solution**: Verify the request URL matches the handler URL exactly. MSW will error on unhandled requests by default (configured in `setup.ts`).

### Issue: State persists between tests

**Solution**: Make sure `mockHealthStore.reset()` is called in `beforeEach`. Check that no global state is leaking.

### Issue: Cannot find element in DOM

**Solution**: Use `screen.debug()` to inspect rendered output. Ensure you're waiting for loading states to complete with `waitFor`.

## Comparison with Backend Integration Tests

### Backend (`apps/api/tests/integration/`)

- Uses real MongoDB database
- Tests API endpoints with HTTP client
- Verifies database persistence
- Setup: `conftest.py` with database fixtures

### Frontend (`apps/web/tests/integration/`)

- Uses MSW to mock API
- Tests UI components with user interactions
- Verifies UI rendering and state management
- Setup: `setup.ts` with MSW and mock data store

Both follow similar principles:
- Test real integration (minimal mocking)
- Focus on happy paths and error cases
- Use descriptive test names
- Verify end-to-end behavior within their layer

## Related Documentation

- [Frontend Architecture Guidelines](../../.prompts/20_frontend.md)
- [Backend Integration Tests](../../../api/tests/README.md)
- [E2E Testing Guidelines](../../.prompts/31_E2E.md)

"""Tests README"""

# Frontend Tests

Tests for the frontend are organized by type and location.

## Structure

```
__tests__/
├── lib/
│   ├── hooks/
│   │   └── useAuth.test.ts
│   └── services.test.ts
├── integration/
│   └── auth.integration.test.ts
├── fixtures.ts
└── README.md (this file)
```

## Running Tests

```bash
# Run all tests
pnpm test

# Run in watch mode
pnpm test -- --watch

# Run with coverage
pnpm test -- --coverage

# Run specific test file
pnpm test -- useAuth.test.ts

# Run integration tests only
pnpm test -- __tests__/integration
```

## Test Organization

### Unit Tests (`lib/`)

Test individual functions, services, and hooks in isolation with mocks.

- `services.test.ts` - Test API service layer
- `hooks/useAuth.test.ts` - Test authentication hook

### Integration Tests (`integration/`)

Test how multiple parts work together. These might use a test server.

- `auth.integration.test.ts` - Full authentication flow

### Fixtures (`fixtures.ts`)

Reusable mock data for consistent test setup across test files.

## Writing New Tests

1. Import fixtures for mock data
2. Mock external dependencies (fetch, router, etc.)
3. Use React Testing Library for component/hook testing
4. Follow Arrange-Act-Assert pattern

```typescript
it('should do something', async () => {
  // Arrange - setup
  const mockData = mockPet
  jest.mock('service')

  // Act - execute
  const result = await someFunction(mockData)

  // Assert - verify
  expect(result).toEqual(expected)
})
```

## Coverage Goals

- Services: 80%+
- Hooks: 75%+
- Components: 60%+

## Debugging Tests

```bash
# Run single test in debug mode
node --inspect-brk node_modules/.bin/jest --runInBand test_file.ts

# Run with detailed output
pnpm test -- --verbose
```

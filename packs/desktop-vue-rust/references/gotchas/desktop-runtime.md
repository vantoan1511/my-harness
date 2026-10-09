# Gotcha: Desktop Runtime & IPC Pitfalls

## 1. Direct Import Prohibition
**Trap**: Importing native runtime libraries (`@neutralinojs/lib`, `@tauri-apps/api`) directly into Vue SFCs or composables.
**Impact**: Breaks unit tests running in Node.js (which lacks the native desktop runtime environment). Tight coupling makes mocking and refactoring difficult.
**Solution**: Always route native capabilities through centralized services in `@/services/*` (e.g. `@/services/nativeService`). Mock only the service in tests.

## 2. Idle Connection Drops
**Trap**: The local IPC socket or WebSocket can disconnect when the computer sleeps or when the process is backgrounded for extended periods.
**Solution**: Implement heartbeat ping/pong in the backend engine and an automatic reconnect listener in the frontend service with exponential backoff.

## 3. Asynchronous IPC Timeouts
**Trap**: IPC calls hang indefinitely if the backend crashes or deadlocks.
**Solution**: Always wrap IPC requests in an async timeout helper (`withTimeout(promise, 5000)`). Provide fallback UI state rather than freezing indefinitely.

# Gotchas: Neutralinojs Runtime & IPC Invariants

---

## 1. Direct Imports of `@neutralinojs/lib`
- **NEVER** import `@neutralinojs/lib` inside Vue components, views, or composables (`src/components/`, `src/views/`, `src/composables/`).
- **Why**: Direct imports break component testability, violate boundary separation, and cause crashes in Node.js test runners where the Neutralino WebSocket is not present.
- **Rule**: Always import via `@/services/nativeService` or dedicated domain services in `src/services/*`.

---

## 2. Asynchronous Native Storage Timeouts
- Calling `Neutralino.storage.getData(key)` makes an IPC request to Neutralino's storage driver.
- On Windows or slow disk environments, if storage hangs or is corrupt, the entire UI initialization can block indefinitely.
- **Rule**: Always use the `withTimeout` wrapper ([src/utils/async.ts](file:///d:/Projects/orbit/src/utils/async.ts)) with `DEFAULT_STORAGE_TIMEOUT_MS` (1500ms) to fall back safely to defaults.

---

## 3. Background Process Management & Port Forwards
- Port forwards spawn background `kubectl` processes managed by the Rust backend engine.
- On exit or stop, processes must be killed cleanly.
- Windows process termination requires handling process trees (`taskkill /F /T /PID <pid>`) so orphaned child connections don't hold ports open.

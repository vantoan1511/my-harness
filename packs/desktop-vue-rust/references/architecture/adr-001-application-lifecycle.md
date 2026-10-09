# ADR-001: Application Startup Lifecycle & IPC Handshake Invariants

## Context

Desktop applications combining a native Rust backend with a web frontend communicate over local IPC (e.g. WebSocket or local sockets). When the app launches, the runtime spawns the backend process, which connects back to the frontend/runtime to establish bidirectional event streams.

## Invariant 1: Synchronous Mounting Before `init()`

In `src/main.ts`:
```typescript
// 1. Mount Vue app synchronously FIRST
app.mount('#app')

// 2. Initialize desktop runtime SECOND
init()

// 3. Hydrate persistent stores asynchronously in the background
void Promise.allSettled([
  initTheme(),
  tableFilterStore.init(),
  userPreferencesStore.init(),
])
```

### Why?
- `App.vue` and root views register event listeners during their `onMounted()` hooks:
  - `events.on(AppEvents.EngineConnected)`
  - `events.on(AppEvents.InitialStateUpdated)`
- If `init()` runs before `app.mount('#app')`, or if `app.mount()` is delayed by top-level `await` promises, the backend engine connects and broadcasts initial state *before* frontend listeners are mounted.
- **Symptom if violated**: Initial state is lost on boot, UI hangs on loading skeleton, or a false "engine connection timeout" dialog appears.

## Invariant 2: Asynchronous Persistent Store Hydration
- Never `await` persistent store hydration before `app.mount('#app')`.
- All storage hydration must run in the background using `void Promise.allSettled(...)`.
- Stores must provide sensible default reactive fallbacks immediately so initial views can render without blocking.

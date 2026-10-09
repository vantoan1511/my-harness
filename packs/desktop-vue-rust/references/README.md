# Desktop Vue + Rust Knowledge Base & Reference Catalog

This directory contains architectural decisions (ADRs), canonical implementation recipes, and desktop runtime gotchas for Vue 3 + PrimeVue 4 + Rust desktop applications.

---

## Catalog Index

### 1. Architecture Decision Records (`architecture/`)
- [adr-001-application-lifecycle.md](architecture/adr-001-application-lifecycle.md) — Synchronous `app.mount()` before `init()`, IPC event handshake, and async store hydration.
- [adr-002-configuration-system.md](architecture/adr-002-configuration-system.md) — Backend-controlled settings model, `~/.<app_name>/config.json`, and dynamic UI rendering.
- [adr-003-storage-and-state.md](architecture/adr-003-storage-and-state.md) — Storage tiers: Native desktop filesystem vs Pinia reactive memory vs browser `localStorage` prohibition.

### 2. Canonical Recipes (`recipes/`)
- [canonical-data-view.md](recipes/canonical-data-view.md) — How to build a standard desktop entity view (ViewLayout, DataTable, search toolbar, DetailsDrawer).
- [canonical-primevue-controls.md](recipes/canonical-primevue-controls.md) — PrimeVue v4 / Nora controls, forms, modal dialogs, and `v-tooltip` directives.
- [canonical-node-test.md](recipes/canonical-node-test.md) — Node native test runner (`node:test`, `node:assert/strict`) starter templates for frontend.
- [canonical-rust-test.md](recipes/canonical-rust-test.md) — Rust `cargo test` unit tests and IPC contract serialization tests.

### 3. Hard-Earned Gotchas (`gotchas/`)
- [desktop-runtime.md](gotchas/desktop-runtime.md) — Prohibiting direct runtime imports in UI, idle timeouts, IPC error serialization.
- [primevue-quirks.md](gotchas/primevue-quirks.md) — Tooltip directives vs native title, flat DataTable rules, PassThrough scope.
- [tailwind-v4.md](gotchas/tailwind-v4.md) — Tailwind v4 CSS-first conventions, trailing exclamation mark (`p-0!`), CSS variable utilities.

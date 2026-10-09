# Desktop Vue + Rust Application Pack

A comprehensive, production-grade project skeleton for lightweight desktop applications built with:
- **Rust backend** for privileged operations, OS/filesystem access, caching, and business logic
- **Desktop runtime** (Neutralinojs or Tauri) connecting backend and webview over IPC
- **Vue 3 + TypeScript + Vite** frontend
- **Tailwind CSS v4** utility styling
- **PrimeVue v4 (Nora theme)** component and design system

This pack extracts the complete architectural skeleton of Orbit **without** any of the Orbit- or Kubernetes-specific domain logic, providing the missing utilities, lifecycle rules, configuration system, and recipes.

---

## What's Included

### 1. Architectural Rules (`rules/`)
- `desktop-configuration-system.md` — Backend-owned, system-defined configuration model across IPC with dynamic PrimeVue form rendering.
- `desktop-design-system.md` — Technical, compact, information-dense desktop UI tokens, typography, and borderless grouping.
- `desktop-frontend-engineering.md` — Startup sequence (synchronous app mount before runtime init, async store hydration), centralized service boundaries.
- `primevue-nora-standards.md` — Single source of truth for PrimeVue customizations, avoiding style drift, `v-tooltip` enforcement.

### 2. Specialized Desktop Skills (`skills/`)
- `primevue-customization` — Presets, design tokens, PassThrough, styling scope decision tree.
- `desktop-ui-implementation` — End-to-end implementation workflow for desktop UI screens, forms, and dialogs.
- `desktop-ui-review` — Consistency review gate for desktop UI and PrimeVue theming.
- `data-view-page` — Standard desktop entity view pattern (DataTable, filter toolbar, pagination, actions, DetailsDrawer).

### 3. Architecture Decision Records (`references/architecture/`)
- `adr-001-application-lifecycle.md` — Synchronous mounting before runtime `init()`, IPC event race condition avoidance.
- `adr-002-configuration-system.md` — Why configuration definitions belong in Rust with lean disk overrides in `~/.<app_name>/config.json`.
- `adr-003-storage-and-state.md` — Three-tier storage hierarchy and browser `localStorage` prohibition.

### 4. Canonical Recipes (`references/recipes/`)
- `canonical-data-view.md` — Complete starter template for ViewLayout, filter toolbar, flat PrimeVue DataTable, and side DetailsDrawer.
- `canonical-primevue-controls.md` — PrimeVue v4 / Nora controls, forms, modal dialogs, and `v-tooltip` directives.
- `canonical-node-test.md` — Native Node 24 test runner templates for utilities and Pinia stores.
- `canonical-rust-test.md` — Rust unit tests and IPC request/response serialization tests.

### 5. Hard-Earned Gotchas (`references/gotchas/`)
- `desktop-runtime.md` — Neutralino/Tauri runtime gotchas, direct import prohibitions, idle timeouts.
- `primevue-quirks.md` — Flat DataTable rules, PassThrough specificity, tooltip directives.
- `tailwind-v4.md` — Tailwind v4 CSS-first utilities, trailing exclamation syntax, CSS variables.

### 6. Pre-Configured Guardrails (`harness.config.json`)
- Banned direct runtime imports (`@neutralinojs/lib`, `@tauri-apps/api`) in UI.
- Banned Rust `.unwrap()`, `.expect()`, `panic!` in production engine code.
- Banned raw HTML `<button>`, `<input>`, `<select>` in Vue templates.
- Banned native HTML `title="..."` attributes.
- Banned hardcoded hex colors in stylesheets.

---

## Installation into a Project

```bash
# Initialize a new project with this pack directly:
python d:/Projects/my-harness/harness.py init /path/to/my-project --pack desktop-vue-rust

# Or add it to an existing project:
python d:/Projects/my-harness/harness.py add-pack desktop-vue-rust /path/to/my-project
```

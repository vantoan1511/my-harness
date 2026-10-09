# Desktop Frontend Engineering

## Scope

These rules apply to lightweight desktop applications built with Vue 3, TypeScript, Tailwind CSS v4, PrimeVue v4, and a desktop runtime (such as Neutralinojs or Tauri).

## General Principles

Do not optimize for the shortest path if it creates:
- duplicated components
- duplicated styles
- inconsistent APIs
- page-specific hacks
- unnecessary abstractions
- new patterns that already exist elsewhere

Prefer consistency and maintainability over implementation speed.

---

## Application Lifecycle & Startup Sequence

### 1. Synchronous App Mounting Before `init()`
`app.mount('#app')` in `src/main.ts` **MUST** execute synchronously before the desktop runtime's `init()` is called.

**Why**: Root components and views register listeners for core IPC broadcast events (e.g. `engineConnected`, initial state updates) during their `onMounted()` hooks. If `init()` runs before `app.mount('#app')` or if mounting is delayed by asynchronous promises, the backend engine connects and broadcasts initial state events before frontend listeners are active. This causes lost state and triggers false engine connection timeouts.

### 2. Asynchronous Storage & Store Hydration
Hydrate persistent stores and settings (e.g. theme, table filters, user preferences) asynchronously in the background (`void Promise.allSettled(...)`) **AFTER** `app.mount('#app')` and `init()`. Never block `app.mount('#app')` with top-level `await` promises.

---

## Native & IPC Boundaries

- **Never import desktop runtime libraries directly** (such as `@neutralinojs/lib` or `@tauri-apps/api`) inside Vue components, views, or composables.
- Always access OS, filesystem, window, events, storage, and IPC functions via centralized service wrappers in `@/services/*` (e.g. `@/services/nativeService`).
- Components must remain purely representational and delegate system interactions to services or Pinia stores.

---

## PrimeVue Components & Directives

- Use PrimeVue v4 components and directives for all controls and interactions (`Button`, `InputText`, `InputNumber`, `Select`, `ToggleSwitch`, `DataTable`, `Dialog`).
- **Never use raw HTML form controls** (`<button>`, `<input>`, `<select>`, `<textarea>`) in `.vue` templates.
- **Always use PrimeVue's `v-tooltip` directive** (e.g. `v-tooltip.top="'...'"` or `v-tooltip="'...'"`). Never use native HTML `title` attributes for tooltips or descriptive hover text.

---

## Styling & Design Tokens

Prefer, in order:
1. existing PrimeVue/Nora theme configuration (`definePreset`)
2. existing application design tokens (`base.css` CSS variables)
3. shared component styles
4. existing utility classes (Tailwind v4)
5. component-scoped styles for genuinely local layout

Do not hard-code hex color codes when an existing token exists (`var(--accent)`, `var(--border)`, `var(--bg-card)`).

---

## Verification

After implementation:
- Inspect changed and analogous components
- Ensure zero direct runtime imports in views/components
- Run pre-flight verification: `python .agents/scripts/verify_shift_left.py --changed`
- Run type checking and linter

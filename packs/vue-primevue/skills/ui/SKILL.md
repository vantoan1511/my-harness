---
name: ui
description: Guidelines and best practices for developing user interfaces using PrimeVue 4 in combination with Vue 3, Tailwind CSS v4, and TypeScript.
---

# PrimeVue UI Integration & Styling Patterns

This skill defines the development guidelines, component standards, and styling patterns for applications built using **PrimeVue 4**, **Vue 3**, and **Tailwind CSS v4**.

## When to Activate

Activate this skill when:
- **UI Implementation**: Building or styling interfaces using **PrimeVue 4** components within **Vue 3**.
- **Styling & Theming**: Applying **Tailwind CSS v4** utility classes, configuring custom presets (`definePreset`), or managing dark mode coordination (`darkModeSelector`).
- **Data Display**: Implementing complex data grids (`DataTable`), lists (`DataView`), charts (`Chart`, `MeterGroup`), or hierarchical views (`Tree`, `TreeTable`, `OrganizationChart`).
- **Forms & Inputs**: Creating accessible forms using advanced inputs (`Select`, `DatePicker`, `AutoComplete`), label wrappers (`FloatLabel`, `IftaLabel`), and validation states (`invalid`).
- **Navigation & Layout**: Organizing content with containers (`Card`, `Panel`, `Tabs`), navigation systems (`Menubar`, `Breadcrumb`, `Dock`), or wizard flows (`Stepper`).
- **Interactivity & Feedback**: Adding overlays (`Dialog`, `Popover`), feedback components (`Toast`, `Message`), or animations (`v-ripple`, `v-animateonscroll`, `v-styleclass`).
- **Performance**: Using virtualization (`VirtualScroller`) or deferred loading (`DeferredContent`) for large datasets or heavy media.

## Scope Boundaries

- **In-Scope**: Vue 3 + PrimeVue 4 + Tailwind CSS v4 integration, Pass-Through (`pt`) attributes, design tokens, and semantic styling.
- **Out-of-Scope**: Pure backend logic, generic React/Next.js UI patterns (use `frontend-patterns`), or CSS rules unrelated to the PrimeVue/Tailwind ecosystem.

---

## 📚 Reference Guides

Detailed implementation patterns and configurations are organized into specialized references:

### 1. [Setup & Global Configuration](references/setup-config.md)
Guidelines for Vue 3 module options, global behavioral settings (ripple, zIndex), and Dark Mode coordination with Tailwind CSS.

### 2. [Theming, Styling & Tailwind Integration](references/theming-styling.md)
How to define custom presets, use dynamic theming utilities, integrate Tailwind CSS v4 semantic tokens, and use Pass-Through (`pt`) attributes for surgical styling.

### 3. [Input Components & Form Patterns](references/forms-inputs.md)
Comprehensive patterns for PrimeVue 4 input components, highlighting `variant` and `fluid` props, label wrappers, and form validation states.

### 4. [Animation Utilities](references/animations.md)
Core directives (`v-ripple`, `v-animateonscroll`) and Tailwind CSS v4 animation utilities for interactive feedback and transitions.

### 5. [Data Tables & Data Display](references/data-tables.md)
Categorized patterns for tabular data, hierarchical views, media collections, and visualization charts using PrimeVue 4.

### 6. [Layout & Container Patterns](references/layout-containers.md)
Implementation patterns for structural containers, navigation systems, and status indicators like Cards, Tabs, Menubar, and Avatars.

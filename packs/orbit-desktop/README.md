# Orbit Desktop Pack for my-harness

This pack encapsulates Orbit's domain rules, custom skills, and architectural recipes.

## Contents

- **Rules**:
  - `orbit-configuration-system.md` — Unified Configuration model and storage tiers.
  - `orbit-design-system.md` — Noir / technical desktop visual guidelines.
  - `orbit-frontend-engineering.md` — Application lifecycle, sync mount, async hydration.
  - `orbit-primevue.md` — Nora theme single-source-of-truth rules.
- **Skills**:
  - `orbit-primevue-customization` — Presets, PassThrough, styling scope.
  - `orbit-resource-page` — Canonical Kubernetes resource views, tables, and drawers.
  - `orbit-ui-implementation` — Consistent UI implementation workflows.
  - `orbit-ui-review` — Visual consistency and PrimeVue review gate.
  - `winget` — WinGet package publishing and fork synchronization.
- **References**:
  - ADRs (Application lifecycle, configuration, storage tiers)
  - Gotchas (Neutralino runtime, PrimeVue quirks, Tailwind v4)
  - Canonical Recipes (Resource page, PrimeVue controls)

## Installation into a Project

```bash
python /path/to/my-harness/harness.py add-pack orbit-desktop
```

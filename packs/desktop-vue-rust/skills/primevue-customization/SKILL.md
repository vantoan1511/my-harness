---
name: primevue-customization
description: Customizes PrimeVue v4 components using the Nora theme and shared styling strategy. Use when changing PrimeVue appearance, theme tokens, PassThrough configuration, DataTable density, forms, buttons, tabs, dialogs, or overlays.
---

# PrimeVue Customization

## Core Rule

PrimeVue component styling is shared application infrastructure. Never treat a PrimeVue customization as an isolated page-level decision without first checking the existing canonical implementation.

## Workflow

### Step 1: Locate Canonical Configuration
Search the repository for:
- PrimeVue initialization in `src/main.ts`
- Nora preset configuration and `definePreset`
- Theme tokens (`components`, `semantic`, `primitive`, `pt`, `dt`)
- Shared component wrappers and styling

### Step 2: Determine Scope
Use this decision tree:
- **Global visual language**: Update PrimeVue/Nora theme preset (`definePreset`) or shared design token.
- **Shared application behavior**: Update or create shared component wrapper.
- **Unique page layout**: Page-local layout styling.
- **Exceptional one-off**: Local styling with documented rationale.

### Step 3: Avoid Style Drift
Never introduce differing heights or radii for the same component across multiple views. If two views need a Button or InputText, they must share the canonical sizing.

### Step 4: PassThrough & Token Configuration
Prefer configuring PrimeVue through supported PassThrough (`pt`) props or design tokens (`dt`) over brittle CSS class selectors.

### Step 5: Check Impact
After changing shared PrimeVue styling:
- Inspect usages across at least one table-heavy screen and one form-heavy screen.
- Verify that changes did not unintentionally break existing views.

## Final Checklist
- [ ] Existing PrimeVue configuration inspected
- [ ] Nora preset token overrides inspected
- [ ] Correct scope chosen (theme vs shared wrapper vs local)
- [ ] No duplicate shared CSS selectors introduced
- [ ] Tooltip directives (`v-tooltip`) used consistently

---
name: desktop-ui-implementation
description: Implements or modifies desktop Vue UI using PrimeVue v4 and Nora theme while preserving shared component patterns, visual consistency, and technical desktop design. Use for UI screens, components, layouts, forms, tables, dialogs, and navigation.
---

# Desktop UI Implementation

## Goal

Build UI that feels native to the desktop application, with compact information density, clean hierarchy, and strict adherence to the design system.

## Required Workflow

### 1. Understand Before Editing
Before writing code:
- Inspect the target page and neighboring components.
- Inspect the PrimeVue configuration and Nora preset (`src/theme/appTheme.ts`).
- Search for existing implementations of every control you intend to add.

### 2. Identify the Reuse Path
For each element:
- Existing shared component → reuse
- Existing PrimeVue component → reuse
- Existing pattern that needs a slight parameter → generalize
- Genuinely new interaction → design reusable component

### 3. Decide Styling Scope
Always prefer:
1. PrimeVue/Nora theme preset (`definePreset`)
2. Shared component wrapper
3. Shared CSS custom property token (`base.css`)
4. Page-local layout styling

### 4. Implement
- Favor composition over duplication.
- Avoid copied CSS blocks, duplicate PrimeVue overrides, or hard-coded dimensions.
- Use Lucide icons with consistent sizes (`w-4 h-4` for toolbars, `w-3.5 h-3.5` for drawer headers).

### 5. Shift-Left Pre-Flight Verification
Run the automated pre-flight scanner on modified files:
```bash
python .agents/scripts/verify_shift_left.py --changed
```
Ensure:
- Zero raw HTML `<button>`, `<input>`, `<select>` tags in `.vue` templates.
- Zero native HTML `title="..."` attributes (must use PrimeVue `v-tooltip`).
- Zero hardcoded hex colors in styles (must use tokens from `base.css`).
- Zero direct native runtime imports in UI components.

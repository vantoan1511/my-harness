# PrimeVue v4 / Nora Theme Standards

## Purpose

Treat PrimeVue/Nora as a shared design system, not merely a component library. Prevent PrimeVue customizations from drifting across the application.

## Single Source of Truth

There must be one canonical styling strategy for each PrimeVue component family:
- Button appearance (height, radius, variants)
- Input height and radius (`variant="filled"`)
- Select / Dropdown styling
- Tab styling
- Dialog structure and radius
- DataTable row density
- Tooltip appearance and directive usage (`v-tooltip`)

Before modifying a PrimeVue component, locate the existing canonical configuration.

---

## Centralize Broad Customizations

If a customization applies to all or most instances of a PrimeVue component, put it in the shared theme configuration (`definePreset`) or shared component styling.

**Do NOT implement broad visual changes in a page component.**

Examples of changes that belong centrally:
- Button height and corner radius
- Input field height and border treatment
- DataTable row density and padding
- Dialog radius and header styling
- Common focus states

---

## Local Customization Constraints

Local styling is acceptable only when the requirement is genuinely contextual.
- A local customization **MUST NOT** silently create a new reusable visual variant.
- If the same local customization appears in another location, consolidate it into the canonical shared implementation.
- Do NOT create duplicate local classes (`.my-button`, `.overview-button`) when both should follow the shared Button style.

---

## Theming Workflow

When a PrimeVue component needs a visual change:
1. Inspect the installed PrimeVue setup and `theme/appTheme.ts`.
2. Inspect the Nora preset and existing `definePreset` token overrides.
3. Search for `pt`, `dt`, CSS selectors, and wrappers already customizing the component.
4. Decide whether the requirement is global or contextual.
5. Apply the customization at the narrowest correct shared level.

---

## Tooltip Directives

**Always use PrimeVue's `v-tooltip` directive** (e.g. `v-tooltip.top="'...'"` or `v-tooltip="'...'"`). Never use native HTML `title` attributes for tooltips or descriptive hints.

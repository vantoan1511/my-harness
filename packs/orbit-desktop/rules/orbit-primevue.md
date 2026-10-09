---
trigger: always_on
---

# Orbit PrimeVue v4 / Nora Rules

## Purpose

This rule prevents PrimeVue customizations from drifting across Orbit.

Orbit uses PrimeVue v4 with the Nora theme. Treat PrimeVue/Nora as a shared design system, not merely a component library.

## Single Source of Truth

There must be one canonical styling strategy for each PrimeVue component family.

Examples:

- Button appearance
- Input height and radius
- Select/Dropdown appearance
- Tab styling
- Dialog structure
- DataTable density
- Paginator controls
- Tag/Badge appearance
- Menu items
- Tooltip appearance and directive usage (`v-tooltip`)

Before modifying a PrimeVue component, locate the existing canonical configuration.

## Centralize Broad Customizations

If a customization applies to all or most instances of a PrimeVue component, put it in the shared theme configuration or shared component styling.

Do NOT implement broad visual changes in a page component.

Examples of changes that normally belong centrally:

- Button height
- Button radius
- Input height
- Input border treatment
- DataTable row density
- Tab typography
- Dialog radius
- Dropdown spacing
- common focus states

## Local Customization

Local styling is acceptable only when the requirement is genuinely contextual.

A local customization MUST NOT silently create a new reusable visual variant.

If the same local customization appears in another location, consolidate it into the canonical shared implementation.

## No Duplicate Variants

Do not create:

- `.my-button`
- `.deployment-button`
- `.overview-button`

when all three are actually attempts to make the same PrimeVue Button look the same.

Instead, fix the shared Button customization.

Similarly, do not create multiple local overrides for the same PrimeVue selector.

## Theme Configuration First

When a PrimeVue component needs a visual change:

1. Inspect the PrimeVue v4 setup.
2. Inspect the Nora preset and existing `definePreset`/theme configuration.
3. Inspect existing `components` and semantic token overrides.
4. Search for `pt`, `dt`, CSS selectors, classes, and wrappers already customizing the component.
5. Decide whether the requirement is global or contextual.
6. Apply the customization at the narrowest correct shared level.

Do not guess the PrimeVue theming API. Inspect the project's installed PrimeVue version and current configuration first.

## PassThrough / Component APIs

Use PrimeVue's supported APIs and the project's established pattern.

Do not introduce a new PassThrough convention in one page if the project already has a shared convention.

If a PassThrough customization becomes reusable, move it to the shared component/theme layer.

## Tooltips Directive

Always use PrimeVue's `v-tooltip` directive (e.g. `v-tooltip.top="'...'"` or `v-tooltip="'...'"`). Never use native HTML `title` attributes for tooltips or descriptive hints.

## Verification

After changing a PrimeVue component:

1. Search all usages of that component.
2. Check at least two representative screens when possible.
3. Verify that the customization did not unintentionally change another screen.
4. Confirm that there is still one canonical visual treatment.

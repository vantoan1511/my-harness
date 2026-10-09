# Vue 3 + PrimeVue 4 Standards

## Principles
1. Always use PrimeVue v4 components (`Button`, `InputText`, `Select`, `DataTable`) instead of raw HTML controls.
2. Always use `v-tooltip` directive for tooltips, never native `title="..."` attributes.
3. Centralize theme styling in presets or shared wrappers to prevent style drift across screens.
4. Prefer Tailwind CSS utility classes aligned with design tokens.

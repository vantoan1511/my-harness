---
name: data-view-page
description: Builds desktop data views using established table patterns, PrimeVue v4 Nora components, filters, pagination, status indicators, and contextual action drawers. Use when adding or modifying data views, entity tables, or management screens.
---

# Desktop Data View Page

## Goal

Create new data management and entity views by extending the standard desktop data view pattern instead of inventing arbitrary layouts.

## Standard Hierarchy

```
┌────────────────────────────────────────────────────────┐
│ Page Title (ViewLayout)                   [Actions]    │
├────────────────────────────────────────────────────────┤
│ [Search / Filters Toolbar]                             │
├────────────────────────────────────────────────────────┤
│ DataTable (Flat, borderless container, subtle headers) │
│ - Row 1                                                │
│ - Row 2                                                │
├────────────────────────────────────────────────────────┤
│ Paginator (Compact, subtle controls)                   │
└────────────────────────────────────────────────────────┘
                       ▲
            [Side Details Drawer] (Progressive disclosure)
```

## Structure & Guidelines

### 1. View Layout
- Use the shared `ViewLayout` component for consistent page padding (`p-8`), title typography (`text-xl font-bold`), and top-level action button placement.

### 2. Filter Toolbar
- Compact layout (`gap-3` or `gap-4`).
- Use PrimeVue inputs with `variant="filled"` for flush, borderless integration.
- Size inputs consistently (`size="small"`, `text-sm`).

### 3. Data Table
- Use PrimeVue `DataTable` with flat, single-container styling (`border border-(--border) rounded-lg overflow-hidden bg-(--bg-card)`).
- Never wrap the table in an elevated `<Card>` component.
- Ensure uniform row heights and density.
- Subtle header row styling (`bg-surface-100` / `bg-surface-900`) with a crisp bottom separator.
- Right-align numeric columns (counts, size, metrics).
- Provide loading skeletons (`Skeleton`) and empty states (`EmptyState`).

### 4. Status Badges
- Reuse semantic status badges for state presentation (`--success`, `--warning`, `--danger`, `--info`).
- Never use arbitrary raw color classes for state indicators.

### 5. Contextual Actions & Details Drawer
- Row context menu or end-of-row actions button with `v-tooltip`.
- Slide-out details drawer (`Drawer`) for inspecting full entity metadata without leaving the page.

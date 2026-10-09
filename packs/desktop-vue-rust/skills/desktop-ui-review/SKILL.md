---
name: desktop-ui-review
description: Reviews desktop UI changes for visual consistency, PrimeVue/Nora adherence, component reuse, styling deduplication, and technical desktop design. Use after implementing or modifying UI.
---

# Desktop UI Review

## Purpose

This is a consistency and quality review gate. The primary question is:

> Does this change look and feel like it belongs to a cohesive, professional technical desktop application?

## Review Procedure

### 1. Compare With Analogous Screens
Compare the changed view against existing application screens:
- Page title & toolbar layout
- Density and row heights in tables
- Spacing and borderless grouping
- Semantic colors vs raw decorative colors
- Loading, empty, and error states

### 2. PrimeVue Consistency
For every PrimeVue component touched:
- Does it match canonical styling?
- Does it use `v-tooltip` instead of native `title="..."`?
- Did it accidentally introduce an unnecessary local visual variant?

### 3. Search for Duplication
Search the codebase for:
- Duplicate PrimeVue CSS selectors
- Repeated custom dimensions
- Duplicated utility wrappers

### 4. Evaluate Design Character
Reject changes that make the UI:
- SaaS-marketing like (excessive whitespace, decorative cards, large radii)
- Inconsistently spaced or styled
- Lacking clear typographic hierarchy

## Verdict & Action
- **Blocker**: Conflicting global PrimeVue styles, raw HTML interactive elements, direct runtime imports in UI.
- **Important**: Inconsistent row density, unnecessary local overrides, missing tooltip directives.
- **Minor**: Minor alignment or spacing adjustments.

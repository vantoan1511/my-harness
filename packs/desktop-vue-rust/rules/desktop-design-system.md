# Desktop Design System

## Visual Philosophy

The desktop visual language is **technical, compact, information-dense, and minimalist**. It must feel like a professional developer IDE or infrastructure console — not a consumer SaaS marketing dashboard.

The canonical source of truth for visual decisions:
- `src/assets/base.css` — design tokens (colors, shadows, z-index, typography)
- `src/assets/main.css` — global base styles, scrollbar, page transitions
- `src/theme/appTheme.ts` — PrimeVue Nora preset customization

---

## UI Principles

### Information Density
Prefer useful information over decorative whitespace while preserving scanability and clear hierarchy.

### Hierarchy
Establish hierarchy in this order:
1. Typography
2. Spacing
3. Surface contrast
4. Semantic color
5. Borders only when structural

Do not use every mechanism simultaneously for the same element.

### Component Grouping Without Borders
When spacing alone is insufficient to distinguish complex component groups, use these **borderless grouping techniques**:
1. **Proportional Ratio Spacing (1:3 Rhythm)**:
   - Intra-item gap (label to input): tight (`gap-1.5` / `gap-2`).
   - Inter-item gap (controls in same sub-group): medium (`gap-3` / `gap-4`).
   - Inter-group gap (between major sections): wide (`gap-8` / `gap-10`).
2. **Subtle Surface Tone Shifts (Zonal Backgrounds)**:
   - Use flat, borderless background fills (`bg-(--bg-hover)/40`, `bg-surface-50`, `bg-surface-900`) with soft radii to group related controls without stroke lines.
3. **Two-Column / Asymmetric Layout**:
   - Pair an informative left header column (~25–30% width: title, description, icon) with interactive controls on the right column (~70–75% width).
4. **Typographic Rhythm & Eyebrow Headers**:
   - Use small, uppercase tracked overlines (`text-xs font-semibold tracking-wider text-muted-color`).
5. **Grouped Inset Wells**:
   - Group repeatable items (key-value pairs, lists) in borderless inset wells with unified inner padding.

---

## Typography

| Role | Font family | Token |
|---|---|---|
| UI text | Inter → system-ui | `--font-ui` |
| Monospace | Geist Mono → JetBrains Mono → Fira Code | `--font-mono` |

### Text Scale
| Usage | Size class | Weight |
|---|---|---|
| Page/section title | `text-xl` | `font-bold` |
| Card/drawer title | `text-lg` | `font-bold` |
| Table headers, labels | `text-sm` | `font-medium` or `font-semibold` |
| Table cell content | `text-xs` | `font-normal` or `font-medium` |
| Footer / status bar | `text-[11px]` | `font-medium` |

Never use type sizes above `text-xl` for data-density screens.

---

## Color & Design Tokens

Use CSS custom properties from `base.css`. Never hard-code hex values in component styles.

### Core Tokens
- Brand / Accent: `--accent`, `--accent-hover`, `--accent-active`, `--accent-soft`
- Backgrounds: `--bg-app`, `--bg-sidebar`, `--bg-panel`, `--bg-card`, `--bg-hover`, `--bg-active`
- Text: `--text-primary`, `--text-secondary`, `--text-muted`, `--text-disabled`
- Borders: `--border`, `--border-strong`
- Semantic Status: `--success`, `--warning`, `--danger`, `--info` (each paired with a `-soft` background variant)

---

## Data Tables & Containers

- Use a flat, single-container design (`border border-(--border) rounded-lg overflow-hidden bg-(--bg-card)`) without elevated `<Card>` wrappers.
- Table headers use subtle tonal background shifts with a crisp bottom separator.
- Data rows use compact heights, subtle separators, and responsive hover states (`hover:bg-(--bg-hover)`).
- Right-align numeric and metric columns.

---

## UI Anti-Patterns

Never use:
- Raw `<button>`, `<input>`, `<select>` when equivalent PrimeVue components exist.
- Hardcoded hex color values outside of `base.css`.
- Arbitrary dimension classes: `w-[140px]`, `gap-[18px]` (use nearest Tailwind step or CSS variables).
- Borders or `<hr>` lines used purely to group form fields instead of natural spacing (`gap-6`, `gap-8`).
- Gradients or decorative box-shadows.
- Native HTML `title="..."` attributes (always use PrimeVue `v-tooltip`).
- Direct native runtime imports in UI components.

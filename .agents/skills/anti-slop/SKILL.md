---
name: anti-slop
description: Enforces senior-level code craft and eliminates AI code slop through upfront invariant locking, strict negative constraints, and an automated self-audit & rewrite loop. Use when implementing features/fixes cleanly without slop, or when auditing and rewriting AI-generated diffs.
---

# Anti-Slop Code Craft

Write and refine code the way an opinionated senior engineer maintains a production codebase: optimize for **long-term readability, minimal surface area, and native repo fit** — not just "making the current prompt pass."

> **Core Principle:** Passing tests is the floor, not the bar. If a diff adds unnecessary branches, defensive bloat, speculative abstractions, or parallel logic, it is slop — rewrite it before finishing.

---

## Operating Modes

Determine mode from the user's request:

- **Author Mode** *(default when implementing a feature, bug fix, or refactor)*: Run **Phases 1 → 4** end-to-end.
- **Audit & Rewrite Mode** *(when asked to clean up slop, or invoked on an existing diff / file path)*: Skip directly to **Phase 4 (Self-Audit & Auto-Fix Loop)** against `git diff` or the specified target files.

---

## Phase 1 — Codebase Grounding & Exemplar Lock

Before writing a single line of code:

1. **Pick 1–2 Exemplar Files:** Locate the cleanest existing file(s) in the same layer/domain of the repo. Mirror their naming, error handling, layering, and idioms exactly.
2. **Check for Reuse & Deletion First:** Search for existing helpers, domain types, and patterns. Explicitly ask:
   - *Can an existing function/module be extended cleanly instead of adding a new one?*
   - *Can old/dead code be deleted or simplified so the net complexity stays flat or drops?*
3. **Reject Additive Bias:** Do not assume every task means adding more code. Prefer editing or replacing the root structure over bolting on flags, wrappers, or special-case branches.

---

## Phase 2 — Contract & Invariant Lock

Briefly lock the mental model before typing (in working notes or a short plan for non-trivial changes):

- **Trust Boundaries:** Identify where untrusted external input enters (HTTP/IPC/CLI/FS/env). Validate strictly at that boundary; trust typed contracts everywhere inside.
- **Data Shapes & Invariants:** State the exact types and guarantees callers and callees rely on.
- **Failure Mode:** Define how errors propagate (fail fast with context — never silent fallback).
- **Minimal File Footprint:** List the smallest set of files that actually need to change.

---

## Phase 3 — Implement Under Anti-Slop Negative Constraints

Enforce these hard prohibitions while writing code:

1. **No Additive Band-Aids:** Do not stack `if (specialCase)` patches or boolean mode flags onto a flawed design. Fix the underlying abstraction or control flow.
2. **No Speculative Abstractions:** Do not create single-use helpers, wrapper classes, factories, or interfaces "for future extensibility." Introduce an abstraction only when there are **≥ 2 concrete callers** or a real architectural/testing boundary.
3. **No Defensive Bloat Inside Trust Boundaries:** Do not add redundant `if (!x) return null`, `x ?? ""`, or extra runtime guards for invariants already guaranteed by the type system or upstream boundary validation.
4. **No Silent Error Swallowing:** Never wrap code in `try/catch` just to log and return a dummy/empty value unless the domain contract explicitly requires graceful degradation. Propagate or wrap errors with actionable context.
5. **No Type-System Escapes:** Never use `any`, unsafe casts (`as unknown as T`), `@ts-ignore`, or `# type: ignore` to silence compiler complaints. Fix the type contract instead.
6. **No Narrator Comments:** Never write comments that restate what the code already says (`// loop through items`, `// return result`). Comment only non-obvious *why*, invariants, edge-case constraints, or trade-offs.
7. **No Parallel Implementations:** Never write a slightly different copy of an existing utility, hook, service, or UI control. Reuse or generalize the canonical one.
8. **No Tangled Control Flow:** Flatten nested `if/else` chains (> 3 levels) with early returns and guard clauses. Avoid nested ternaries and 50+ line god functions.

---

## Phase 4 — Self-Audit & Auto-Fix Loop (Max 2 Passes)

After implementation passes tests/typecheck (or immediately in **Audit & Rewrite Mode**), switch into a hostile senior-reviewer mindset and inspect the actual diff:

```bash
git status --short
git diff
```
*(Also read any newly created untracked files in full.)*

### The 8-Point Slop Audit Rubric

Check every changed hunk against this table:

| # | Slop Smell | Concrete Signal | Required Rewrite |
|---|---|---|---|
| 1 | **Additive Band-Aid** | New `if`/`flag` bolted onto existing logic instead of fixing root flow | Refactor the core path cleanly; remove the patch branch |
| 2 | **Defensive Bloat** | Redundant null/type checks inside typed internal functions | Delete checks guaranteed by types/boundaries |
| 3 | **Silent Swallow** | `catch` returning `null`/`[]`/`false` or ignoring failure | Fail fast or propagate typed error |
| 4 | **Speculative Layer** | Helper/interface/wrapper with only 1 caller and no boundary need | Inline it; keep code direct |
| 5 | **Narrator Noise** | Comments restating code, leftover `console.log`/debug prints, dead code | Delete immediately |
| 6 | **Parallel Copy** | Re-implemented logic that already exists elsewhere in repo | Replace with existing utility/component |
| 7 | **Type Escape** | `any`, broad casts, lint/type suppressions | Narrow properly or fix the contract |
| 8 | **Foreign Idiom** | Naming, error style, or structure clashes with exemplar files | Rewrite to match native repo conventions |

### Auto-Fix & Convergence Rules

- **Pass 1:** Fix every detected slop smell directly in place (behavior-preserving). Re-run the project's type-check, linter, and unit tests.
- **Fast Path:** If 0 slop smells remain and all checks pass, stop and report.
- **Pass 2 (Final Polish):** Re-read `git diff` once more to verify the rewrite didn't introduce new bloat or break behavior. Re-run verification if any edit was made.
- **Bounded Loop:** Maximum 2 audit passes. Never churn stylistic preferences endlessly.

---

## Output Summary

When done, provide a concise report:
- **Exemplar(s) mirrored:** `<paths>`
- **Slop smells caught & fixed:** bullet list of concrete removals/simplifications (or `None — clean on first pass`)
- **Verification:** type-check, lint, and test status

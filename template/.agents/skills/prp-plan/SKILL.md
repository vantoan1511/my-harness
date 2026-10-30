---
name: prp-plan
description: Create comprehensive feature implementation plan with codebase analysis and pattern extraction
---

# PRP Plan

Create a detailed, self-contained implementation plan that captures all codebase patterns, conventions, and context needed to implement a feature in a single pass.

**Core Philosophy**: A great plan contains everything needed to implement without asking further questions. Every pattern, every convention, every gotcha — captured once, referenced throughout.

**Golden Rule**: If you would need to search the codebase during implementation, capture that knowledge NOW in the plan.

---

## Phase 0 — DETECT

Determine input type from `$ARGUMENTS`:

| Input Pattern | Detection | Action |
|---|---|---|
| Path ending in `.prd.md` | File path to PRD | Parse PRD, find next pending phase |
| Path to `.md` with "Implementation Phases" | PRD-like document | Parse phases, find next pending |
| Path to any other file | Reference file | Read file for context, treat as free-form |
| Free-form text | Feature description | Proceed directly to Phase 1 |
| Empty / blank | No input | Ask user what feature to plan |

### PRD Parsing (when input is a PRD)

1. Read the PRD file
2. Parse the **Implementation Phases** section
3. Find phases by status:
   - Look for `pending` phases
   - Check dependency chains
   - Select the **next eligible pending phase**
4. Extract phase details (name, scope, acceptance criteria)
5. Use the phase description as the feature to plan

---

## Phase 1 — PARSE

Extract and clarify the feature requirements:
- **What** is being built (concrete deliverable)
- **Why** it matters (user value)
- **Who** uses it (target user/system)
- **Where** it fits (which part of the codebase)

### User Story Format:
```
As a [type of user],
I want [capability],
So that [benefit].
```

---

## Phase 2 — EXPLORE

Gather deep codebase intelligence. Search the codebase directly across 8 categories:

1. **Similar Implementations** — Existing features resembling the planned one.
2. **Naming Conventions** — How files, functions, variables, and classes are named.
3. **Error Handling** — How errors are caught, propagated, logged, and returned.
4. **Logging Patterns** — What gets logged and at what level.
5. **Type Definitions** — Relevant types, interfaces, and schemas.
6. **Test Patterns** — Where tests live, naming conventions, assertion styles.
7. **Configuration** — Config files, environment variables, feature flags.
8. **Dependencies** — Libraries, internal modules, and utilities used.

### Codebase Analysis (5 Traces):
1. **Entry Points** — How requests/events enter the system.
2. **Data Flow** — How data moves through code paths.
3. **State Changes** — What state is modified and where.
4. **Contracts** — Interfaces, APIs, or schemas that must be honored.
5. **Patterns** — Architectural patterns (repository, service, composable, handler).

---

## Phase 3 — RESEARCH

If external libraries, APIs, or unfamiliar technologies are involved:
1. Search official documentation and find usage examples.
2. Identify version-specific gotchas.

---

## Phase 4 — DESIGN

### UX / Behavioral Transformation (if applicable)
Document before and after states:
- **Before**: Current flow, what the user sees/does.
- **After**: Improved flow, what changes.

---

## Phase 5 — ARCHITECT

### Strategic Design
- **Approach**: High-level strategy.
- **Alternatives Considered**: Evaluated alternatives and why rejected.
- **Scope**: Concrete boundaries of what WILL be built.
- **NOT Building**: Explicit list of what is OUT OF SCOPE.

### Shift-Left Contract-First Design
Before defining tasks, define data contracts:
1. **API / Boundary Contracts**: Define exact request/response schemas or types.
2. **State & Storage Invariants**: Document state keys, stores, or default fallbacks.
3. **Component & Layout Contracts**: Document shared component usage and design tokens.

---

## Phase 6 — GENERATE

Write the full plan document. Save to:
```
.agents/PRPs/plans/{kebab-case-feature-name}.plan.md
```

### Plan Template

Read and follow the canonical plan structure in [`resources/plan-template.md`](./resources/plan-template.md), ensuring every task defines `ACTION`, `TEST_FIRST`, `IMPLEMENT`, `MIRROR`, `IMPORTS`, `GOTCHA`, and `MICRO_VALIDATE`, plus the Level 0 Shift-Left Pre-Flight validation command:
```bash
python -c "import os, subprocess, sys; p = '.agents/scripts/verify_shift_left.py'; p = p if os.path.exists(p) else os.path.expanduser('~/.gemini/config/plugins/my-harness/scripts/verify_shift_left.py'); sys.exit(subprocess.call([sys.executable, p, '--changed']) if os.path.exists(p) else 0)"
```

---

## Output

Report to user:

```
## Plan Created

- **File**: .agents/PRPs/plans/{name}.plan.md
- **Complexity**: [level]
- **Scope**: [N files, M tasks]
- **Key Patterns**: [top discovered patterns]

> Next step: Run `/implement .agents/PRPs/plans/{name}.plan.md` to execute this plan.
```

> [!IMPORTANT]
> Never begin implementation or write feature code during `/prp-plan`. The output must end cleanly with this plan handoff block so implementation can be executed via `/implement`.


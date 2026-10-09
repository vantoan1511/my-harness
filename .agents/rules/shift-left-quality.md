# Shift-Left Quality & Architecture Constitution

## Core Philosophy

> **Prevention over Detection.**
>
> Defects, architectural violations, design-system drift, and broken contracts must be prevented and caught at the earliest possible phase — during planning, test design, and atomic file edits — rather than deferred to post-implementation sweeps, code reviews, or pull requests.

Waiting until code review to discover missing tests, broken types, leaky abstractions, or architectural boundary violations is a failure of the shift-left workflow.

---

## The 5 Pillars of Shift-Left

```
┌────────────────────────────────────────────────────────────────────────┐
│                        SHIFT-LEFT TIMELINE                             │
│                                                                        │
│  [PRD / Plan] ──► [Test First] ──► [Atomic Edit] ──► [Pre-Flight Check]│
│       │                 │                │                  │          │
│   Contracts &       Failing Test     Minimal Code        Automated     │
│   Guardrails        Specified &      Passes Test &       Verification  │
│   Established       Confirmed        No Debt             Passes Zero-Err│
└────────────────────────────────────────────────────────────────────────┘
```

---

### Pillar 1: Contract-First & Type-Strict Boundaries

Before writing business logic, define the contracts that govern communication across boundaries:

1. **API / IPC / Service Contracts**:
   - Explicitly define the request/response data models and schemas before writing implementation logic.
   - Explicitly define strongly-typed models across boundary layers (e.g., Backend structs ↔ Frontend interfaces).
   - Never send unstructured dynamic dictionaries/maps when a typed model can be represented.
   - Keep payloads versionable, lean, and free of sensitive internal secrets.
2. **Strict Typing**:
   - Zero loose `any` types. Use explicit types or unknown with type narrowing.
   - Zero arbitrary type casts without documented rationale.
3. **State Invariants**:
   - Document pre-conditions, post-conditions, and default fallback states during the planning phase.

---

### Pillar 2: Preventative Architectural Guardrails

Every agent must enforce the following non-negotiable architectural rules *while drafting code*, not at review time:

1. **Boundary Discipline**:
   - Protect architectural boundaries. Do not import low-level system or runtime libraries directly in UI or presentation components.
   - Route interactions through centralized domain services or abstractions.
2. **Component & Design Standards**:
   - Favor the project's canonical component library and design tokens over raw HTML controls or ad-hoc styles.
   - Never hardcode raw hex colors when theme/design tokens exist.
3. **Backend & Error Safety**:
   - Handle errors explicitly (e.g. `Result<T, E>`, try/catch, error returns). Avoid uncontrolled crashes or panics in production code.
4. **Git Discipline**:
   - **NEVER** work directly on or commit to protected branches (`main`, `master`).
   - **ALWAYS** verify the branch with `git branch --show-current` and checkout a dedicated feature/fix branch (`feat/...`, `fix/...`) before modifying code.

---

### Pillar 3: Test-First (TDD) as Upfront Design

Testing is an active design tool, not a post-implementation verification chore:

1. **Red Gate**:
   - Before implementing logic, write the test case first in the appropriate test suite.
   - Execute the test runner and verify that the test fails for the expected reason.
2. **Green Gate**:
   - Write the minimal production code necessary to satisfy the test.
   - Execute the test runner and verify the test passes.
3. **Refactor Gate**:
   - Clean up code structure, eliminate duplication, and verify all tests remain green.

---

### Pillar 4: Atomic Micro-Validation Loops

Do not write code across 5 files before running a single verification check:

1. **Verify Every File**:
   - After editing a file, run an immediate micro-check:
     - Run type checking and linter on the modified file or project.
     - Run fast unit tests covering the modified function.
2. **Zero Accumulated Debt**:
   - If a type error, lint warning, or test failure appears, STOP immediately and resolve it before touching the next file.
   - Never assume "I will fix the compiler errors at the end."

---

### Pillar 5: Automated Shift-Left Pre-Flight

Before completing a task, committing, or reporting completion:

1. **Run the Pre-Flight Scanner**:
   ```bash
   python .agents/scripts/verify_shift_left.py --changed
   ```
   This fast static check (< 0.5s) scans changed files for:
   - Branch safety (not on `main`/`master`).
   - Configurable banned imports or leaky dependencies.
   - Configurable banned patterns or unsafe error calls.
   - Banned raw HTML tags or missing design directives.
2. **Run Targeted Tests**:
   - Run the unit tests covering the modified area.
3. **Run Full Verification**:
   - Run full static analysis, type checks, linters, and test suites.

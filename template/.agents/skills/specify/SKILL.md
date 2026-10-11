---
name: specify
description: Transform raw intent into a validated, contract-first specification and shift-left implementation plan through autonomous codebase discovery and interactive clarification.
---

# Specify: Intent → Clarification → Spec → Plan

Turn raw, informal user intent into a validated, contract-first specification and an executable Shift-Left implementation plan in a single streamlined workflow.

```
┌────────────────────────────────────────────────────────────────────────┐
│                   INTENT ──► SPEC ──► PLAN WORKFLOW                    │
│                                                                        │
│  [User Intent]                                                         │
│        │                                                               │
│        ▼                                                               │
│  Phase 1: RECONNAISSANCE (Autonomous Codebase Exploration)             │
│        • Survey analogous features, APIs, stores, & components         │
│        • Locate reusable modules, tokens, & patterns                   │
│        │                                                               │
│        ▼                                                               │
│  Phase 2: CLARIFICATION (Interactive Ambiguity Resolution)             │
│        • Identify decision forks, UX behaviors, & technical options    │
│        • Ask targeted questions (using `ask_question` interactive UI)  │
│        │                                                               │
│        ▼                                                               │
│  Phase 3: SPECIFICATION (Contract-First PRD/Spec)                      │
│        • Define Problem, User Story, Invariants, & Scope               │
│        • Define interface contracts, models, schemas, & boundaries     │
│        • Output: `.agents/PRPs/prds/{name}.prd.md`                     │
│        │                                                               │
│        ▼                                                               │
│  Phase 4: SHIFT-LEFT PLAN GENERATION                                   │
│        • Automatically transitions spec into `prp-plan`                │
│        • Generates `.agents/PRPs/plans/{name}.plan.md`                 │
│        • Pre-fills TDD failing test specs & micro-validation commands  │
│        │                                                               │
│        ▼                                                               │
│  [Ready to `/implement`]                                               │
└────────────────────────────────────────────────────────────────────────┘
```

---

## When to Activate

- User provides an informal, high-level, or underspecified feature request.
- User invokes `/specify <intent>` or `/spec <intent>`.
- User asks to explore a capability before writing code.
- User wants architectural and UX alignment before generating a plan.

---

## Phase 1 — RECONNAISSANCE: Autonomous Information Gathering

**DO NOT ask questions immediately.** Before engaging the user, silently gather deep codebase context so every subsequent question is informed, specific, and grounded in repository evidence.

### 0. Consult Curated Knowledge Base
- Inspect `.agents/references/README.md` for relevant Architectural Decision Records (ADRs), canonical recipes, and domain gotchas before searching from scratch.
- Review existing recipes in `.agents/references/recipes/` and gotchas in `.agents/references/gotchas/`.

### 1. Locate Analogous Features & Components
- Use `codegraph` (`codegraph_explore`) or targeted searches to find similar existing implementations.
- If UI is involved:
  - Inspect analogous views and components.
  - Check component styling, design tokens, and shared layouts.
- If Backend/Data is involved:
  - Inspect existing handlers, endpoints, or data models.
  - Inspect reactive stores, state containers, and domain services.

### 2. Identify Technical & Architectural Boundaries
- Can existing APIs handle this, or are new endpoints/handlers needed?
- What state needs to be stored? (Session state, local cache, database, persistent config).
- What existing modules can be reused or extended?

### 3. Extract Unknowns & Decision Forks
List specific ambiguities that cannot be answered by the code alone:
- **Scope boundaries**: What is in v1 vs out of scope?
- **Placement & UX**: Where should the control/view live?
- **Behavioral choices**: Confirmation dialog vs instant feedback? Polling vs websocket stream?

---

## Phase 2 — CLARIFICATION: Interactive Ambiguity Resolution

Engage the user to clarify open questions and resolve decision forks.

### 1. Interactive Questioning via `ask_question`
When decision forks have clear choices, use the interactive `ask_question` tool to present structured choices to the user:

```json
{
  "questions": [
    {
      "question": "Where should the new action be accessible from?",
      "options": [
        "(Recommended) Both in the resource details panel and the table row context menu",
        "Only in the resource details panel",
        "Only as a row action in the resource table"
      ],
      "is_multi_select": false
    },
    {
      "question": "What confirmation behavior do you prefer?",
      "options": [
        "(Recommended) Confirmation modal before triggering action",
        "Immediate trigger with non-blocking toast notification"
      ],
      "is_multi_select": false
    }
  ]
}
```

### 2. Guiding Principles for Clarification
- Ask at most 2–4 high-impact questions at once.
- Always provide a recommended option prefixed with `(Recommended)`.
- Never ask questions the codebase already answers (e.g. project framework, theme, language).
- Wait for user response before generating the specification.

---

## Phase 3 — SPECIFICATION: Contract-First Spec Generation

Once answers are received, synthesize user intent and codebase reconnaissance into a crisp specification.

Save the specification to:
```
.agents/PRPs/prds/{kebab-case-feature-name}.prd.md
```

### Spec Template (`.prd.md`)

```markdown
# Spec: [Feature Name]

## 1. Intent & Problem Statement
- **User Intent**: [Original raw intent from user]
- **Problem**: [Who is affected, what pain they experience, and why current workaround is insufficient]
- **Target Outcome**: [Observable capability and success metric]

## 2. User Experience & Interactions
- **Placement**: [Exact location in UI: page, panel, toolbar, table, menu]
- **Interaction Flow**:
  1. User clicks ...
  2. System shows ...
  3. Action executes with feedback ...
- **Component Strategy**:
  - Components used: [`Button`, `Dialog`, `Toast`, `Select`, etc.]
  - Tokens used: [`var(--accent)`, `var(--border)`, `var(--bg-panel)`, etc.]

## 3. Contract-First Boundaries

### API / Boundary Contract (if applicable)
```typescript
// Define request/response models, interfaces, or schemas
export interface ActionRequest {
  id: string
  payload: Record<string, unknown>
}

export interface ActionResponse {
  success: boolean
  message: string
}
```

### State & Storage Invariants
- State store / Cache location
- Storage key / DB table
- Default fallback state if offline / empty.

## 4. Scope Boundaries
- **In Scope (v1)**:
  - [Explicit item 1]
  - [Explicit item 2]
- **Out of Scope**:
  - [Explicit item 1 to avoid scope creep]
  - [Explicit item 2]

## 5. Acceptance Criteria
- [ ] AC-1: [Specific testable condition]
- [ ] AC-2: [Specific testable condition]
- [ ] AC-3: Zero architectural violations (verify_shift_left.py passes)
```

---

## Phase 4 — PLAN GENERATION: Automatic Shift-Left Implementation Plan

Immediately following specification creation, automatically generate the Shift-Left Implementation Plan so the user can transition directly into execution.

Save the plan to:
```
.agents/PRPs/plans/{kebab-case-feature-name}.plan.md
```

The plan must:
1. Reference the newly created `.prd.md` as its source PRD.
2. Embed the contracts defined in Phase 3.
3. Define **Step-by-Step Tasks** where each task contains:
   - `ACTION`: concrete edit description
   - `TEST_FIRST`: specific test file path, test name, input fixture, expected assertion
   - `IMPLEMENT`: minimal code instructions to make test pass
   - `MICRO_VALIDATE`: fast check command (`npm test`, `pytest`, `cargo test`, `python .agents/scripts/verify_shift_left.py --changed`, etc.)
4. Include the Level 0 Pre-Flight Scanner in validation commands.

---

## Phase 5 — HANDOFF

The output of `/specify` must always strictly adhere to the following Markdown heading and bullet structure without deviating or preemptively writing implementation code. Always use blank lines between sections, standard Markdown headings, and bullet lists (`- `) so that chat and markdown renderers preserve formatting without collapsing lines:

```markdown
## Specification & Implementation Plan Ready

- **Feature**: [Feature Name]
- **Spec**: [name].prd.md
- **Plan**: [name].plan.md
- **Test Strategy**: [Test runners and command, e.g., cargo test, npm test, pytest]

### Contracts Defined
- [Contract 1, e.g. API request/response schema or endpoint parameters]
- [Contract 2, e.g. State store action or storage model]

### Summary of Decisions
- **[Decision Area 1]**: [Explanation of decision]
- **[Decision Area 2]**: [Explanation of decision]

Next Step: Run /implement .agents/PRPs/plans/{name}.plan.md to begin test-driven implementation.
```

> [!IMPORTANT]
> Never begin implementation or write feature code during `/specify`. The output must end cleanly with this handoff block.

---

## Verification Checklist

Before reporting completion of the specify workflow:
- [ ] Codebase was searched *before* asking questions (no redundant questions).
- [ ] Ambiguities were clarified interactively using `ask_question`.
- [ ] Interface contracts and data models are explicitly documented in the spec.
- [ ] Spec was saved to `.agents/PRPs/prds/{name}.prd.md`.
- [ ] Plan was generated and saved to `.agents/PRPs/plans/{name}.plan.md`.
- [ ] Every task in the plan has a concrete `TEST_FIRST` specification and `MICRO_VALIDATE` command.

---
name: specify
description: Transform raw intent into a validated, contract-first specification and shift-left implementation plan through autonomous codebase discovery and interactive clarification.
---

# Specify: Intent → Clarification → Spec → Plan

Turn raw, informal user intent into a validated, contract-first specification and an executable Shift-Left implementation plan in a single streamlined workflow.

```
┌────────────────────────────────────────────────────────────────────────┐
│              ISSUE / INTENT ──► CLEAR? ──► SPEC ──► PLAN               │
│                                                                        │
│  [GitHub Issue #N or User Intent]                                      │
│        │                                                               │
│        ▼                                                               │
│  Phase 1: RECONNAISSANCE (Issue Fetch + Autonomous Exploration)        │
│        • Fetch issue & Parent Epic (`gh issue view`) if #N provided    │
│        • Inspect current Git branch & candidate PR target branches     │
│        • Survey analogous features, APIs, stores, & components         │
│        │                                                               │
│        ▼                                                               │
│  Phase 1.5: THE "CLEAR?" GATE (Definition of Ready Check)              │
│        • Run `gh_project.py check-ready` + decision-fork check         │
│        • Clear? ──Yes──► Ask Delivery/PR prefs (if unset) ─► Phase 4   │
│        • Clear? ──No───► Continue to Phase 2 Clarification             │
│        │                                                               │
│        ▼                                                               │
│  Phase 2: CLARIFICATION (Interactive Ambiguity Resolution)             │
│        • Ask targeted questions + Delivery/PR prefs (`ask_question`)   │
│        • Sync clarified AC & notes back to Issue (`gh issue edit`)     │
│        │                                                               │
│        ▼                                                               │
│  Phase 3: SPECIFICATION (Contract-First PRD/Spec)                      │
│        • Define interface contracts, models, schemas, & boundaries     │
│        • Output: `.agents/PRPs/prds/{name}.prd.md` (when needed)       │
│        │                                                               │
│        ▼                                                               │
│  Phase 4: SHIFT-LEFT PLAN GENERATION                                   │
│        • Generates `.agents/PRPs/plans/{name}.plan.md`                 │
│        • Embeds Issue/Epic, Branch Name, Auto-Create PR, Base Branch   │
│        │                                                               │
│        ▼                                                               │
│  [Ready to `/implement`]                                               │
└────────────────────────────────────────────────────────────────────────┘
```

---

## When to Activate

- User provides a GitHub Issue reference (`/specify #42` or issue URL) to refine, clarify, and plan.
- User provides an informal, high-level, or underspecified feature request.
- User invokes `/specify <intent>` or `/spec <intent>`.
- User asks to explore a capability before writing code.
- User wants architectural and UX alignment before generating a plan.

---

## Phase 1 — RECONNAISSANCE: Autonomous Information Gathering

**DO NOT ask questions immediately.** Before engaging the user, silently gather deep codebase context (and GitHub Issue context, if an issue is referenced) so every subsequent question is informed, specific, and grounded in repository evidence.

### 0a. GitHub Issue & Epic Ingestion (When Input is `#<issue>` or Issue URL)
- Extract the issue number and inspect the ticket and comments:
  ```bash
  gh issue view <number> --json number,title,body,labels,comments,projectItems
  ```
- If the issue body contains `Part of #<epic>`, also inspect the Parent Epic (`gh issue view <epic> --json number,title,body`) for broader goals and constraints.
- Evaluate Issue Readiness using `gh_project.py`:
  ```bash
  python -c "import os, subprocess, sys; p = '.agents/scripts/gh_project.py'; p = p if os.path.exists(p) else os.path.expanduser('~/.gemini/config/plugins/my-harness/scripts/gh_project.py'); sys.exit(subprocess.call([sys.executable, p, 'check-ready', '<number>']) if os.path.exists(p) else 0)"
  ```

### 0b. Git Branch & PR Target Discovery
Inspect the current Git branch and available branches before asking Delivery & PR Preferences:
```bash
git branch --show-current
git branch -a
```
Identify:
- The current working branch (e.g., `main`, `master`, or an active integration/feature branch like `feat/...`).
- Candidate target branches for a PR (default `main`/`master`, plus any active integration branches `feat/*` or `develop` / `release/*`).

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

## Phase 1.5 — THE "CLEAR?" GATE (Readiness & Fast-Track Decision)

### Blocker & Board Reorganization Gate (MANDATORY before Spec/Plan)

During Phase 1 / Phase 1.5, inspect all `Depends on #<N>` links, open prerequisite issues, and blockers discovered during codebase reconnaissance:

1. **All deliverables blocked**:
   - **STOP immediately** at `/specify` — do NOT generate a `.prd.md` or `.plan.md`.
   - Ensure every blocker exists as its own tracked GitHub Issue on the Project board (creating missing blocker/follow-up issues if needed), update the blocked issue's `### Technical Notes / Dependencies` with `Depends on #<blocker>`, set its status to `Todo`, and recommend resolving the blocker first.
2. **Partially blocked (mix of unblocked + blocked work, e.g. Phase 1 unblocked, Phase 2 blocked)**:
   - **STOP before Phase 4 (Plan Generation)** and reorganize the board first:
     - Split the blocked portion into its own dedicated follow-up GitHub Issue (linked to the same `Parent Epic` and `Depends on #<blocker>`), add it to the Project board (`Todo`), and verify every blocker has its own issue.
     - Narrow the current issue's `### Summary` and `### Acceptance Criteria` strictly to the **unblocked** deliverables so the resulting PR resolves 100% of the issue (`Closes #<issue>`).
   - Confirm the reorganized scope before generating the plan.

Before prompting the user, determine whether requirements are already unambiguous:

- **CLEAR (`is_clear == true` from `gh_project.py check-ready` AND zero unresolved UX/architectural decision forks after codebase reconnaissance)**:
  - **Skip redundant technical/UX clarification questions** and **skip creating a duplicate `.prd.md`** when the GitHub Issue + Parent Epic already serve as the authoritative spec.
  - **Delivery & PR Preferences Check (MANDATORY unless already specified)**: If the user has not already explicitly stated **Branch Name**, **Auto-Create PR** mode (`--no-pr` / `--local` / seamless), and **PR Target Branch** (`--base <branch>`), ask **only** those Delivery & PR Preferences questions via `ask_question` (see Phase 2, section `1a. Delivery & PR Preferences`) before generating the plan.
  - Transition directly to **Phase 4 — PLAN GENERATION** to produce `.agents/PRPs/plans/issue-<number>-{kebab-name}.plan.md` with `- **GitHub Issue**: #<number>`, `- **Parent Epic**: #<epic>`, `- **Branch Name**: ...`, `- **Auto-Create PR**: ...`, and `- **Base Branch**: ...` in Metadata.
- **NOT CLEAR (`is_clear == false` OR unresolved decision forks remain)**:
  - Proceed to **Phase 2 — CLARIFICATION**.

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

### 1a. Delivery & PR Preferences (MANDATORY unless already specified)
Always confirm the working branch and how `/implement` should deliver the completed work (combining these with the technical/UX questions above in a single `ask_question` call when in Phase 2, or asking them standalone at Phase 1.5 when requirements are already clear):

1. **Working Branch Name (`Branch Name`)**:
   - Decide the exact feature/fix branch name `/implement` will work on (never `main`/`master`): either the current non-protected feature branch (if already on one) or a new branch (`feat/issue-<number>-{kebab-name}`, `feat/{kebab-name}`, or `fix/{kebab-name}`).
2. **Auto-Create PR (Seamless Mode)**:
   - Ask whether `/implement` should run in **Seamless Mode** (commit, push, and auto-create a GitHub PR) or **Local-Only Mode** (`--no-pr` / `local: true` or `--no-commit`).
3. **PR Target Branch (`Base Branch`)**:
   - Ask which target branch the PR should merge into (populated from Phase 1 Git branch discovery — recommend `main`/`master` or the active integration `feat/*` branch when currently working from one; `ask_question` automatically lets the user enter another branch via *Other*).

```json
{
  "questions": [
    {
      "question": "Which working branch name should /implement use?",
      "options": [
        "(Recommended) feat/<kebab-name> (or <current-feature-branch> if already on one)",
        "fix/<kebab-name>"
      ],
      "is_multi_select": false
    },
    {
      "question": "Should /implement auto-create a GitHub PR after validation (Seamless Mode)?",
      "options": [
        "(Recommended) Yes — Auto-create PR in Seamless Mode",
        "No — Local-only commit (--no-pr / local: true)",
        "No — Keep changes uncommitted locally (--no-commit)"
      ],
      "is_multi_select": false
    },
    {
      "question": "Which target branch should the PR merge into?",
      "options": [
        "(Recommended) main",
        "<detected-integration-branch-if-any>"
      ],
      "is_multi_select": false
    }
  ]
}
```
*(Skip any question only if the user already specified it explicitly in the prompt, e.g., branch name, `--no-pr`, or `--base <branch>`.)*

### 2. Guiding Principles for Clarification
- Ask at most 2–4 high-impact technical/UX questions at once, plus up to 3 Delivery & PR Preferences questions (`Branch Name`, `Auto-Create PR`, `PR Target Branch`) when not yet specified.
- Always provide a recommended option prefixed with `(Recommended)`.
- Never ask technical questions the codebase already answers (e.g. project framework, theme, language).
- Wait for user response before generating the specification and plan.

### 3. Sync Clarified Spec Back to GitHub Issue (When Working from Issue `#<number>`)
After receiving the user's answers, update the GitHub Issue so it stays the single source of truth with refined `### Summary`, `### Acceptance Criteria` (`- [ ]`), and `### Technical Notes / Dependencies`:
```powershell
gh issue edit <number> --body $updatedBody
```

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
1. Reference the newly created `.prd.md` (or `GitHub Issue #<number>` / `Parent Epic #<epic>`) in its `## Metadata`.
2. Persist the user's **Delivery & PR Preferences** in `## Metadata` so `/implement` and `/pr` execute them automatically in a fresh session:
   - `- **Branch Name**: <branch-name>` (e.g., `feat/issue-<number>-{kebab-name}` or `feat/{kebab-name}`)
   - `- **Auto-Create PR**: true` (Seamless Mode) or `- **Auto-Create PR**: false (local: true)` (Local-Only Mode; append `--no-commit` note if uncommitted mode was chosen)
   - `- **Base Branch**: <target-branch>` (e.g., `main` or `feat/<integration-branch>`)
3. Embed the contracts defined in Phase 3 (or resolved from the GitHub Issue).
4. Define **Step-by-Step Tasks** where each task contains:
   - `ACTION`: concrete edit description
   - `TEST_FIRST`: specific test file path, test name, input fixture, expected assertion
   - `IMPLEMENT`: minimal code instructions to make test pass
   - `MICRO_VALIDATE`: fast check command (`npm test`, `pytest`, `cargo test`, or `verify_shift_left.py --changed` from `.agents/scripts/` or `~/.gemini/config/plugins/my-harness/scripts/`)
5. Include the Level 0 Pre-Flight Scanner in validation commands.

---

## Phase 5 — HANDOFF

The output of `/specify` must always strictly adhere to the following Markdown heading and bullet structure without deviating or preemptively writing implementation code. Always use blank lines between sections, standard Markdown headings, and bullet lists (`- `) so that chat and markdown renderers preserve formatting without collapsing lines:

```markdown
## Specification & Implementation Plan Ready

- **Feature**: [Feature Name]
- **Spec**: [name].prd.md
- **Plan**: [name].plan.md
- **Test Strategy**: [Test runners and command, e.g., cargo test, npm test, pytest]
- **Branch Name**: [<branch-name>]
- **Auto-Create PR**: [Yes (Seamless Mode) | No (Local-Only / --no-pr)]
- **PR Target Branch**: [<target-branch> | N/A (local-only)]

### Contracts Defined
- [Contract 1, e.g. API request/response schema or endpoint parameters]
- [Contract 2, e.g. State store action or storage model]

### Summary of Decisions
- **[Decision Area 1]**: [Explanation of decision]
- **[Decision Area 2]**: [Explanation of decision]

> **Recommended Next Step (Clean Context & Low Effort)**:
> 1. Open a **New Conversation** in Antigravity Desktop.
> 2. Switch Model Effort to **Medium** (or **Low** for small scoped tasks).
> 3. Copy & paste the prompt below to run `/implement`:
> ```text
> /implement @.agents/PRPs/plans/{name}.plan.md
> ```
> Starting execution in a fresh session eliminates planning clutter, prevents context rot, and reduces LLM response latency.
```

*(When generating the actual handoff, `/implement @.agents/PRPs/plans/{name}.plan.md` automatically picks up `Branch Name`, `Auto-Create PR`, and `Base Branch` from the plan metadata; you may also include explicit `--no-pr` / `--no-commit` / `--base <target-branch>` flags in the command when non-default options were selected.)*

> [!IMPORTANT]
> Never begin implementation or write feature code during `/specify`. The output must end cleanly with this handoff block.

---

## Verification Checklist

Before reporting completion of the specify workflow:
- [ ] Codebase and current Git branches (`git branch --show-current`, `git branch -a`) were inspected *before* asking questions.
- [ ] Ambiguities and Delivery & PR Preferences (`Branch Name`, `Auto-Create PR` seamless mode, and `PR Target Branch`) were clarified interactively via `ask_question` (unless already explicitly specified).
- [ ] Interface contracts and data models are explicitly documented in the spec.
- [ ] Spec was saved to `.agents/PRPs/prds/{name}.prd.md` (or linked GitHub Issue updated when fast-tracked).
- [ ] Plan was generated and saved to `.agents/PRPs/plans/{name}.plan.md` with `Branch Name`, `Auto-Create PR`, and `Base Branch` in `## Metadata`.
- [ ] Every task in the plan has a concrete `TEST_FIRST` specification and `MICRO_VALIDATE` command.

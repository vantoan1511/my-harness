# Spec: Integrated Review, Simplify & Adapt Loop in `/implement`

## 1. Intent & Problem Statement
- **User Intent**: Improve the AI harness workflow by integrating code review, simplification, and automated adaptation directly into `/implement` so users do not have to manually open a separate session to run `/code-review` and create a follow-up adaptation plan.
- **Problem**:
  In the current `/implement` workflow (`.agents/skills/implement/SKILL.md` and `template/.agents/skills/implement/SKILL.md`), execution transitions directly from **Phase 4 (VALIDATE)** to **Phase 5 (REPORT)**, **Phase 6 (COMMIT)**, and **Phase 7 (PR)**, and then instructs the user at the end to *"run `/code-review {number}` for automated review."*
  This causes three major workflow inefficiencies:
  1. Code is committed and pushed to a PR before undergoing a holistic semantic code review against the Shift-Left Quality & Architecture Constitution (`review-rules.md`, `shift-left-quality.md`, `simplifier/SKILL.md`).
  2. Reviewing in the same agent context suffers from confirmation bias unless delegated to an isolated, fresh-context critic subagent.
  3. Users must manually open another session, run `/code-review`, and ask another agent to generate and execute a remediation plan from the review artifact.
- **Target Outcome**:
  1. Introduce **Phase 4.5 — REVIEW, SIMPLIFY & ADAPT (Self-Healing Loop)** inside `/implement` (between Phase 4 VALIDATE and Phase 5 REPORT).
  2. Delegate semantic review of the uncommitted working tree diff to a **fresh-context Critic Subagent** (`invoke_subagent`) to eliminate confirmation bias and preserve main-agent context window hygiene.
  3. Automatically remediate `CRITICAL`, `HIGH`, and `MEDIUM` (including code simplification targets from `simplifier`) findings via atomic TDD micro-loops with a bounded circuit breaker (maximum 2 passes).
  4. Record a unified **Self-Review & Adaptation Log** inside the implementation report (`resources/report-template.md`), PR body, and Phase 8 output summary.
  5. Keep project `.agents/`, `template/.agents/`, `AGENTS.md`, `template/AGENTS.md.template`, `README.md`, `template/PLUGIN_README.md`, and the global Antigravity plugin synchronized.

---

## 2. User Experience & Interactions

### Workflow Progression in `/implement`
```
Phase 3: EXECUTE (Sequential TDD Task Loop + Micro-Validation)
   │
   ▼
Phase 4: VALIDATE (Pre-Flight Scanner, Static Analysis, Unit Tests, Build)
   │
   ▼
Phase 4.5: REVIEW, SIMPLIFY & ADAPT (Autonomous Critic → Fix → Re-Verify)
   ├─ 1. Spawn isolated Critic Subagent on `git diff HEAD` + untracked files
   ├─ 2. Evaluate Security, Architecture, Reuse/DRY, Code Smells, & Simplifier rules
   ├─ 3. Auto-adapt CRITICAL, HIGH, & MEDIUM findings (RED → GREEN → Micro-Validate)
   ├─ 4. Re-run Phase 4 validation & verify convergence (max 2 iterations)
   └─ 5. Escalate via `ask_question` only if a blocker conflicts with plan after 2 passes
   │
   ▼
Phase 5: REPORT (Includes Self-Review & Adaptation Summary)
   │
   ▼
Phase 6 & 7: COMMIT & PR (Only pre-reviewed, simplified, zero-blocker code is pushed)
```

---

## 3. Contract-First Boundaries

### 1. Critic Subagent Contract (Phase 4.5 Input/Output Schema)
When `/implement` invokes the Critic Subagent (`invoke_subagent` with `research` or read-only reviewer role), the subagent must return findings structured by severity:

```markdown
### Review Findings
- **Decision**: APPROVE | ADAPT_REQUIRED | ESCALATE
- **Findings**:
  - `[CRITICAL|HIGH|MEDIUM|LOW]` `path/to/file:line` — **Category**: [Security | Architecture | Reuse/DRY | Code Smell | Simplifier]
    - **Issue**: [Concise description of defect or smell]
    - **Adaptation**: [Concrete minimal fix required]
```

### 2. Severity-Tiered Remediation Matrix
| Severity | Scope | Required Action in Phase 4.5 |
|---|---|---|
| **CRITICAL** | Security vulnerabilities, secrets, data loss, broken boundaries | **Mandatory Auto-Adapt**: Write/update failing test (RED), apply fix (GREEN), run micro-validation. Block commit if unresolved. |
| **HIGH** | Logic bugs, contract mismatches, unhandled errors, architecture drift | **Mandatory Auto-Adapt**: Write/update failing test (RED), apply fix (GREEN), run micro-validation. Block commit if unresolved. |
| **MEDIUM** | DRY violations, >50 LOC functions, deep nesting (>3 levels), dead code, `simplifier` targets | **Auto-Adapt & Simplify**: Apply behavior-preserving simplification or refactoring and re-verify tests. |
| **LOW** | Minor stylistic nits or optional trade-offs | **Log Only**: Record in implementation report under *Self-Review & Adaptation Log* without unnecessary code churn. |

### 3. Bounded Circuit Breaker Invariants
- **Maximum Iterations**: `MAX_REVIEW_PASSES = 2`.
  - **Pass 1**: Full diff review by Critic Subagent → Atomic remediation of all `CRITICAL`, `HIGH`, and `MEDIUM` items → Full Phase 4 re-validation.
  - **Pass 2 (Verification Pass)**: Triggered only if Pass 1 modified source files; verifies remediated files introduced zero new `CRITICAL` or `HIGH` issues.
- **Escalation Gate**: If any `CRITICAL` or `HIGH` finding remains unresolved after Pass 2 or directly contradicts the user's explicit specification, halt before Phase 6 (COMMIT) and prompt the user via `ask_question`.

### 4. Implementation Report & Output Contract
Both `.agents/skills/implement/resources/report-template.md` and `template/.agents/skills/implement/resources/report-template.md` must include a `## Self-Review & Adaptation Log` section:

```markdown
## Self-Review & Adaptation Log

| # | Severity | File | Issue | Adaptation Applied | Status |
|---|---|---|---|---|---|
| 1 | [HIGH/MEDIUM/LOW] | `path/to/file` | [finding] | [fix applied or logged] | [done] Adapted / Logged |
```

### 5. Synchronization Invariant
- `.agents/skills/implement/SKILL.md` and `template/.agents/skills/implement/SKILL.md` must be byte-for-byte identical.
- `.agents/skills/implement/resources/report-template.md` and `template/.agents/skills/implement/resources/report-template.md` must be byte-for-byte identical.

---

## 4. Scope Boundaries
- **In Scope (v1)**:
  - Add `Phase 4.5 — REVIEW, SIMPLIFY & ADAPT` to `.agents/skills/implement/SKILL.md` and `template/.agents/skills/implement/SKILL.md`.
  - Update Phase 7 (PR Body), Phase 8 (Output Summary), and Success Criteria in `implement/SKILL.md` to reflect built-in self-review and adaptation.
  - Update `.agents/skills/implement/resources/report-template.md` and `template/.agents/skills/implement/resources/report-template.md` with the `## Self-Review & Adaptation Log` section.
  - Update `AGENTS.md`, `template/AGENTS.md.template`, `README.md`, and `template/PLUGIN_README.md` to document the integrated review-and-adapt loop inside `/implement`.
  - Add unit tests in `tests/test_implement_skill.py` verifying Phase 4.5 presence, Critic Subagent instructions, bounded loop rules, report template structure, and byte-for-byte parity between project and template files.
  - Deploy updated skills and documentation to the global Antigravity plugin via `python harness.py update --force`.
- **Out of Scope**:
  - Removing standalone `/code-review` (which remains essential for reviewing external PRs or ad-hoc manual audits).
  - Unbounded autonomous refactoring of files outside the plan's modified file set.

---

## 5. Acceptance Criteria
- [ ] AC-1: `implement/SKILL.md` (both project and template) defines `## Phase 4.5 — REVIEW, SIMPLIFY & ADAPT` with Fresh-Context Critic Subagent delegation, Severity-Tiered Remediation Matrix, and a 2-pass circuit breaker.
- [ ] AC-2: `implement/resources/report-template.md` (both project and template) includes `## Self-Review & Adaptation Log` and updated validation/next-step entries.
- [ ] AC-3: Project and template files for `implement/SKILL.md` and `implement/resources/report-template.md` are byte-for-byte identical.
- [ ] AC-4: `AGENTS.md`, `template/AGENTS.md.template`, `README.md`, and `template/PLUGIN_README.md` reflect the integrated review & adaptation flow.
- [ ] AC-5: `tests/test_implement_skill.py` passes alongside the full test suite (`python -m unittest discover tests`).
- [ ] AC-6: Zero architectural violations (`python .agents/scripts/verify_shift_left.py --changed` passes).

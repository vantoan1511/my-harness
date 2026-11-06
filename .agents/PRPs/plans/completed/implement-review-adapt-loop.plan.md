# Plan: Integrated Review, Simplify & Adapt Loop in `/implement`

## Summary
Integrate an autonomous **Phase 4.5 — REVIEW, SIMPLIFY & ADAPT (Self-Healing Loop)** directly into the `/implement` skill before committing and opening a pull request. The phase delegates semantic code review of the uncommitted working tree diff to a fresh-context Critic Subagent (eliminating confirmation bias), automatically adapts `CRITICAL`, `HIGH`, and `MEDIUM` (including `simplifier` targets) findings via bounded TDD micro-loops (max 2 passes), and records all adaptations in the implementation report and PR summary.

## User Story
As an engineer using `my-harness`, I want `/implement` to automatically review, simplify, and adapt my implementation before committing and opening a PR, so that I do not have to manually start a second session for `/code-review` and create a separate adaptation plan.

## Problem → Solution
- **Current State**: `/implement` runs mechanical checks (Phase 4 VALIDATE) and immediately commits and opens a PR, prompting the user to run `/code-review` afterward in another session.
- **Desired State**: `/implement` runs `Phase 4.5 — REVIEW, SIMPLIFY & ADAPT` right after mechanical validation passes. It spawns an isolated Critic Subagent to audit `git diff HEAD` + untracked files against the Shift-Left Constitution and `simplifier` rules, auto-remediates `CRITICAL`/`HIGH`/`MEDIUM` findings using TDD micro-validation (up to 2 passes), and logs the results in the implementation report and PR description prior to committing.

## Metadata
- **Complexity**: Medium
- **Source PRD**: [.agents/PRPs/prds/implement-review-adapt-loop.prd.md](file:///d:/Projects/my-harness/.agents/PRPs/prds/implement-review-adapt-loop.prd.md)
- **PRD Phase**: Phase 1 (Complete v1)
- **Estimated Files**: 10

---

## Mandatory Reading

| Priority | File | Lines | Why |
|---|---|---|---|
| P0 (critical) | `.agents/skills/implement/SKILL.md` | 133-460 | Current Phase 4–8 flow, PR body template, and success criteria |
| P0 (critical) | `.agents/skills/implement/resources/report-template.md` | 1-57 | Implementation report template to extend with Self-Review & Adaptation Log |
| P1 (important) | `.agents/skills/code-review/SKILL.md` | 21-90 | Local Review Mode rubric (Security, Architecture, Reuse/DRY, Smells, Consistency) |
| P1 (important) | `.agents/skills/simplifier/SKILL.md` | 1-42 | Code simplification targets to incorporate into MEDIUM severity adaptation |
| P1 (important) | `tests/test_specify_format.py` | 1-33 | Reference pattern for skill format & template parity unit tests |

---

## Patterns to Mirror

### SKILL_PARITY_TEST_STRUCTURE
// SOURCE: [tests/test_specify_format.py:6-18](file:///d:/Projects/my-harness/tests/test_specify_format.py#L6-L18)
```python
class TestImplementSkill(unittest.TestCase):
    def setUp(self):
        self.repo_root = Path(__file__).resolve().parent.parent
        self.project_skill = self.repo_root / ".agents" / "skills" / "implement" / "SKILL.md"
        self.template_skill = self.repo_root / "template" / ".agents" / "skills" / "implement" / "SKILL.md"
```

### CROSS_PLATFORM_PRE_FLIGHT_SNIPPET
// SOURCE: [.agents/skills/implement/SKILL.md:112](file:///d:/Projects/my-harness/.agents/skills/implement/SKILL.md#L112)
```bash
python -c "import os, subprocess, sys; p = '.agents/scripts/verify_shift_left.py'; p = p if os.path.exists(p) else os.path.expanduser('~/.gemini/config/plugins/my-harness/scripts/verify_shift_left.py'); sys.exit(subprocess.call([sys.executable, p, '--changed']) if os.path.exists(p) else 0)"
```

---

## Files to Change

| File | Action | Justification |
|---|---|---|
| `tests/test_implement_skill.py` | CREATE | Unit tests verifying Phase 4.5 structure, Critic Subagent contract, circuit breaker rules, report template updates, and byte-for-byte project/template parity |
| `.agents/skills/implement/SKILL.md` | UPDATE | Insert `Phase 4.5 — REVIEW, SIMPLIFY & ADAPT`, update PR template (Phase 7), Output summary (Phase 8), and Success Criteria |
| `template/.agents/skills/implement/SKILL.md` | UPDATE | Synchronize template copy with `.agents/skills/implement/SKILL.md` |
| `.agents/skills/implement/resources/report-template.md` | UPDATE | Add `## Self-Review & Adaptation Log` section and update Validation Results table |
| `template/.agents/skills/implement/resources/report-template.md` | UPDATE | Synchronize template copy with `.agents/skills/implement/resources/report-template.md` |
| `AGENTS.md` | UPDATE | Document built-in review & adaptation loop under Phase 3 — Implement |
| `template/AGENTS.md.template` | UPDATE | Synchronize starter `AGENTS.md.template` with updated Phase 3 description |
| `README.md` | UPDATE | Update `/implement` description to highlight autonomous review, simplification, and self-adaptation |
| `template/PLUGIN_README.md` | UPDATE | Update `/implement` section in plugin README |

## NOT Building
- Removing standalone `/code-review` (which remains dedicated to reviewing existing GitHub PRs or standalone manual diffs).
- Unbounded multi-pass review loops (strictly capped at 2 passes to prevent infinite ping-ponging).

---

## Step-by-Step Tasks

### Task 1: Write Unit Tests for `/implement` Review-Adapt Loop & Template Parity (RED)
- **ACTION**: Create `tests/test_implement_skill.py` to test that `implement/SKILL.md` and `implement/resources/report-template.md` exist in both `.agents/` and `template/.agents/`, are byte-for-byte identical, and include `## Phase 4.5 — REVIEW, SIMPLIFY & ADAPT`, Fresh-Context Critic Subagent delegation (`invoke_subagent`), the Severity-Tiered Remediation Matrix (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`), bounded convergence (`Max 2 Passes`), and `## Self-Review & Adaptation Log` in `report-template.md`.
- **TEST_FIRST**:
  - Test File: `tests/test_implement_skill.py`
  - Test Cases:
    - `test_implement_skills_and_templates_exist`
    - `test_implement_files_are_identical`
    - `test_implement_skill_has_phase_4_5_review_adapt_loop`
    - `test_report_template_has_self_review_log`
- **IMPLEMENT**: Create `tests/test_implement_skill.py` with the above assertions.
- **MIRROR**: `tests/test_specify_format.py` and `tests/test_code_review_skill.py`
- **IMPORTS**: `unittest`, `from pathlib import Path`
- **GOTCHA**: Always read files with `encoding="utf-8"` to avoid Windows cp1252 decoding errors on box-drawing or arrow characters.
- **MICRO_VALIDATE**:
  ```bash
  python -m unittest tests/test_implement_skill.py
  python .agents/scripts/verify_shift_left.py --changed
  ```

### Task 2: Update `implement/SKILL.md` and `implement/resources/report-template.md` (GREEN)
- **ACTION**:
  1. Update `.agents/skills/implement/SKILL.md` and `template/.agents/skills/implement/SKILL.md` to add `## Phase 4.5 — REVIEW, SIMPLIFY & ADAPT` between Phase 4 and Phase 5, and update Phase 7 (PR body), Phase 8 (Output summary), Failure Handling, and Success Criteria (`REVIEW_ADAPT_PASS`).
  2. Update `.agents/skills/implement/resources/report-template.md` and `template/.agents/skills/implement/resources/report-template.md` to include `| Self-Review & Adapt | [done] Pass | N findings adapted |` in Validation Results and the `## Self-Review & Adaptation Log` table.
- **TEST_FIRST**: Verified by failing tests in `tests/test_implement_skill.py` from Task 1.
- **IMPLEMENT**:
  - In `Phase 4.5 — REVIEW, SIMPLIFY & ADAPT`:
    - Step 1: Gather working tree diff (`git status --short`, `git diff HEAD`, plus newly created untracked files).
    - Step 2: Spawn a **Fresh-Context Critic Subagent** (`invoke_subagent` with `research` or read-only critic role) so the review is free from implementation confirmation bias. Provide the subagent with the plan's Acceptance Criteria, changed/untracked files, the 5-part Shift-Left Review Rubric (Security, Architecture & Boundaries, Reuse/Anti-WET, Code Smells, Consistency), and `simplifier` targets.
    - Step 3: Apply the **Severity-Tiered Remediation Matrix**:
      - `CRITICAL` / `HIGH`: Mandatory Auto-Adapt via TDD micro-loop (write/update failing test → minimal code fix → run `verify_shift_left.py --changed` and targeted test).
      - `MEDIUM` (including `simplifier` targets): Auto-Adapt & Simplify (flatten deep nesting, remove dead code/debug logs, eliminate duplication while keeping tests green).
      - `LOW`: Log in report under `Self-Review & Adaptation Log` without unnecessary churn.
    - Step 4: **Bounded Convergence (Max 2 Passes)**:
      - If Pass 1 modified any files, re-run Phase 4 validations and perform at most one verification pass (Pass 2) on the remediated files.
      - If a `CRITICAL` or `HIGH` blocker remains unresolved after 2 passes or conflicts with the user's explicit plan, pause before Phase 6 (COMMIT) and escalate via `ask_question`.
- **MIRROR**: `.agents/skills/implement/SKILL.md` and `.agents/skills/code-review/SKILL.md`
- **IMPORTS**: N/A (Markdown skill specifications)
- **GOTCHA**: Keep all shell commands in `implement/SKILL.md` cross-platform safe (PowerShell & Bash compatible; no Unix-only `grep`, `xargs`, or `2>/dev/null`). Ensure `.agents/skills/implement/` and `template/.agents/skills/implement/` are byte-for-byte identical.
- **MICRO_VALIDATE**:
  ```bash
  python -m unittest tests/test_implement_skill.py
  python .agents/scripts/verify_shift_left.py --changed
  ```

### Task 3: Update Workflow Documentation (`AGENTS.md`, `AGENTS.md.template`, `README.md`, `PLUGIN_README.md`)
- **ACTION**: Update `AGENTS.md`, `template/AGENTS.md.template`, `README.md`, and `template/PLUGIN_README.md` so the documented Phase 3 (`/implement`) workflow reflects the integrated Critic Subagent review, simplification, and self-adaptation loop prior to committing and opening a PR.
- **TEST_FIRST**: Add assertion in `tests/test_implement_skill.py` (`test_agents_md_documents_review_adapt_in_implement`) verifying both `AGENTS.md` and `template/AGENTS.md.template` mention the self-review and adaptation step in Phase 3.
- **IMPLEMENT**: Update Phase 3 in `AGENTS.md` and `template/AGENTS.md.template`, plus `/implement` descriptions in `README.md` and `template/PLUGIN_README.md`.
- **MIRROR**: `AGENTS.md` and `template/AGENTS.md.template`
- **IMPORTS**: N/A
- **GOTCHA**: Preserve `{{PROJECT_NAME}}` and `{{TECH_STACK}}` placeholders in `template/AGENTS.md.template`.
- **MICRO_VALIDATE**:
  ```bash
  python -m unittest tests/test_implement_skill.py
  python .agents/scripts/verify_shift_left.py --changed
  ```

### Task 4: Deploy Updated Skills to Global Antigravity Plugin & Run Full Suite
- **ACTION**: Run `python harness.py update --force` to synchronize the updated `implement` skill and consolidated rules into the global Antigravity plugin (`~/.gemini/config/plugins/my-harness`), then execute the full verification suite.
- **TEST_FIRST**: Existing suite (`tests/test_implement_skill.py` + `python -m unittest discover tests`).
- **IMPLEMENT**: Execute `python harness.py update --force`.
- **MIRROR**: `.agents/PRPs/plans/completed/specify-handoff-format.plan.md` (Task 3)
- **IMPORTS**: N/A
- **GOTCHA**: Verify `git status --short` after plugin deployment to ensure no temporary artifacts remain in the working tree.
- **MICRO_VALIDATE**:
  ```bash
  python -m unittest discover tests
  python .agents/scripts/verify_shift_left.py --all-checks
  ```

---

## Test-Driven Strategy

All implementation MUST be preceded by writing failing tests in `tests/test_implement_skill.py`.

### Unit Tests
| Test | Input | Expected Output | Edge Case? |
|---|---|---|---|
| `test_implement_skills_and_templates_exist` | Project & template paths | Both `SKILL.md` and `report-template.md` exist | No |
| `test_implement_files_are_identical` | File contents of project & template | Byte-for-byte equality | Yes (prevents drift) |
| `test_implement_skill_has_phase_4_5_review_adapt_loop` | `implement/SKILL.md` | Contains `## Phase 4.5 — REVIEW, SIMPLIFY & ADAPT`, `invoke_subagent`, severity matrix, and `Max 2 Passes` | Yes |
| `test_report_template_has_self_review_log` | `report-template.md` | Contains `## Self-Review & Adaptation Log` | No |
| `test_agents_md_documents_review_adapt_in_implement` | `AGENTS.md` & `AGENTS.md.template` | Phase 3 mentions autonomous review and adaptation before commit/PR | No |

### Edge Cases Checklist
- [x] Zero findings in Phase 4.5 (fast-path directly to Phase 5 Report without redundant re-validation)
- [x] Unresolved blocker after 2 passes (circuit breaker halts before commit and escalates via `ask_question`)
- [x] Untracked newly created files included alongside `git diff HEAD` during Phase 4.5 inspection
- [x] Cross-platform shell safety (no Unix-only syntax in `implement/SKILL.md`)

---

## Validation Commands

### Level 0: Shift-Left Pre-Flight Scanner (< 1s)
```bash
python -c "import os, subprocess, sys; p = '.agents/scripts/verify_shift_left.py'; p = p if os.path.exists(p) else os.path.expanduser('~/.gemini/config/plugins/my-harness/scripts/verify_shift_left.py'); sys.exit(subprocess.call([sys.executable, p, '--changed']) if os.path.exists(p) else 0)"
```

### Level 1: Static & Structural Analysis
```bash
git diff --check
```

### Level 2: Unit Tests
```bash
python -m unittest discover tests
```

### Level 3: Full Harness Verification
```bash
python .agents/scripts/verify_shift_left.py --all-checks
```

---

## Acceptance Criteria
- [ ] All tasks completed
- [ ] All validation commands pass
- [ ] Tests written first (`tests/test_implement_skill.py`) and passing
- [ ] Project and template copies of `implement/SKILL.md` and `report-template.md` are byte-for-byte identical
- [ ] Zero shift-left architectural violations

## Risks
| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Confirmation bias during self-review | High (if same context) | Medium | Explicitly require spawning a fresh-context Critic Subagent (`invoke_subagent`) with read-only scope |
| Infinite review-fix ping-pong loop | Medium | High | Enforce strict `Max 2 Passes` circuit breaker and `LOW` severity log-only policy |
| Drift between `.agents/` and `template/.agents/` | Medium | High | Enforce byte-for-byte equality in `tests/test_implement_skill.py` |

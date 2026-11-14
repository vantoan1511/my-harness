---
name: implement
description: Execute an implementation plan with rigorous validation loops, then automatically commit and create a GitHub PR
---

# PRP Implement

Execute a plan file step-by-step with continuous validation, then seamlessly commit changes and create a pull request. Every change is verified immediately — never accumulate broken state.

**Core Philosophy**: Validation loops catch mistakes early. Run checks after every change. Fix issues immediately. Once validated and reported, seamlessly commit and open a PR without requiring manual follow-up triggers.

**Golden Rule**: If a validation fails, fix it before moving on. Never accumulate broken state. Never commit or open a PR with failing validations.

---

## Phase 0 — DETECT

### Package Manager & Tooling Detection

| File Exists | Package Manager / Tool | Command Prefix / Runner |
|---|---|---|
| `bun.lockb` | bun | `bun run` / `bun test` |
| `pnpm-lock.yaml` | pnpm | `pnpm run` / `pnpm test` |
| `yarn.lock` | yarn | `yarn` / `yarn test` |
| `package-lock.json` | npm | `npm run` / `npm test` |
| `pyproject.toml` or `requirements.txt` | uv / pip / pytest | `pytest` / `python -m pytest` |
| `Cargo.toml` | cargo | `cargo test` / `cargo clippy` |
| `go.mod` | go | `go test ./...` / `go vet ./...` |

### Validation Scripts

Check `package.json` (or equivalent build / configuration file) for available scripts using file reading tools or:

```bash
# For Node.js projects (PowerShell & Bash safe)
python -c "import json; print(json.load(open('package.json')).get('scripts', {}))"
```

Note available commands for: type-check, lint, test, build.

---

## Phase 1 — LOAD

### Parse Arguments & Execution Mode

Parse `$ARGUMENTS` for the plan file path and optional execution mode flags:

| Flag / Plan Metadata | Mode | Behavior |
|---|---|---|
| *(default)* | **Standard PR Mode** | Execute plan, validate, commit locally, push to remote, and create/update a GitHub PR (Phase 7). |
| `--no-pr`, `--local`, `--spike`, or plan metadata `spike: true` / `local: true` | **Spike / Playground / Local-Only Mode** | Execute plan, validate, and create a clean local commit in Phase 6. **SKIP Phase 7 entirely** (do NOT push to remote origin and do NOT run `gh pr create`). |
| `--no-commit` *(with Spike/Local mode)* | **Uncommitted / Staged Local Mode** | Keep changes uncommitted or staged in Phase 6 without creating a commit, and **SKIP Phase 7 entirely**. |

Read the plan file using your file reading tools (e.g., `read_file` on the plan path from `$ARGUMENTS`):

Extract these sections from the plan:
- **Metadata / Frontmatter** — Check for `spike: true`, `local: true`, `GitHub Issue` (`#<number>`), and `Parent Epic` (`#<epic>`)
- **Summary** — What is being built
- **Patterns to Mirror** — Code conventions to follow
- **Files to Change** — What to create or modify
- **Step-by-Step Tasks** — Implementation sequence
- **Validation Commands** — How to verify correctness
- **Acceptance Criteria** — Definition of done

If the file doesn't exist or isn't a valid plan:
```
Error: Plan file not found or invalid.
Run /specify <intent> or /prp-plan <feature-description> to create a plan first.
```

**CHECKPOINT**: Plan loaded. All sections identified. Tasks extracted.

---

## Phase 2 — PREPARE

### Git State Verification

```bash
git branch --show-current
git status --porcelain
```

### Branch Decision

| Current State | Action |
|---|---|
| On feature branch | Use current branch |
| On main / master, clean working tree | Create feature branch: `git checkout -b feat/issue-<number>-{plan-name}` (or `feat/{plan-name}` if no issue) |
| On main / master, dirty working tree | **STOP** — Ask user to stash or commit first |
| In a git worktree for this feature | Use the worktree |

### Transition Project Status to `In Progress` (if linked to a GitHub Issue)

When `GitHub Issue` `#<number>` is present in the plan metadata, move the ticket on the GitHub Project board to `In Progress`:
```bash
python -c "import os, subprocess, sys; p = '.agents/scripts/gh_project.py'; p = p if os.path.exists(p) else os.path.expanduser('~/.gemini/config/plugins/my-harness/scripts/gh_project.py'); subprocess.call([sys.executable, p, 'set-status', '<ISSUE_NUMBER>', 'In Progress']) if os.path.exists(p) else 0"
```

### Sync Remote

```bash
git pull --rebase origin HEAD
```

**CHECKPOINT**: On correct branch. Working tree ready. Remote synced.

---

## Phase 3 — EXECUTE

Process each task from the plan sequentially.

### Per-Task Shift-Left Loop

For each task in **Step-by-Step Tasks**:

1. **Read MIRROR reference** — Open the pattern file referenced in the task's MIRROR field. Understand the convention before writing code.

2. **Write Tests First (RED)** — Write failing tests as specified in the `TEST_FIRST` field using the project's test runner.

3. **Validate Test Failure** — Run the test command to ensure it fails with the expected assertion error.

4. **Implement Minimal Code (GREEN)** — Write only the code necessary to make the test pass. Follow discovered patterns and avoid speculative code.

5. **Run Shift-Left Micro-Validation Immediately** — After EVERY file change:
   ```bash
   # 1. Fast architectural & static pre-flight (< 0.5s)
   python -c "import os, subprocess, sys; p = '.agents/scripts/verify_shift_left.py'; p = p if os.path.exists(p) else os.path.expanduser('~/.gemini/config/plugins/my-harness/scripts/verify_shift_left.py'); sys.exit(subprocess.call([sys.executable, p, '--changed']) if os.path.exists(p) else 0)"

   # 2. Type check & fast task test
   [MICRO_VALIDATE command from task, or configured test/type-check command]
   ```
   **RULE**: If tests, type-check, lint, or pre-flight fails → STOP and fix the issue before touching another file or proceeding to the next task. Never accumulate broken state.

6. **Track progress** — Log: `[done] Task N: [task name] — complete`

### Handling Deviations

If implementation must deviate from the plan:
- Note **WHAT** changed
- Note **WHY** it changed
- Continue with the corrected approach
- These deviations will be captured in the final report

**CHECKPOINT**: All tasks executed. Deviations logged. Zero debt accumulated.

---

## Phase 4 — VALIDATE

Run the comprehensive validation suite. Because shift-left micro-validation ran per-task, this phase confirms full-system regression safety.

### Level 0: Shift-Left Pre-Flight Verification

```bash
python -c "import os, subprocess, sys; p = '.agents/scripts/verify_shift_left.py'; p = p if os.path.exists(p) else os.path.expanduser('~/.gemini/config/plugins/my-harness/scripts/verify_shift_left.py'); sys.exit(subprocess.call([sys.executable, p, '--changed']) if os.path.exists(p) else 0)"
```
Zero architectural violations, zero banned imports, zero raw controls or style violations.

### Level 1: Static Analysis

```bash
# Type checking & linting configured for project
python -c "import os, subprocess, sys; p = '.agents/scripts/verify_shift_left.py'; p = p if os.path.exists(p) else os.path.expanduser('~/.gemini/config/plugins/my-harness/scripts/verify_shift_left.py'); sys.exit(subprocess.call([sys.executable, p, '--lint', '--type-check']) if os.path.exists(p) else 0)"
# Or native commands: npm run type-check && npm run lint / cargo clippy / ruff check / go vet
```

If lint errors remain after auto-fix, fix manually.

### Level 2: Full Unit Tests

Verify all tests pass without regressions:

```bash
# Run project test suite
python -c "import os, subprocess, sys; p = '.agents/scripts/verify_shift_left.py'; p = p if os.path.exists(p) else os.path.expanduser('~/.gemini/config/plugins/my-harness/scripts/verify_shift_left.py'); sys.exit(subprocess.call([sys.executable, p, '--test']) if os.path.exists(p) else 0)"
# Or native commands: npm test / cargo test / pytest / go test ./...
```
- Ensure test coverage exists for every new function
- Cover edge cases listed in the plan
- If a test fails → fix the implementation (not the test, unless the test assertion itself was wrong)

### Level 3: Build Check

```bash
[project build command: e.g. npm run build, cargo build, go build]
```

Build must succeed with zero errors.

### Level 4: Integration Testing (if applicable)

Run integration or end-to-end tests if defined in the project.

### Level 5: Edge Case Testing

Run through edge cases from the plan's Test-Driven Strategy checklist.

**CHECKPOINT**: All validation levels pass. Zero errors.

---

## Phase 4.5 — REVIEW, SIMPLIFY & ADAPT (Self-Healing Loop)

Run an autonomous, semantic self-review, simplification, and adaptation loop on the uncommitted working tree diff BEFORE generating reports or committing code.

**Core Philosophy**: Mechanical validation (Phase 4) proves the code compiles and passes tests; semantic review checks architecture, security, design patterns, and simplicity. Reviewing in the same agent context suffers from confirmation bias, so Phase 4.5 delegates review to an isolated Critic Subagent.

### Step 1: Collect Working Tree Changes

Inspect all modified and untracked files:
```bash
git status --short
git diff HEAD
```
For untracked files (`??`), read their contents so the critic reviews complete implementations.

### Step 2: Spawn Fresh-Context Critic Subagent

Invoke a read-only Critic Subagent via `invoke_subagent` to evaluate the uncommitted diff without confirmation bias:
- **Role**: `Code Critic & Quality Auditor`
- **TypeName**: `research`
- **Subagent Prompt Content**:
  1. Provide the Plan Summary and Acceptance Criteria from Phase 1.
  2. Provide the diff (`git diff HEAD`) and paths/contents of untracked files.
  3. Rubric based on the Shift-Left Quality & Architecture Constitution and Simplifier:
     - **Security**: Zero secrets, safe error handling, input validation, safe execution paths.
     - **Architecture & Boundaries**: Layer encapsulation, correct dependency direction, zero banned imports.
     - **Reuse & Anti-WET**: Reusing existing utilities, no duplicate logic or models.
     - **Code Smells**: Deep nesting (>3 levels), large functions (>50 lines), magic constants, dead code, stray debug logs.
     - **Simplifier Targets**: Clarity over cleverness, early returns, removing unneeded single-use abstractions.
  4. Response Schema:
     ```markdown
     ### Review Findings
     - **Decision**: APPROVE | ADAPT_REQUIRED | ESCALATE
     - **Findings**:
       - `[CRITICAL|HIGH|MEDIUM|LOW]` `path/to/file:line` — **Category**: [Security | Architecture | Reuse/DRY | Code Smell | Simplifier]
         - **Issue**: [Concise description]
         - **Adaptation**: [Concrete minimal fix required]
     ```

### Step 3: Apply Severity-Tiered Remediation Matrix

Process findings reported by the Critic Subagent:

| Severity | Scope | Required Action in Phase 4.5 |
|---|---|---|
| **CRITICAL** | Security vulnerabilities, secrets, broken boundary violations | **Mandatory Auto-Adapt**: Write/update failing test (RED), apply fix (GREEN), run micro-validation. Block commit if unresolved. |
| **HIGH** | Logic bugs, contract mismatches, unhandled errors, architecture drift | **Mandatory Auto-Adapt**: Write/update failing test (RED), apply fix (GREEN), run micro-validation. Block commit if unresolved. |
| **MEDIUM** | DRY violations, deep nesting (>3 levels), large functions (>50 LOC), dead code, stray debug logs, `simplifier` targets | **Auto-Adapt & Simplify**: Apply minimal behavior-preserving simplification or refactoring and re-verify tests. |
| **LOW** | Minor stylistic preferences or acceptable trade-offs | **Log Only**: Record in report under *Self-Review & Adaptation Log* without unnecessary code churn. |

### Step 4: Bounded Convergence (Max 2 Passes)

To prevent infinite loops while guaranteeing quality:
- **Pass 1**: Complete review of the working tree → Apply adaptations for `CRITICAL`, `HIGH`, and `MEDIUM` items.
- **Fast Path**: If Pass 1 finds 0 `CRITICAL`/`HIGH`/`MEDIUM` items (or only `LOW`), proceed immediately to Phase 5.
- **Pass 2 (Verification Pass)**: If Pass 1 modified code, re-run Phase 4 validation suite and have the Critic Subagent perform a focused verification pass on the remediated files.
- **Circuit Breaker / Escalation Gate**:
  - Maximum of 2 review passes allowed.
  - If any `CRITICAL` or `HIGH` blocker remains unresolved after 2 passes, or if a finding conflicts with the user's explicit plan or specifications, STOP before Phase 6 (COMMIT) and escalate to the user via `ask_question`.

**CHECKPOINT**: Working tree reviewed. All high/medium findings adapted and simplified. Zero blockers.

---

## Phase 5 — REPORT

### Create Implementation Report

```bash
mkdir -p .agents/PRPs/reports
```

Write report to `.agents/PRPs/reports/{plan-name}-report.md` following the template in [`resources/report-template.md`](./resources/report-template.md) (including Summary, Assessment vs Reality, Tasks Completed, Validation Results, Files Changed, Deviations, Tests Written, and Next Steps).

### Update PRD (if applicable)

If this implementation was for a PRD phase:
1. Update the phase status from `in-progress` to `complete`
2. Add report path as reference

### Persist Curated Gotchas & Knowledge
Extract Self-Review & Adaptation findings and deviations into persistent gotchas:
```bash
python .agents/scripts/curate_knowledge.py --persist
```

### Archive Plan

```bash
mkdir -p .agents/PRPs/plans/completed
mv "$ARGUMENTS" .agents/PRPs/plans/completed/
```

**CHECKPOINT**: Report created. PRD updated. Plan archived.

---

## Phase 6 — COMMIT

Seamlessly stage and commit all implementation code, tests, reports, and archived plans with a descriptive conventional commit message.

### 0. Check Spike / Local / No-Commit Flags

Check if `$ARGUMENTS` contains `--no-pr`, `--local`, `--spike`, `--no-commit`, or if the plan metadata indicates `spike: true` / `local: true`:
- **If `--no-commit` is specified**:
  - Keep changes uncommitted or staged (`git add -A` if requested, without running `git commit`).
  - **SKIP Phase 7 entirely** (do NOT push to remote origin and do NOT run `gh pr create`) and proceed directly to Phase 8.
- **If `--no-pr`, `--local`, `--spike`, or plan metadata `spike: true` / `local: true` is present**:
  - Proceed with steps 1–4 below to create a clean local commit (or offer to keep changes uncommitted/staged if `--no-commit` is specified).
  - After committing locally, **SKIP Phase 7 entirely**: do NOT push to remote origin and do NOT run `gh pr create`.
  - Print a clean summary:
    ```
    [Spike Completed] Local changes verified and committed locally on branch <branch>. No remote PR was created.
    ```

### 1. Revert Local Development Configs (Safety Guard)

Ensure local development configurations, environment overrides, or debug flags are reverted to production-safe defaults before committing.

### 2. Stage All Changes

```bash
git status --short
git add -A
git diff --cached --stat
```

If nothing is modified or staged (e.g. working tree is already clean):
- Note that working tree is clean.
- Proceed to Phase 7 if commits are ahead of base branch (unless in Spike / Local mode).

### 3. Craft Conventional Commit Message

Derive a conventional commit message from the plan's summary and tasks completed:

```
{type}: {description}
```

- **Type**: `feat` (new feature/capability), `fix` (bug fix), `refactor` (code restructuring), `test` (test additions), `chore` (configuration/dependencies), `perf` (performance), or `docs` (documentation)
- **Rules**:
  - Imperative mood ("add user authentication" not "added...")
  - Lowercase after the type prefix
  - No trailing period
  - Under 72 characters
  - Describe WHAT changed, not HOW

### 4. Commit Changes

```bash
git commit -m "{type}: {description}"
```

Capture short hash:
```bash
git rev-parse --short HEAD
```

**CHECKPOINT**: All changes committed cleanly. Working tree clean.

---

## Phase 7 — PR

> **Mode Gate (Spike / Local-Only Mode Check)**:
> Before executing Phase 7, check if `$ARGUMENTS` contains `--no-pr`, `--local`, `--spike`, or if the plan metadata indicates `spike: true` / `local: true`:
> - **If present (Spike/Local Mode)**:
>   - **SKIP Phase 7 entirely**: Do NOT push to remote origin (`git push`) and do NOT run `gh pr create`.
>   - Print a clean summary: `[Spike Completed] Local changes verified and committed locally on branch <branch>. No remote PR was created.`
>   - Proceed directly to Phase 8.
> - **If omitted (Default Mode)**:
>   - Preserve the existing behavior (push and create PR) below.

Seamlessly push the feature branch to the remote and create or update the GitHub Pull Request.

### 1. Validate PR Preconditions

```bash
git branch --show-current
git status --short
git log origin/main..HEAD --oneline
```

| Check | Condition | Action if Failed |
|---|---|---|
| Not on base branch | Current branch ≠ `main` / `master` | Stop: "Cannot create PR from base branch." |
| Clean working directory | No uncommitted changes | Re-run staging/commit from Phase 6 |
| Commits ahead | `git log origin/main..HEAD` not empty | Stop: "No commits ahead of base. Nothing to PR." |

### 2. Check for Existing PR

```bash
gh pr view --json number,url 2>$null || gh pr list --state open --json number,url --jq ".[0]"
```

- If a PR already exists for this branch:
  ```bash
  git push origin HEAD
  ```
  Note the existing PR URL and number. Proceed to Phase 8.

### 3. Discover PR Template & Structure Body

Extract any associated `GitHub Issue` (`#<number>`) from the plan metadata, source PRD, or branch name.

Check for PR templates in:
1. `.github/PULL_REQUEST_TEMPLATE/`
2. `.github/PULL_REQUEST_TEMPLATE.md`
3. `.github/pull_request_template.md`

If found, fill in sections using the implementation findings and include `Closes #<issue>` plus verified Acceptance Criteria (`- [x]`) in the related issues section. Every PR created for a GitHub Issue MUST resolve its linked issue on merge using `Closes #<issue>` (never leave an implemented plan's issue half-open with `Refs #<issue>`; if remaining work was discovered or deferred, split it into a separate backlog issue first).
If not found, use default format:

```markdown
## Summary
{1-2 sentence description from plan summary}

{If an issue/ticket number was found: "Closes #<issue>"}

## Changes
{bulleted list of tasks completed}

## Acceptance Criteria Verified
{checked `- [x]` list from linked GitHub Issue / plan}

## Files Changed
{table or summary of changed files}

## Validation
- Shift-Left Pre-Flight: Passed (zero violations)
- Type Check & Lint: Passed
- Unit Tests: Passed
- Build: Passed
- Self-Review & Adapt Loop: Passed (critic audited, all high/medium findings remediated)

## Artifacts
- Report: `.agents/PRPs/reports/{name}-report.md`
- Completed Plan: `.agents/PRPs/plans/completed/{name}.plan.md`
```

### 4. Push to Remote

```bash
git push -u origin HEAD
```

If push fails due to divergence:
```bash
git fetch origin
git rebase origin/main
git push -u origin HEAD
```

### 5. Create Pull Request

```bash
gh pr create \
  --title "{PR title}" \
  --base main \
  --body "{PR body}"
```

Verify PR details (including `closingIssuesReferences` when an issue number was linked):
```bash
gh pr view --json number,url,title,state,baseRefName,headRefName,additions,deletions,changedFiles,closingIssuesReferences
```

### Fallback if GitHub CLI Unavailable
If `gh` CLI is not installed or unauthenticated:
- The branch is already pushed to remote via `git push -u origin HEAD`.
- Note the push succeeded and display the GitHub URL to create the PR manually (e.g. `https://github.com/{owner}/{repo}/pull/new/{branch}`).

**CHECKPOINT**: Remote branch pushed. Pull request created or updated.

---

## Phase 8 — OUTPUT

If running in **Spike / Local-Only Mode** (`--no-pr`, `--local`, `--spike`, or `spike: true` / `local: true`), include the summary banner:

```
[Spike Completed] Local changes verified and committed locally on branch <branch>. No remote PR was created.
```

Report comprehensive results to user:

```
## Implementation, Commit & PR Complete

- **Plan**: [plan file path] → archived to completed/
- **Branch**: [current branch name]
- **Status**: [done] All tasks complete, verified, committed, and PR created

### Validation Summary

| Check | Status |
|---|---|
| Shift-Left Pre-Flight | [done] Zero violations |
| Type Check | [done] |
| Lint | [done] |
| Tests | [done] (N written) |
| Build | [done] |
| Integration | [done] or N/A |
| Self-Review & Adapt | [done] (N findings adapted) |

### Commit

- **Hash**: {short_hash}
- **Message**: {type}: {description}
- **Files**: {count} file(s) changed

### Pull Request

- **PR**: #{number} — {title}
- **URL**: {url}
- **Branch**: {head} → {base}
- **Status**: {state}

### Artifacts
- Report: `.agents/PRPs/reports/{name}-report.md`
- Archived Plan: `.agents/PRPs/plans/completed/{name}.plan.md`

### PRD Progress (if applicable)
| Phase | Status |
|---|---|
| Phase 1 | [done] Complete |
| Phase 2 | [next] |
| ... | ... |

> Next step: Open PR in browser with `gh pr view {number} --web`, or merge via `gh pr merge {number}`.
```

---

## Phase 9 — MERGE, CLOSE ISSUE & FOLLOW-UP TRIAGE

> **Mode Gate (Spike / Local-Only Mode)**: Skip Phase 9 entirely when `--no-pr`, `--local`, `--spike`, `--no-commit`, or `spike: true` / `local: true` is active.

### Step 1: Known Issues & Follow-Up Triage (`Found Known Issues? → Create New Issue`)

Before or immediately after merging the PR, harvest candidate follow-up items from:
1. Deferred `LOW` / `MEDIUM` findings logged in Phase 4.5 `Self-Review & Adaptation Log`.
2. `Deviations from Plan` and `Issues Encountered` in `.agents/PRPs/reports/{name}-report.md`.
3. Any `Out of Scope` / `NOT Building` edge cases uncovered during execution.

If one or more candidate known issues exist:
- Prompt the user via `ask_question` (`is_multi_select: true`): *"Found known issues or follow-up items. Which ones should I create as new GitHub Project issues?"*
- For each selected item, create a structured GitHub Issue matching `.github/ISSUE_TEMPLATE/task.yml` (`Parent Epic`, `Summary`, `Acceptance Criteria`, and `Technical Notes / Dependencies` referencing `Discovered in PR #<pr_number>`), add it to the Project (`gh project item-add`), and set `Status = Todo` and `Priority`:
  ```powershell
  $url = gh issue create --title "<Business-oriented follow-up title>" --body $followupBody
  gh project item-add <project-number> --owner <owner> --url $url
  ```
- Record created follow-up issue numbers under `## Known Issues & Follow-Up Tickets` in the implementation report.

### Step 2: Merge PR & Close Issue (`Merge & Close Issue`)

When the user confirms merging (or passes `--merge`):
1. Verify CI checks pass:
   ```bash
   gh pr checks <number>
   ```
2. Merge PR, delete branch, and sync local base branch:
   ```bash
   gh pr merge <number> --squash --delete-branch
   git checkout main
   git pull origin main
   ```
3. Verify the linked GitHub Issue `#<issue>` is closed (`gh issue view <issue> --json state`) and transition its GitHub Project status to `Done`:
   ```bash
   python -c "import os, subprocess, sys; p = '.agents/scripts/gh_project.py'; p = p if os.path.exists(p) else os.path.expanduser('~/.gemini/config/plugins/my-harness/scripts/gh_project.py'); subprocess.call([sys.executable, p, 'set-status', '<ISSUE_NUMBER>', 'Done']) if os.path.exists(p) else 0"
   ```
4. If a `Parent Epic` `#<epic>` is linked, refresh its Roadmap dates:
   ```bash
   python -c "import os, subprocess, sys; p = '.agents/scripts/gh_project.py'; p = p if os.path.exists(p) else os.path.expanduser('~/.gemini/config/plugins/my-harness/scripts/gh_project.py'); subprocess.call([sys.executable, p, 'rollup-epic', '<EPIC_NUMBER>']) if os.path.exists(p) else 0"
   ```

---

## Handling Failures

### Type Check Fails
1. Read the error message carefully
2. Fix the type error in the source file
3. Re-run type-check
4. Continue only when clean

### Tests Fail
1. Identify whether the bug is in the implementation or the test
2. Fix the root cause (usually the implementation)
3. Re-run tests
4. Continue only when green

### Lint Fails
1. Run auto-fix first
2. If errors remain, fix manually
3. Re-run lint
4. Continue only when clean

### Build Fails
1. Usually a type or import issue — check error message
2. Fix the offending file
3. Re-run build
4. Continue only when successful

---

## Success Criteria

- **TASKS_COMPLETE**: All tasks from the plan executed
- **TYPES_PASS**: Zero type errors
- **LINT_PASS**: Zero lint errors
- **TESTS_PASS**: All tests green, new tests written
- **BUILD_PASS**: Build succeeds
- **REVIEW_ADAPT_PASS**: Self-review passed with zero unhandled critical/high findings
- **REPORT_CREATED**: Implementation report saved
- **PLAN_ARCHIVED**: Plan moved to `completed/`
- **COMMITTED**: Changes cleanly staged and committed with conventional message
- **PR_CREATED**: Branch pushed to remote and GitHub PR created

---

## Next Steps

- Open PR in browser: `gh pr view <number> --web`
- Run `/code-review <number>` to perform automated review on the PR
- Merge PR via `gh pr merge <number>` when approved
- Run `/prp-plan <next-phase>` if the PRD has more phases

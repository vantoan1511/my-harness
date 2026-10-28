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

Read the plan file using your file reading tools (e.g., `read_file` on `$ARGUMENTS`):

Extract these sections from the plan:
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
| On main / master, clean working tree | Create feature branch: `git checkout -b feat/{plan-name}` |
| On main / master, dirty working tree | **STOP** — Ask user to stash or commit first |
| In a git worktree for this feature | Use the worktree |

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
   python .agents/scripts/verify_shift_left.py --changed

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
python .agents/scripts/verify_shift_left.py --changed
```
Zero architectural violations, zero banned imports, zero raw controls or style violations.

### Level 1: Static Analysis

```bash
# Type checking & linting configured for project
python .agents/scripts/verify_shift_left.py --lint --type-check
# Or native commands: npm run type-check && npm run lint / cargo clippy / ruff check / go vet
```

If lint errors remain after auto-fix, fix manually.

### Level 2: Full Unit Tests

Verify all tests pass without regressions:

```bash
# Run project test suite
python .agents/scripts/verify_shift_left.py --test
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

## Phase 5 — REPORT

### Create Implementation Report

```bash
mkdir -p .agents/PRPs/reports
```

Write report to `.agents/PRPs/reports/{plan-name}-report.md`:

```markdown
# Implementation Report: [Feature Name]

## Summary
[What was implemented]

## Assessment vs Reality

| Metric | Predicted (Plan) | Actual |
|---|---|---|
| Complexity | [from plan] | [actual] |
| Confidence | [from plan] | [actual] |
| Files Changed | [from plan] | [actual count] |

## Tasks Completed

| # | Task | Status | Notes |
|---|---|---|---|
| 1 | [task name] | [done] Complete | |
| 2 | [task name] | [done] Complete | Deviated — [reason] |

## Validation Results

| Level | Status | Notes |
|---|---|---|
| Pre-Flight Scanner | [done] Pass | Zero violations |
| Static Analysis | [done] Pass | |
| Unit Tests | [done] Pass | N tests written |
| Build | [done] Pass | |
| Integration | [done] Pass | or N/A |
| Edge Cases | [done] Pass | |

## Files Changed

| File | Action | Lines |
|---|---|---|
| `path/to/file` | CREATED | +N |
| `path/to/file` | UPDATED | +N / -M |

## Deviations from Plan
[List any deviations with WHAT and WHY, or "None"]

## Issues Encountered
[List any problems and how they were resolved, or "None"]

## Tests Written

| Test File | Tests | Coverage |
|---|---|---|
| `path/to/test` | N tests | [area covered] |

## Knowledge Base Updates (Self-Improving)
[List any new gotchas, architectural decisions, or recipes contributed to `.agents/references/`, or "None"]

## Next Steps
- [ ] Review PR: [PR URL or #<number>]
- [ ] Code review via `/code-review <number>`
- [ ] Merge PR when approved
```

### Update PRD (if applicable)

If this implementation was for a PRD phase:
1. Update the phase status from `in-progress` to `complete`
2. Add report path as reference

### Archive Plan

```bash
mkdir -p .agents/PRPs/plans/completed
mv "$ARGUMENTS" .agents/PRPs/plans/completed/
```

**CHECKPOINT**: Report created. PRD updated. Plan archived.

---

## Phase 6 — COMMIT

Seamlessly stage and commit all implementation code, tests, reports, and archived plans with a descriptive conventional commit message.

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
- Proceed to Phase 7 if commits are ahead of base branch.

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

Check for PR templates in:
1. `.github/PULL_REQUEST_TEMPLATE/`
2. `.github/PULL_REQUEST_TEMPLATE.md`
3. `.github/pull_request_template.md`

If found, fill in sections using the implementation findings.
If not found, use default format:

```markdown
## Summary
{1-2 sentence description from plan summary}

## Changes
{bulleted list of tasks completed}

## Files Changed
{table or summary of changed files}

## Validation
- Shift-Left Pre-Flight: Passed (zero violations)
- Type Check & Lint: Passed
- Unit Tests: Passed
- Build: Passed

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

Verify PR details:
```bash
gh pr view --json number,url,title,state,baseRefName,headRefName,additions,deletions,changedFiles
```

### Fallback if GitHub CLI Unavailable
If `gh` CLI is not installed or unauthenticated:
- The branch is already pushed to remote via `git push -u origin HEAD`.
- Note the push succeeded and display the GitHub URL to create the PR manually (e.g. `https://github.com/{owner}/{repo}/pull/new/{branch}`).

**CHECKPOINT**: Remote branch pushed. Pull request created or updated.

---

## Phase 8 — OUTPUT

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

> Next step: Open PR in browser with `gh pr view {number} --web`, or run `/code-review {number}` for automated review.
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

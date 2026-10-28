---
name: code-review
description: Code review — local uncommitted changes or GitHub PR (pass PR number/URL for PR mode)
---

# Code Review

**Input**: PR number, PR URL, `--pr <branch>`, or empty for local review.

---

## Mode Selection

- If user provides PR number, PR URL, `--pr`, or target branch:
  → Jump to **PR Review Mode**.
- Otherwise:
  → Use **Local Review Mode**.

---

## Local Review Mode

Fast, shift-left quality and security audit of uncommitted working tree changes.

### Phase 1 — GATHER & PRE-FLIGHT

1. Inspect changed files & diff overview:
   ```bash
   git status --short
   git diff --stat HEAD
   ```

2. Run Shift-Left Pre-Flight Scanner (cross-platform compatible):
   ```bash
   python -m scripts.verify_shift_left --changed 2>$null || python -c "import os, subprocess; p=os.path.expanduser('~/.gemini/config/plugins/my-harness/scripts/verify_shift_left.py'); subprocess.run(['python', p, '--changed']) if os.path.exists(p) else None"
   ```

3. Early termination:
   - If no changed files: Stop and inform user: *"Nothing to review."*
   - If shift-left scanner detects blocker violations (secrets, debugger leaks, merge conflict markers): Treat as **CRITICAL/HIGH** blockers immediately.

### Phase 2 — ADAPTIVE SCOPE REVIEW

Avoid reading every file in its entirety to prevent context exhaustion and rate limits:

1. **Diff-First Inspection**: Read `git diff HEAD` to examine changed blocks and immediate context.
2. **Context Expansion**: Only read full files or expanded ranges ($\pm 30$ lines) for:
   - Core domain models, architecture boundaries, security/auth layers.
   - Complex refactorings or public API signatures.
3. **Subagent Delegation for Large Diff**:
   - If total changed files $> 10$ or diff $> 500$ lines, launch a review subagent (e.g. `research` or module-specific reviewer) to evaluate chunks and report structured findings.

Evaluate against the **Shift-Left Quality Review Constitution**:

#### 1. Security Issues (CRITICAL)
- Hardcoded credentials, secrets, tokens, API keys
- Injection risks (SQL, OS command, LDAP, template)
- XSS and unescaped input rendering
- Missing input/boundary validation, unsafe deserialization
- Path traversal vulnerabilities

#### 2. Architecture & Boundary Discipline (HIGH)
- Respect layer boundaries, dependency direction (DIP), and single responsibility (SRP).
- Prohibit band-aid additive branching (e.g. nested `if-else` chains $\ge 3$ branches without lookup tables/strategies).
- Ensure interfaces remain decoupled from concrete 3rd-party clients.

#### 3. Code Reuse, Anti-WET & Design (HIGH)
- Identify unnecessary duplication across utilities, styles, and logic.
- Avoid premature or leaky abstractions; favor simplicity (KISS, YAGNI).

#### 4. Code Smells & Maintainability (HIGH)
- Large functions (>50 lines) or overly complex files (>800 lines).
- Deep nesting (>3 levels).
- Magic strings, numbers, untyped blobs (prefer typed models, enums, constants).
- Silent error swallowing (`catch (e) {}` with no logging or recovery).

#### 5. Consistency & Native Repository Feel (MEDIUM)
- Naming conventions, error structures, state management, idiomatic formatting.
- Semantic constants over ad-hoc literals.

### Phase 3 — REPORT & GATES

Generate structured report:
- Severity: CRITICAL, HIGH, MEDIUM, LOW
- Location: `file_path:line_number`
- Issue description and concrete suggested fix
- Block merges/commits if CRITICAL or HIGH issues exist.

---

## PR Review Mode

Comprehensive GitHub PR review with branch isolation, targeted testing, and non-destructive context gathering.

### Phase 1 — FETCH & METADATA

1. Extract PR number or search by branch:
   ```bash
   # Branch input:
   gh pr list --head <branch> --json number,title
   # View PR summary:
   gh pr view <NUMBER> --json number,title,body,author,baseRefName,headRefName,changedFiles,additions,deletions
   ```

2. Inspect PR stats and changed files list:
   ```bash
   gh pr diff <NUMBER> --name-only
   ```

### Phase 2 — NON-DESTRUCTIVE CONTEXT GATHERING

> [!WARNING]
> **Workspace Preservation**: Do NOT run `gh pr checkout <NUMBER>` directly inside a dirty or active working branch to avoid overwriting uncommitted work or causing branch drift.

Use non-destructive inspection techniques:
1. **Targeted Git Inspection**:
   ```bash
   git fetch origin <headRefName> --depth=50
   git show origin/<headRefName>:<path/to/file>
   ```
2. **Isolated Worktree (Only for heavy local testing if needed)**:
   ```bash
   git worktree add .agents/worktree-pr-<NUMBER> origin/<headRefName>
   # Cleanup after completion: git worktree remove --force .agents/worktree-pr-<NUMBER>
   ```

3. Read contextual guidelines:
   - Project rules: `AGENTS.md`, `GEMINI.md`, `.agents/rules/`
   - PR description and linked issues for intended behavior.

### Phase 3 — ADAPTIVE REVIEW & CATEGORIZATION

1. Review unified diff first (`gh pr diff <NUMBER>`).
2. Read surrounding code context only where logic depends on outside states or invariants.
3. Categorize findings:

| Category | Key Verifications |
|---|---|
| **Architecture** | Layer boundaries, anti-spaghetti, extensible patterns |
| **Correctness** | Logic bugs, null safety, off-by-one, race conditions, edge cases |
| **Type Safety** | No arbitrary `any`, proper type narrowing, sound interfaces |
| **Security** | Secrets, injections, path traversals, authn/authz gaps |
| **Performance** | N+1 queries, unbounded iterations, memory leaks, I/O blocking |
| **Maintainability** | Magic literals, deep nesting, missing tests, unhandled errors |

Severities:
- **CRITICAL**: Immediate security or data loss hazard. (Blocker)
- **HIGH**: Logic flaw, breaking contract, or high-risk defect. (Blocker)
- **MEDIUM**: Code smell, architectural drift, or missing best practice.
- **LOW**: Minor stylistic nit, comment formatting.

### Phase 4 — IMPACTED / TARGETED VALIDATION

Avoid running unconstrained full-repository test suites blindly. Execute fast checks first, followed by targeted tests covering modified paths:

**Node.js / TypeScript**:
```bash
# Type check (fast)
npx tsc --noEmit
# Lint
npm run lint -- --max-warnings=0
# Targeted Unit Test (pass changed test file or pattern)
npm test -- <path/to/test-or-spec>
```

**Python**:
```bash
# Targeted pytest on modified test modules
pytest <path/to/test_file.py>
```

**Rust**:
```bash
cargo clippy -- -D warnings
cargo test <test_name_filter>
```

**Go**:
```bash
go vet ./...
go test -run <TestPattern> ./<package_path>/...
```

*Note: Offer the user the option to run the full comprehensive test suite if all targeted checks pass.*

### Phase 5 — DECISION MATRIX

| Condition | Decision |
|---|---|
| Zero CRITICAL/HIGH issues, all targeted validation passes | **APPROVE** |
| Only MEDIUM/LOW issues, validation passes | **APPROVE** with suggestions |
| Any HIGH issue or failed validation | **REQUEST CHANGES** |
| Any CRITICAL issue (security/data integrity) | **BLOCK** |
| Draft PR | **COMMENT** only |

### Phase 6 — ARTIFACT GENERATION

Write report to `.agents/reviews/pr-<NUMBER>-review.md`:

```markdown
# PR Review: #<NUMBER> — <TITLE>

**Reviewed**: <date>
**Author**: <author>
**Branch**: <headRef> → <baseRef>
**Decision**: APPROVE | REQUEST CHANGES | BLOCK

## Summary
<Concise assessment of changes and risk level>

## Findings

### CRITICAL
<findings or "None">

### HIGH
<findings or "None">

### MEDIUM
<findings or "None">

### LOW
<findings or "None">

## Validation Results
| Check | Target / Command | Result |
|---|---|---|
| Type Check | ... | Pass / Fail / Skipped |
| Linter | ... | Pass / Fail / Skipped |
| Targeted Tests | ... | Pass / Fail / Skipped |

## Files Reviewed
<list of modified files and review depths>
```

### Phase 7 — PUBLISH (HUMAN APPROVAL GATE)

> [!IMPORTANT]
> **Human Approval Gate**: Never publish review judgments (`APPROVE` / `REQUEST_CHANGES`) directly to remote GitHub repositories without explicit confirmation from the user.

When the user gives approval or specifies `--submit`:

```bash
# Post comment summary
gh pr review <NUMBER> --comment --body "<summary_content>"

# Post review approval
gh pr review <NUMBER> --approve --body "<summary_content>"

# Post request changes
gh pr review <NUMBER> --request-changes --body "<required_fixes>"
```

For batch inline comments, save payload to a temporary JSON file and submit via GitHub API (PowerShell & Bash safe):
```bash
gh api "repos/{owner}/{repo}/pulls/<NUMBER>/reviews" -f event="COMMENT" -f body="Automated Code Review" --input comments.json
```

### Phase 8 — SUMMARY OUTPUT

Present summary directly in chat:
- PR title & link
- Decision summary
- Count of CRITICAL / HIGH / MEDIUM / LOW findings
- Link to local review artifact
- Suggested next actions

---

## Edge Cases & Fail-safes

- **No `gh` CLI or Unauthenticated**: Fall back cleanly to local-only git diff review and report locally.
- **Large PRs (>10 files or >500 LOC)**: Automatically trigger adaptive sampling; prioritize interface contracts, security layers, and data mutations; recommend subagent delegation.
- **Diverged / Out-of-date Branches**: Check if base branch is behind `origin/<baseRef>` and warn before running validation tests.

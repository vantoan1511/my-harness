---
name: pr
description: Create a GitHub PR from current branch with unpushed commits — discovers templates, analyzes changes, pushes
---

# Create Pull Request

**Input**: `$ARGUMENTS` — optional, may contain a base branch name and/or flags (e.g., `--draft`, `--base <branch>`).

**Parse `$ARGUMENTS` & Resolve `<base>`**:
- Extract any recognized flags (`--draft`) and optional `--base <branch>`
- Treat remaining non-flag text as the base branch name
- If no base branch is explicitly provided in `$ARGUMENTS`, resolve `<base>` in order:
  1. `git config --get branch.<current-branch>.base` (if set when branching from an integration branch)
  2. `Base Branch` / `base_branch` in any linked PRP plan metadata
  3. Closest ancestor remote integration branch (e.g. `origin/feat/*` ahead of `origin/main` that is an ancestor of `HEAD` or has a closer merge-base than `origin/main`)
  4. Default to `main`

---

## Phase 1 — VALIDATE

Check preconditions:

```bash
git branch --show-current
git status --short
git log origin/<base>..HEAD --oneline
```

| Check | Condition | Action if Failed |
|---|---|---|
| Not on base branch | Current branch ≠ base | Stop: "Switch to a feature branch first." |
| Clean working directory | No uncommitted changes | Warn: "You have uncommitted changes. Commit or stash first. Use `/commit` to commit." |
| Has commits ahead | `git log origin/<base>..HEAD` not empty | Stop: "No commits ahead of `<base>`. Nothing to PR." |
| No existing PR | `gh pr list --head <branch> --json number` is empty | Stop: "PR already exists: #<number>. Use `gh pr view <number> --web` to open it." |

If all checks pass, proceed.

---

## Phase 2 — DISCOVER

### PR Template

Search for PR template in order:

1. `.github/PULL_REQUEST_TEMPLATE/` directory — if exists, list files and let user choose (or use `default.md`)
2. `.github/PULL_REQUEST_TEMPLATE.md`
3. `.github/pull_request_template.md`
4. `docs/pull_request_template.md`

If found, read it and use its structure for the PR body.

### Commit Analysis

```bash
git log origin/<base>..HEAD --format="%h %s" --reverse
```

Analyze commits to determine:
- **PR title**: Use conventional commit format with type prefix — `feat: ...`, `fix: ...`, etc.
  - If multiple types, use the dominant one
  - If single commit, use its message as-is
- **Change summary**: Group commits by type/area

### File Analysis

```bash
git diff origin/<base>..HEAD --stat
git diff origin/<base>..HEAD --name-only
```

Categorize changed files: source, tests, docs, config, migrations.

### PRP Artifacts

Check for related PRP artifacts:
- `.agents/PRPs/reports/` — Implementation reports
- `.agents/PRPs/plans/` — Plans that were executed
- `.agents/PRPs/prds/` — Related PRDs

Reference these in the PR body if they exist.

### Linked GitHub Issue

Extract any associated `GitHub Issue` (`#<number>`) in priority order from:
1. Linked PRP plan metadata (`- **GitHub Issue**: #<number>`), `.agents/PRPs/reports/`, or `.agents/PRPs/prds/`
2. Current branch name (e.g., `feat/issue-<number>-...`, `fix/issue-<number>-...`, or `<type>/<number>-...`)
3. Commit messages in `origin/<base>..HEAD` (`Closes #<N>`, `Fixes #<N>`, `Refs #<N>`)

---

## Phase 3 — PUSH

```bash
git push -u origin HEAD
```

If push fails due to divergence:
```bash
git fetch origin
git rebase origin/<base>
git push -u origin HEAD
```

If rebase conflicts occur, stop and inform the user.

---

## Phase 4 — CREATE

### With Template

If a PR template was found in Phase 2, fill in each section using the commit and file analysis. Preserve all template sections — leave sections as "N/A" if not applicable rather than removing them. When a `GitHub Issue` (`#<issue>`) was discovered, include `Closes #<issue>` in the related issues section.

### Without Template

Use this default format:

```markdown
## Summary

<1-2 sentence description of what this PR does and why>

## Changes

<bulleted list of changes grouped by area>

## Files Changed

<table or list of changed files with change type: Added/Modified/Deleted>

## Testing

<description of how changes were tested, or "Needs testing">

## Related Issues

<If a GitHub Issue was discovered: "Closes #<issue>", otherwise "None">
```

### Create the PR

```bash
gh pr create \
  --title "<PR title>" \
  --base <base-branch> \
  --body "<PR body>"
  # Add --draft if the --draft flag was parsed from $ARGUMENTS
```

---

## Phase 5 — VERIFY

```bash
gh repo view --json defaultBranchRef --jq .defaultBranchRef.name
gh pr view --json number,url,title,state,baseRefName,headRefName,additions,deletions,changedFiles,closingIssuesReferences
gh pr checks --json name,state,bucket 2>$null || true
```

When a `GitHub Issue` (`#<issue>`) was linked:
- **If `<base>` equals the repository default branch** and `closingIssuesReferences` is empty, update the PR body (`gh pr edit <number> --body ...`) so `Closes #<issue>` is recognized.
- **If `<base>` is a non-default branch (e.g., `feat/*`, `develop`, `release/*`)**: GitHub ignores `Closes #<issue>` auto-linking and auto-closing on non-default base branches (`closingIssuesReferences` stays empty). Keep `Closes #<issue>` in the PR body for traceability, and post a cross-reference comment on the issue:
  ```bash
  gh issue comment <issue> --body "Linked PR #<pr-number> (targeting \`<base>\`): <pr-url>"
  ```

---

## Phase 6 — OUTPUT

Report to user:

```
PR #<number>: <title>
URL: <url>
Branch: <head> → <base>
Changes: +<additions> -<deletions> across <changedFiles> files

CI Checks: <status summary or "pending" or "none configured">

Artifacts referenced:
  - <any PRP reports/plans linked in PR body>

Next steps:
  - gh pr view <number> --web   → open in browser
  - /code-review <number>       → review the PR
  - gh pr merge <number>        → merge when ready
```

---

## Phase 7 — MERGE, CLOSE ISSUE & FOLLOW-UP TRIAGE

When the user requests merging or closing out the PR lifecycle:

1. **Merge & Sync Base Branch**:
   ```bash
   gh pr checks <number>
   gh pr merge <number> --squash --delete-branch
   git checkout <base>
   git pull origin <base>
   ```
2. **Close Linked Issue & Update Project Board Status (`Done`)**:
   - Confirm linked `Closes #<issue>` tickets are closed (`gh issue view <issue> --json state --jq .state`).
   - If a linked issue is still `OPEN` (for example, because the PR merged into a non-default `feat/*` base branch where GitHub does not auto-close `Closes #<issue>`), explicitly close it referencing the merged PR:
     ```bash
     gh issue close <issue> --reason completed --comment "Resolved by merged PR #<pr-number> into \`<base>\`."
     ```
   - Transition each closed issue to `Done` and roll up any Parent Epic Roadmap dates:
     ```bash
     python -c "import os, subprocess, sys; p = '.agents/scripts/gh_project.py'; p = p if os.path.exists(p) else os.path.expanduser('~/.gemini/config/plugins/my-harness/scripts/gh_project.py'); subprocess.call([sys.executable, p, 'set-status', '<ISSUE_NUMBER>', 'Done']) if os.path.exists(p) else 0"
     ```
3. **Found Known Issues? → Create New Issue**:
   - Inspect `.agents/reviews/pr-<number>-review.md` and `.agents/PRPs/reports/` for deferred findings or known issues.
   - If any exist, ask the user via `ask_question` (`is_multi_select: true`) which items should become new backlog tickets.
   - Create each selected ticket with `gh issue create`, add it to the GitHub Project (`gh project item-add`), and set `Status = Todo`.

---

## Edge Cases

- **No `gh` CLI**: Stop with: "GitHub CLI (`gh`) is required. Install: <https://cli.github.com/>"
- **Not authenticated**: Stop with: "Run `gh auth login` first."
- **Force push needed**: If remote has diverged and rebase was done, use `git push --force-with-lease` (never `--force`).
- **Multiple PR templates**: If `.github/PULL_REQUEST_TEMPLATE/` has multiple files, list them and ask user to choose.
- **Large PR (>20 files)**: Warn about PR size. Suggest splitting if changes are logically separable.

---
name: pr-changelog
description: Generate a concise, focused, and clear changelog for a PR or branch changes based on git diff and commit history — automatically updates the latest entry of CHANGELOG.md if it exists, supports GitHub PRs, conventional commits, and breaking change detection.
---

# PR Changelog Generator

Generate a concise, focused, and high-signal changelog for a pull request or branch changes based on git commit history, diff analysis, and PR metadata. Automatically updates the latest entry in `CHANGELOG.md` if the file exists.

## Input Arguments

`$ARGUMENTS` — optional, can contain:
- A GitHub PR number or URL (e.g., `42`, `#42`, `https://github.com/org/repo/pull/42`)
- A base branch name (e.g., `main`, `origin/main`, `develop`)
- Flags:
  - `--format <concise|pr|keepachangelog|compact|json>` (default: `pr`)
  - `--changelog-file <path>` (override path to `CHANGELOG.md`)
  - `--no-changelog` (skip updating `CHANGELOG.md` even if present)
  - `--update-pr` (automatically update PR description via `gh pr edit`)
  - `--output <file-path>` (write to an explicit file instead of only chat output)

---

## Operating Modes

1. **Local Branch Mode** (Default when no PR number/URL provided):
   - Compares the current branch against the target base branch (`origin/main` or specified base).
2. **GitHub PR Mode** (When PR number/URL is passed or `--pr` is used):
   - Fetches PR metadata and diffs directly via GitHub CLI (`gh`).

---

## Phase 1 — VALIDATE & PRE-FLIGHT

1. Verify git environment:
   ```bash
   git branch --show-current
   git status --short
   ```
2. Determine target base branch:
   - If not specified in arguments, detect default branch (`origin/main` or `origin/master`).
3. If reviewing a local branch, ensure there are commits ahead of base:
   ```bash
   git log origin/<base>..HEAD --oneline
   ```
   If empty, inform user: "No commits ahead of `<base>`. Nothing to generate a changelog for."
4. Check if `CHANGELOG.md` exists in the repository root:
   ```bash
   # Check file existence
   test -f CHANGELOG.md || Test-Path CHANGELOG.md
   ```

---

## Phase 2 — EXTRACT CHANGES

Run the built-in changelog generator script to parse commits, diff stats, conventional commit prefixes, and affected areas:

```bash
# Generate concise changelog (supports both local project and global plugin paths):
python -c "import os, sys, subprocess; cand = next((p for p in ['.agents/skills/pr-changelog/scripts/generate_changelog.py', os.path.expanduser('~/.gemini/config/plugins/my-harness/skills/pr-changelog/scripts/generate_changelog.py'), os.path.expanduser('~/.agents/skills/pr-changelog/scripts/generate_changelog.py')] if os.path.exists(p)), None); sys.exit(subprocess.run([sys.executable, cand] + sys.argv[1:]).returncode if cand else 1)" --base <base> --format concise

# For existing GitHub PR:
python -c "import os, sys, subprocess; cand = next((p for p in ['.agents/skills/pr-changelog/scripts/generate_changelog.py', os.path.expanduser('~/.gemini/config/plugins/my-harness/skills/pr-changelog/scripts/generate_changelog.py'), os.path.expanduser('~/.agents/skills/pr-changelog/scripts/generate_changelog.py')] if os.path.exists(p)), None); sys.exit(subprocess.run([sys.executable, cand] + sys.argv[1:]).returncode if cand else 1)" --pr <pr-number> --format concise
```

---

## Phase 3 — SYNTHESIZE CONCISE & FOCUSED CONTENT

When crafting or refining the changelog:

1. **Be Concise & High-Signal**:
   - Focus strictly on *what changed* and *why it matters*.
   - Filter out low-value noise (lint fixes, typo patches, formatting, version bumps, merge commits).
   - Consolidate multiple small commits targeting the same area into a single clear bullet.
   - Omit empty sections completely (e.g., do not show an empty "Features" or "Breaking Changes" header).
2. **Prioritize Breaking Changes**:
   - Immediately surface breaking changes with 🚨, the affected scope, and required migration action.
3. **Structured Grouping**:
   - ⚠️ **Breaking Changes**: Critical API or contract changes.
   - 🚀 **Features**: New user-facing capabilities or tools.
   - 🐛 **Bug Fixes**: Resolved bugs, edge-case handling, and race conditions.
   - 🔄 **Improvements & Architecture**: Performance boosts, refactoring, and code organization.
   - 🛠️ **Maintenance**: Essential dependency or tool updates.
4. **Sharp Bullets**:
   - Use `- **<scope>**: <clear imperative description> (<ref/hash>)`.

---

## Phase 4 — UPDATE CHANGELOG.MD (IF EXISTS)

If `CHANGELOG.md` exists in the workspace root:

1. **Locate Latest Entry**:
   - Checks for `## [Unreleased]` (or `## Unreleased`).
   - If not present, targets the latest version heading (e.g. `## [x.y.z]`).
   - If no version headings exist, places entries after the primary `# Changelog` heading.
2. **Automatic Insertion**:
   - The script `generate_changelog.py` handles this automatically on execution.
   - If editing manually, insert the concise markdown under the latest entry header without removing existing history.
3. **Notify User**:
   - Highlight that `CHANGELOG.md` has been updated with a link to the file.

---

## Phase 5 — DELIVER OUTPUT

### Concise Markdown Template

```markdown
### ⚠️ Breaking Changes
<!-- Only if breaking changes exist -->
- 🚨 **<scope>**: <breaking change description> (`<hash>`)

### 🚀 Features
- **<scope>**: <concise description> (`<hash>`)

### 🐛 Bug Fixes
- **<scope>**: <concise description> (`<hash>`)

### 🔄 Improvements & Architecture
- **<scope>**: <concise description> (`<hash>`)
```

### Action Dispatch
Depending on flags provided:
1. **Chat Output**: Print the concise changelog.
2. **CHANGELOG.md**: Automatically updated if present.
3. **GitHub PR Description**: If `--update-pr` is specified:
   ```bash
   gh pr edit <pr-number> --body "<generated-changelog>"
   ```

---

## Integration with Google Antigravity SDK

```python
from google.antigravity import Agent, LocalAgentConfig

config = LocalAgentConfig(
    skills_paths=[".agents/skills"]  # Automatically loads pr-changelog
)

async with Agent(config) as agent:
    response = await agent.chat(
        "Generate a concise changelog for my current PR branch and update CHANGELOG.md if it exists"
    )
    print(await response.text())
```

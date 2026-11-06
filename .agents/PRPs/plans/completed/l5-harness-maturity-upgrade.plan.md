# Plan: L5 Harness Maturity Upgrade (Hard Gates, Structural AST Checks, Co-Harness Learning & Trajectory Telemetry)

## Summary
Upgrade `my-harness` from Level 3.8–4.2 to Level 4.5–5.0 by adding (1) automatic Git `pre-commit` shift-left enforcement alongside `post-merge` hooks in `harness.py`, (2) zero-dependency AST and structural complexity checks (`max_function_lines <= 50`, `max_nesting_depth <= 4`) in `verify_shift_left.py`, (3) automated Co-Harness extraction and persistence of Phase 4.5 Critic findings in `curate_knowledge.py` and `/implement`, and (4) trajectory failure streak telemetry in `memory_logger.py`.

## User Story
As an AI-native engineering team using `my-harness`, I want deterministic Git pre-commit gates, sub-second structural complexity checks, automatic gotcha curation from Critic reviews, and tool-failure trajectory logging, so that agents cannot bypass quality gates or repeat the same architectural or operational mistakes across sessions.

## Problem → Solution
- **Advisory Hooks → Hard Git Pre-Commit Gates**: `harness init` and `harness install-hooks` only installed `post-merge` hooks → Now install both `pre-commit` (running `verify_shift_left.py --staged`) and `post-merge`.
- **LLM-Only Structural Checks → Sub-Second AST/Brace Pre-Flight**: Function length (`>50` lines) and nesting depth (`>4` levels) were only checked during LLM review → Now deterministically enforced in `verify_shift_left.py` via `check_structural_complexity` and configured via `rules.structural_rules` in `harness.schema.json`.
- **Static Reports → Co-Harness Self-Improvement**: Phase 4.5 Critic findings sat inert in markdown reports → `curate_knowledge.py --persist` extracts `## Self-Review & Adaptation Log` tables and persists deduplicated gotchas into `.agents/references/gotchas/auto-curated-gotchas.md` during `/implement` Phase 5.
- **Keyword-Only Memory → Trajectory Failure Telemetry**: `memory_logger.py` only matched user text regexes → Now also detects streaks of `>= 2` failed tool calls/commands in `transcript.jsonl` and logs `[Trajectory Failure]` entries.

## Metadata
- **Complexity**: Large
- **Source PRD**: `.agents/PRPs/prds/l5-harness-maturity-upgrade.prd.md`
- **PRD Phase**: Phase 1 (Full L4.5–L5 Upgrade)
- **Estimated Files**: 15 files (scripts, template mirrors, schema, CLI, skills, and unit tests)

---

## Mandatory Reading

| Priority | File | Lines | Why |
|---|---|---|---|
| P0 (critical) | `harness.py` | 665-945 | `cmd_init`, `is_git_hook_installed`, `install_git_hooks`, `cmd_install_hooks` implementation |
| P0 (critical) | `.agents/scripts/verify_shift_left.py` | 159-455 | `Violation` class, `scan_files`, and file scanning loop |
| P0 (critical) | `.agents/scripts/curate_knowledge.py` | 35-147 | Report parsing and knowledge curation flow |
| P0 (critical) | `.agents/scripts/memory_logger.py` | 85-180 | `log_interaction` and `handle_hook` transcript parsing |
| P1 (important) | `harness.schema.json` | 48-120 | JSON schema for `rules` in `harness.config.json` |
| P1 (important) | `.agents/skills/implement/SKILL.md` | 250-276 | Phase 5 (REPORT) workflow and template parity |
| P1 (important) | `tests/test_git_hooks.py` | 1-56 | Existing git hook unit tests |
| P1 (important) | `tests/test_python_syntax.py` | 1-75 | PEP 701 compatibility check (no backslashes inside f-string expressions) |

---

## Patterns to Mirror

### VIOLATION_REPORTING
```python
# SOURCE: .agents/scripts/verify_shift_left.py:54-68
class Violation:
    def __init__(self, file: str, line: int, code: str, rule: str, suggestion: str):
        self.file = file
        self.line = line
        self.code = code.strip()
        self.rule = rule
        self.suggestion = suggestion
```

### GIT_HOOK_INSTALLATION
```python
# SOURCE: harness.py:896-932
def install_git_hooks(repo_root: Path) -> bool:
    hooks_dir = get_git_hooks_dir(repo_root)
    if not hooks_dir:
        return False
    hooks_dir.mkdir(parents=True, exist_ok=True)
```

### TEMPLATE_PARITY_TESTING
```python
# SOURCE: tests/test_implement_skill.py:25-34
for rel in rel_files:
    proj_text = (self.project_skill_dir / rel).read_text(encoding="utf-8")
    tmpl_text = (self.template_skill_dir / rel).read_text(encoding="utf-8")
    self.assertEqual(proj_text, tmpl_text, f"Project and template {rel} must be byte-for-byte identical")
```

---

## Files to Change

| File | Action | Justification |
|---|---|---|
| `harness.schema.json` | UPDATE | Add `structural_rules` schema (`enabled`, `max_function_lines`, `max_nesting_depth`, `path_exclude`) under `rules` |
| `.agents/scripts/verify_shift_left.py` | UPDATE | Add `check_structural_complexity` (Python `ast` + brace/control-flow nesting & function length checks) and wire into `scan_files` |
| `template/.agents/scripts/verify_shift_left.py` | UPDATE | Keep byte-for-byte identical with `.agents/scripts/verify_shift_left.py` |
| `harness.py` | UPDATE | Install both `pre-commit` (running `verify_shift_left.py --staged`) and `post-merge` hooks in `install_git_hooks`, check both in `is_git_hook_installed`, and auto-invoke `install_git_hooks` in `cmd_init` (project scope when `.git` exists) |
| `.agents/scripts/curate_knowledge.py` | UPDATE | Add `extract_self_review_findings`, `persist_curated_gotchas`, and `--persist` CLI flag to write `.agents/references/gotchas/auto-curated-gotchas.md` |
| `template/.agents/scripts/curate_knowledge.py` | UPDATE | Keep byte-for-byte identical with `.agents/scripts/curate_knowledge.py` |
| `.agents/skills/implement/SKILL.md` | UPDATE | Update Phase 5 (REPORT) to run `curate_knowledge.py --persist` so Phase 4.5 Critic findings and deviations automatically update `.agents/references/gotchas/` |
| `template/.agents/skills/implement/SKILL.md` | UPDATE | Keep byte-for-byte identical with `.agents/skills/implement/SKILL.md` |
| `.agents/scripts/memory_logger.py` | UPDATE | Add `extract_trajectory_failures` and `log_trajectory_failures` to log streaks of `>= 2` failed tool executions in `transcript.jsonl` |
| `template/.agents/scripts/memory_logger.py` | UPDATE | Keep byte-for-byte identical with `.agents/scripts/memory_logger.py` |
| `.agents/skills/agent-log-analyzer/scripts/analyze.py` | UPDATE | Parse and report both `**User Request:**` and `**Trajectory Failure:**` entries from `.agents/logs/*.md` |
| `template/.agents/skills/agent-log-analyzer/scripts/analyze.py` | UPDATE | Keep byte-for-byte identical with `.agents/skills/agent-log-analyzer/scripts/analyze.py` |
| `tests/test_git_hooks.py` | UPDATE | Test `pre-commit` and `post-merge` installation, `is_git_hook_installed`, and auto-install during `cmd_init` |
| `tests/test_verify_shift_left.py` | CREATE | Unit tests for `check_structural_complexity` (Python AST & JS/TS/Rust brace functions, length > 50, nesting > 4, `shift-left-ignore`, `structural_rules` config) |
| `tests/test_l5_loops.py` | CREATE | Unit tests for `curate_knowledge.py` (`extract_self_review_findings`, `persist_curated_gotchas`, idempotency) and `memory_logger.py` (`extract_trajectory_failures`, hook logging) |

## NOT Building
- External AST parser dependencies (everything uses Python stdlib `ast`, `re`, `json`).
- Breaking changes to existing `harness.py` CLI flags or existing `verify_shift_left.py` flags.

---

## Step-by-Step Tasks

### Task 1: Git Pre-Commit & Post-Merge Hook Enforcement in `harness.py`
- **ACTION**: Update `harness.py` so `install_git_hooks(repo_root)` installs both `.git/hooks/pre-commit` (which runs `.agents/scripts/verify_shift_left.py --staged` if present) and `.git/hooks/post-merge` (auto-update hook), `is_git_hook_installed(repo_root)` verifies both hooks exist and contain expected markers, and `cmd_init` automatically calls `install_git_hooks(target_dir)` in project scope when `(target_dir / ".git").exists()`.
- **TEST_FIRST**: Update `tests/test_git_hooks.py` to assert:
  1. `install_git_hooks` creates both `.git/hooks/pre-commit` (containing `verify_shift_left.py --staged`) and `.git/hooks/post-merge`.
  2. `is_git_hook_installed` returns `False` if either `pre-commit` or `post-merge` is missing, and `True` when both are installed.
  3. `cmd_init` in project scope on a git repository automatically installs both git hooks.
- **IMPLEMENT**:
  - In `harness.py`, update `install_git_hooks(repo_root: Path) -> bool` to write `pre-commit` and `post-merge` with `0o755` permissions.
  - Update `is_git_hook_installed(repo_root: Path) -> bool` to verify both `post-merge` and `pre-commit`.
  - In `cmd_init`, when `not is_global` and `get_git_hooks_dir(target_dir)` is not `None`, call `install_git_hooks(target_dir)`.
- **MIRROR**: `harness.py:882-943`
- **IMPORTS**: Existing stdlib imports in `harness.py`
- **GOTCHA**: Avoid backslashes inside f-string expressions (PEP 701 check in `tests/test_python_syntax.py`). Ensure `pre-commit` exits `0` gracefully if Python or `.agents/scripts/verify_shift_left.py` is not present in the repo.
- **MICRO_VALIDATE**: `python -m unittest tests/test_git_hooks.py tests/test_harness_init.py`

### Task 2: Structural Complexity Rules Schema & Pre-Flight Scanner (`verify_shift_left.py`)
- **ACTION**: Add `structural_rules` to `harness.schema.json` and implement `check_structural_complexity(file_path, content, structural_cfg)` in `.agents/scripts/verify_shift_left.py` (and sync to `template/.agents/scripts/verify_shift_left.py` and `deploy_antigravity_plugin` portable scripts if applicable).
- **TEST_FIRST**: Create `tests/test_verify_shift_left.py` testing:
  1. Python function `<= 50` lines and `<= 4` nesting depth passes with 0 violations.
  2. Python function `> 50` lines (e.g., 55 lines) triggers a `Violation` citing function name, line count, and max limit.
  3. Python function with control-flow nesting depth `> 4` (e.g., 5 nested `if`/`for`/`while`/`try`/`with` blocks) triggers a `Violation`.
  4. TypeScript/Rust brace-delimited function `> 50` lines or nesting `> 4` triggers a `Violation`.
  5. `shift-left-ignore` comment on the `def`/`function` line or inside skips the violation.
  6. `structural_rules: {"enabled": false}` or `path_exclude` disables the check for matching files.
  7. Template parity between `.agents/scripts/verify_shift_left.py` and `template/.agents/scripts/verify_shift_left.py`.
- **IMPLEMENT**:
  - Update `harness.schema.json` under `properties.rules.properties` to define `structural_rules`.
  - In `.agents/scripts/verify_shift_left.py`, implement `check_structural_complexity(file_path: Path, content: str, structural_cfg: dict) -> list[Violation]`:
    - Default `enabled = structural_cfg.get("enabled", True)`, `max_lines = structural_cfg.get("max_function_lines", 50)`, `max_depth = structural_cfg.get("max_nesting_depth", 4)`, `path_exclude = structural_cfg.get("path_exclude", ["tests/", "test_"])`.
    - For `.py` files: parse with `ast.parse`, inspect `ast.FunctionDef` and `ast.AsyncFunctionDef` (computing `end_lineno - lineno + 1`, skipping if `shift-left-ignore` on def line, and walking child control-flow nodes `If`, `For`, `AsyncFor`, `While`, `Try`, `With`, `AsyncWith` to compute max nesting depth relative to the function). Note: if any existing function in `my-harness` exceeds 50 lines, either refactor helper functions or respect `structural_cfg` so `verify_shift_left.py --changed` passes cleanly on our own files!
    - For `.ts`, `.js`, `.rs`, `.go`, `.vue`: inspect function blocks and control-flow brace depth.
  - Copy `.agents/scripts/verify_shift_left.py` to `template/.agents/scripts/verify_shift_left.py`.
- **MIRROR**: `.agents/scripts/verify_shift_left.py:195-266`
- **IMPORTS**: `import ast` in `verify_shift_left.py`
- **GOTCHA**: Keep functions inside `verify_shift_left.py` itself `<= 50` lines and nesting `<= 4` so that when `verify_shift_left.py --changed` scans itself, it passes with 0 violations!
- **MICRO_VALIDATE**: `python -m unittest tests/test_verify_shift_left.py && python .agents/scripts/verify_shift_left.py --changed`

### Task 3: Co-Harness Self-Review Extraction & Auto-Gotcha Persistence (`curate_knowledge.py` & `/implement`)
- **ACTION**: Enhance `.agents/scripts/curate_knowledge.py` (and `template/.agents/scripts/curate_knowledge.py`) with `extract_self_review_findings(base_dir)`, `persist_curated_gotchas(base_dir, findings, issues)`, and a `--persist` CLI flag. Update `.agents/skills/implement/SKILL.md` (and `template/.agents/skills/implement/SKILL.md`) Phase 5 to invoke `curate_knowledge.py --persist`.
- **TEST_FIRST**: Create `tests/test_l5_loops.py` with tests asserting:
  1. `extract_self_review_findings` parses the markdown table under `## Self-Review & Adaptation Log` from a report file and ignores placeholder rows (`[HIGH/MEDIUM/LOW]` or `None`).
  2. `persist_curated_gotchas` creates `.agents/references/gotchas/auto-curated-gotchas.md` containing `CRITICAL`, `HIGH`, and `MEDIUM` findings and report deviations/issues, and updates `.agents/references/README.md` index if not linked.
  3. Running `persist_curated_gotchas` twice with the same reports is idempotent (no duplicate gotcha sections).
  4. `.agents/scripts/curate_knowledge.py` and `template/.agents/scripts/curate_knowledge.py` are byte-for-byte identical.
  5. `.agents/skills/implement/SKILL.md` and `template/.agents/skills/implement/SKILL.md` are byte-for-byte identical and include `curate_knowledge.py --persist` in Phase 5.
- **IMPLEMENT**:
  - Implement `extract_self_review_findings(base_dir: Path) -> list[dict]` and `persist_curated_gotchas(base_dir: Path, findings: list[dict], issues: list[dict]) -> Path | None` in `.agents/scripts/curate_knowledge.py`.
  - Add `argparse` (`--persist`) to `curate_knowledge.py`.
  - Sync to `template/.agents/scripts/curate_knowledge.py`.
  - Add `curate_knowledge.py --persist` step to Phase 5 in `.agents/skills/implement/SKILL.md` and `template/.agents/skills/implement/SKILL.md`.
- **MIRROR**: `.agents/scripts/curate_knowledge.py:61-94`
- **IMPORTS**: `import argparse` in `curate_knowledge.py`
- **GOTCHA**: Keep all functions in `curate_knowledge.py` `<= 50` lines and nesting `<= 4` to satisfy the new structural complexity gate.
- **MICRO_VALIDATE**: `python -m unittest tests/test_l5_loops.py tests/test_implement_skill.py && python .agents/scripts/verify_shift_left.py --changed`

### Task 4: Trajectory Failure Telemetry (`memory_logger.py` & `agent-log-analyzer`)
- **ACTION**: Upgrade `.agents/scripts/memory_logger.py` (and `template/.agents/scripts/memory_logger.py`) to detect streaks of `>= 2` consecutive failed tool/command steps in `transcript.jsonl` via `extract_trajectory_failures(steps, min_streak=2)` and log them as `**Trajectory Failure:**` entries in `.agents/logs/YYYY-MM-DD.md`. Update `.agents/skills/agent-log-analyzer/scripts/analyze.py` (and its template copy) to extract and display both `**User Request:**` and `**Trajectory Failure:**` entries.
- **TEST_FIRST**: Add unit tests in `tests/test_l5_loops.py` asserting:
  1. `extract_trajectory_failures` returns a failure record when `transcript.jsonl` steps contain `>= 2` consecutive failed steps (`status == "ERROR"` or tool output with `"Command exited with code 1"` / `"exit code"`), and returns `[]` when steps succeed or have only 1 isolated failure.
  2. `handle_hook` logs `**Trajectory Failure:**` to `YYYY-MM-DD.md` when a failure streak is present in the transcript, even if the user prompt had no correction keywords, and updates `.last_logged_step_<conversationId>`.
  3. `analyze.py` extracts and prints both user requests and trajectory failures.
  4. Template parity holds for `memory_logger.py` and `analyze.py`.
- **IMPLEMENT**:
  - Implement `extract_trajectory_failures(steps: list[dict], min_streak: int = 2) -> list[dict]` and `log_trajectory_failures(failures: list[dict], base_dir: Path = None) -> bool` in `.agents/scripts/memory_logger.py`.
  - Wire into `handle_hook` in `memory_logger.py` and sync to `template/.agents/scripts/memory_logger.py`.
  - Update `.agents/skills/agent-log-analyzer/scripts/analyze.py` and `template/.agents/skills/agent-log-analyzer/scripts/analyze.py`.
- **MIRROR**: `.agents/scripts/memory_logger.py:85-177`
- **IMPORTS**: Existing stdlib imports
- **GOTCHA**: Keep functions in `memory_logger.py` and `analyze.py` `<= 50` lines and nesting `<= 4`.
- **MICRO_VALIDATE**: `python -m unittest discover tests && python .agents/scripts/verify_shift_left.py --changed`

---

## Test-Driven Strategy

All implementation MUST be preceded by writing failing tests.

### Unit Tests
| Test | Input | Expected Output | Edge Case? |
|---|---|---|---|
| `test_install_git_hooks_creates_pre_commit_and_post_merge` | Mock git repo | Both `.git/hooks/pre-commit` and `post-merge` created & executable | No |
| `test_python_function_over_50_lines_fails` | 55-line `.py` function | 1 `Violation` reporting function length `55 > 50` | No |
| `test_python_nesting_over_4_levels_fails` | 5-level nested `if/for/try` in `.py` | 1 `Violation` reporting nesting depth `5 > 4` | No |
| `test_structural_check_respects_shift_left_ignore` | 60-line function with `# shift-left-ignore` | 0 violations | Yes |
| `test_extract_and_persist_self_review_findings` | Report with `HIGH` & `MEDIUM` table rows | Deduplicated entries written to `auto-curated-gotchas.md` | Yes (idempotency) |
| `test_trajectory_failure_streak_logged` | Transcript with 2 consecutive failed tool steps | `**Trajectory Failure:**` written to `.agents/logs/YYYY-MM-DD.md` | Yes |

### Edge Cases Checklist
- [x] Empty / nullish input or missing `.git` / `.agents` directories
- [x] Boundary limits (`50` lines pass, `51` lines fail; depth `4` passes, depth `5` fails)
- [x] Idempotent re-runs (`curate_knowledge.py --persist` and `install_git_hooks`)
- [x] Python < 3.12 f-string compatibility (zero backslashes in f-string expressions)

---

## Validation Commands

### Level 0: Shift-Left Pre-Flight Scanner (< 1s)
```bash
python -c "import os, subprocess, sys; p = '.agents/scripts/verify_shift_left.py'; p = p if os.path.exists(p) else os.path.expanduser('~/.gemini/config/plugins/my-harness/scripts/verify_shift_left.py'); sys.exit(subprocess.call([sys.executable, p, '--changed']) if os.path.exists(p) else 0)"
```

### Level 1: Static Analysis & Syntax Compatibility
```bash
python -m unittest tests/test_python_syntax.py
```

### Level 2: Unit Tests
```bash
python -m unittest discover tests
```

### Level 3: Doctor Check
```bash
python harness.py doctor
```

---

## Acceptance Criteria
- [ ] All 4 tasks completed
- [ ] All validation commands pass with zero errors
- [ ] Failing tests written before implementation (TDD Red-Green-Refactor)
- [ ] Template parity verified across all modified `.agents/` and `template/.agents/` files
- [ ] Zero shift-left architectural or structural violations (`verify_shift_left.py --changed`)

## Risks
| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Existing functions in modified files exceed 50 lines and trigger the new structural scanner on `--changed` | High | Medium | Decompose functions in modified files into clean, single-responsibility helpers `<= 50` lines and exclude `tests/` by default in `structural_rules`. |
| Windows file locking or permissions on `.git/hooks/` | Low | Low | Handle `chmod` gracefully inside `try/except` as `harness.py` already does. |

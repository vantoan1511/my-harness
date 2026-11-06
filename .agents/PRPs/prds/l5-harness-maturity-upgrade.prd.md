# Spec: L5 Harness Maturity Upgrade (Hard Gates, Structural AST Checks, Co-Harness Learning & Trajectory Telemetry)

## 1. Intent & Problem Statement
- **User Intent**: Advance `my-harness` from Level 3.8–4.2 (Mature L3 / Early L4) to Level 4.5–5.0 on the AI Harness Maturity Model by implementing deterministic structural gates, Git pre-commit enforcement, automated Co-Harness feedback loops from Phase 4.5 Critic reviews, and trajectory failure telemetry.
- **Problem**:
  1. **Advisory vs. Hard Git Gates**: While `verify_shift_left.py` exists, `harness init` and `harness install-hooks` only install a `post-merge` auto-update hook, leaving `pre-commit` unguarded if an agent skips a manual step.
  2. **Regex-Only Pre-Flight**: Constitutional limits in `AGENTS.md` (functions `> 50 lines`, nesting `> 4 levels`) are currently evaluated only during slow LLM self-review rather than caught deterministically in `< 0.5s` by `verify_shift_left.py`.
  3. **Open-Loop Phase 4.5 Critic Findings**: When `/implement` Phase 4.5's Critic Subagent catches `CRITICAL` or `HIGH` issues and adapts them, those findings are logged in `.agents/PRPs/reports/*-report.md` under `## Self-Review & Adaptation Log`, but `curate_knowledge.py` does not extract them or persist them into `.agents/references/gotchas/`.
  4. **Regex-Bound Memory Logging**: `memory_logger.py` only logs explicit user correction keywords in `USER_INPUT` steps, ignoring implicit agent failure trajectories (e.g., 2+ consecutive failed `run_command` executions or tool error steps in `transcript.jsonl`).
- **Target Outcome**:
  1. `harness init` (project scope, when `.git` exists) and `harness install-hooks` automatically install both `.git/hooks/pre-commit` (running `verify_shift_left.py --staged`) and `.git/hooks/post-merge`.
  2. `verify_shift_left.py` enforces `structural_rules` (`max_function_lines: 50`, `max_nesting_depth: 4` by default) using Python `ast` for `.py` files and brace/control-flow analysis for `.ts`/`.js`/`.rs`/`.go`/`.vue` files, failing pre-flight unless suppressed via `shift-left-ignore`.
  3. `curate_knowledge.py` extracts `CRITICAL`/`HIGH`/`MEDIUM` rows from `## Self-Review & Adaptation Log` in PRP reports and `--persist` writes deduplicated gotcha entries into `.agents/references/gotchas/auto-curated-gotchas.md` (wired into `/implement` Phase 5).
  4. `memory_logger.py` detects repeated tool/command failure streaks (`>= 2` failed tool executions) in `transcript.jsonl` and logs `[Trajectory Failure]` entries to `.agents/logs/YYYY-MM-DD.md`, which `agent-log-analyzer` also surfaces.

## 2. User Experience & Interactions
- **CLI & Git Hook Flow**:
  1. User or agent runs `harness init` or `harness install-hooks`.
  2. Both `.git/hooks/pre-commit` and `.git/hooks/post-merge` are installed.
  3. On `git commit`, `pre-commit` executes `verify_shift_left.py --staged`, blocking commits on protected branches, pattern violations, or structural violations (`> 50` lines or `> 4` nesting depth).
- **Pre-Flight Scanner Flow**:
  1. Agent runs `python .agents/scripts/verify_shift_left.py --changed`.
  2. Scanner checks branch safety, banned imports, banned patterns, Vue template rules, and **structural complexity rules** (`check_structural_complexity`), reporting exact file, function/line, measured metric vs limit, and remediation suggestion.
- **Co-Harness Self-Improvement Flow**:
  1. During `/implement`, Phase 4.5 Critic Subagent identifies findings and records them in the implementation report's `## Self-Review & Adaptation Log` table.
  2. In Phase 5 (REPORT), `/implement` runs `python .agents/scripts/curate_knowledge.py --persist`, which parses report tables and corrections and appends new, deduplicated entries to `.agents/references/gotchas/auto-curated-gotchas.md`.
- **Trajectory Telemetry Flow**:
  1. `memory_logger.py --hook` runs on `PreInvocation`.
  2. In addition to user correction text, it scans recent steps in `transcript.jsonl` for consecutive tool/command failures (`status == "ERROR"` or non-zero exit codes) and logs `[Trajectory Failure]` blocks into `.agents/logs/YYYY-MM-DD.md`.

## 3. Contract-First Boundaries

### Configuration Schema Contract (`harness.schema.json` & `harness.config.json`)
```json
{
  "rules": {
    "structural_rules": {
      "enabled": true,
      "max_function_lines": 50,
      "max_nesting_depth": 4,
      "path_exclude": ["tests/"]
    }
  }
}
```

### Python Function & Data Contracts

```python
# .agents/scripts/verify_shift_left.py
def check_structural_complexity(
    file_path: Path,
    content: str,
    structural_cfg: dict
) -> list[Violation]:
    """
    Validates function length (<= max_function_lines, default 50) and control-flow
    nesting depth (<= max_nesting_depth, default 4).
    - Uses Python `ast` for `.py` files.
    - Uses brace/block tracking for `.ts`, `.js`, `.rs`, `.go`, `.vue` (<script>).
    - Respects `shift-left-ignore` comments on the function definition or offending line,
      as well as `structural_cfg.get("path_exclude", [])` and `structural_cfg.get("enabled", True)`.
    """

# .agents/scripts/curate_knowledge.py
def extract_self_review_findings(base_dir: Path) -> list[dict]:
    """
    Parses markdown tables under `## Self-Review & Adaptation Log` in `.agents/PRPs/reports/*-report.md`.
    Returns list of dicts:
    {
      "report": str,
      "severity": str,   # CRITICAL | HIGH | MEDIUM | LOW
      "file": str,
      "issue": str,
      "adaptation": str,
      "status": str
    }
    """

def persist_curated_gotchas(base_dir: Path, findings: list[dict], issues: list[dict]) -> Path | None:
    """
    Writes or updates `.agents/references/gotchas/auto-curated-gotchas.md` with deduplicated
    HIGH/CRITICAL/MEDIUM self-review findings and report deviations/issues.
    """

# .agents/scripts/memory_logger.py
def extract_trajectory_failures(steps: list[dict], min_streak: int = 2) -> list[dict]:
    """
    Scans parsed JSONL transcript steps for streaks of >= min_streak failed tool executions
    (step status == 'ERROR' or tool output indicating non-zero exit code / failure).
    Returns list of dicts:
    {
      "step_index": int,
      "streak_count": int,
      "tools": list[str],
      "summary": str
    }
    """
```

### State & Storage Invariants
- **Template Parity Invariant**: Every file in `.agents/scripts/` and `.agents/skills/` MUST remain byte-for-byte synchronized with `template/.agents/scripts/` and `template/.agents/skills/` (verified by unit tests).
- **Python < 3.12 Compatibility Invariant**: Zero backslashes inside f-string `{...}` expressions (PEP 701 check in `tests/test_python_syntax.py`).
- **Idempotency Invariant**: Running `curate_knowledge.py --persist` or `harness install-hooks` multiple times must never duplicate entries or corrupt existing files.

## 4. Scope Boundaries
- **In Scope (v1)**:
  - Git `pre-commit` + `post-merge` hook installation in `harness.py` (`install_git_hooks`, `is_git_hook_installed`, `cmd_init`, `cmd_doctor`, `cmd_install_hooks`).
  - Deterministic structural complexity checks (`max_function_lines: 50`, `max_nesting_depth: 4`) in `verify_shift_left.py` and `harness.schema.json`.
  - Co-Harness self-review extraction and `--persist` auto-gotcha curation in `curate_knowledge.py` and `/implement` Phase 5.
  - Trajectory failure streak detection in `memory_logger.py` and support in `agent-log-analyzer/scripts/analyze.py`.
  - Comprehensive unit tests covering all new contracts.
- **Out of Scope**:
  - External third-party AST dependencies (e.g., `tree-sitter`, `esprima`); must remain zero-dependency Python stdlib.
  - Modifying protected branches without user action.

## 5. Acceptance Criteria
- [ ] AC-1: `harness.install_git_hooks(repo)` installs executable `.git/hooks/pre-commit` (invoking `verify_shift_left.py --staged`) and `.git/hooks/post-merge`, and `cmd_init` automatically installs them when `.git` is present in project scope.
- [ ] AC-2: `verify_shift_left.py` flags functions exceeding `max_function_lines` (default 50) or `max_nesting_depth` (default 4) across `.py` and brace-delimited languages, supports `shift-left-ignore` and `structural_rules` config, and passes on `my-harness`'s own codebase.
- [ ] AC-3: `curate_knowledge.py` extracts `## Self-Review & Adaptation Log` entries from PRP reports and `--persist` writes deduplicated gotchas to `.agents/references/gotchas/auto-curated-gotchas.md`.
- [ ] AC-4: `memory_logger.py` detects `>= 2` consecutive tool/command failures in `transcript.jsonl` and logs `[Trajectory Failure]` entries to `.agents/logs/YYYY-MM-DD.md`.
- [ ] AC-5: All existing and new unit tests pass (`python -m unittest discover tests`), `test_python_syntax.py` passes with zero PEP 701 violations, and `verify_shift_left.py --changed` passes with zero violations.

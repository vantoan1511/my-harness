# Implementation Plan: Comprehensive Best Practices Remediation

## 1. Overview & Objectives
- **Goal**: Resolve all critical, high, and medium severity defects identified during the repository best-practices audit.
- **Key Target Areas**:
  1. Fix the syntax error in `install.sh`.
  2. Configure complete Python package bundling in `pyproject.toml`, `setup.py`, and `MANIFEST.in`.
  3. Fix destructive config clobbering in `harness.py` (`copy_tree_merge`).
  4. Enable test isolation via `GEMINI_CONFIG_DIR` environment variable in `harness.py`.
  5. Provide resilient global/workspace path resolution for skills calling helper scripts (`pr-changelog`, `session-handoff`, `agent-log-analyzer`).
  6. Sanitize universal skills (`commit`, `implement`, `pr`) of Unix-only commands failing on Windows PowerShell.
  7. Consolidate `fb-comment-style` as a clean alias to `natural-human-writing`.
  8. Add `harness.schema.json` to back `$schema` references.
  9. Add GitHub Actions CI workflow (`.github/workflows/ci.yml`).
  10. Wire sub-skill tests into the root test discovery and add unit tests for all fixes.

---

## 2. Invariants & Guardrails
- **Git Safety**: Current branch is `fix/remediation-best-practices`. Never commit to `main`.
- **Shift-Left Micro-Validation**: Run `python .agents/scripts/verify_shift_left.py --changed` after every file modification.
- **TDD (Red-Green-Refactor)**: Write unit tests first before writing production fixes.
- **Template & Project Parity**: Changes made to `.agents/` or `template/.agents/` must remain identical and synchronized.

---

## 3. Step-by-Step TDD Tasks

### Task 1: Shell Syntax & Installer Validation (RED -> GREEN)
- **Problem**: `install.sh` has a stray `fi` at line 112 causing a syntax error.
- **Test**: Add `tests/test_installer_syntax.py` testing `install.sh` syntax (matching `if/fi`, `case/esac`, or running `bash -n` if bash is available).
- **Fix**: Remove line 112 in `install.sh`.
- **Validation**: Verify test passes. Run pre-flight check.

### Task 2: Python Package Distribution & Asset Inclusion (RED -> GREEN)
- **Problem**: `pyproject.toml` only declares `py-modules = ["harness"]`, omitting `template/`, `packs/`, `scripts/`, and `assets/` from wheels/sdists.
- **Test**: Add test in `tests/test_packaging.py` asserting `MANIFEST.in` includes required asset trees and `pyproject.toml` configures package data.
- **Fix**:
  - Update `pyproject.toml` and `setup.py` with `include-package-data = true` and `package-data`.
  - Create `MANIFEST.in` including `template`, `packs`, `scripts`, and `assets`.
- **Validation**: Verify test passes. Run pre-flight check.

### Task 3: Non-Destructive Config Merging in `harness.py` (RED -> GREEN)
- **Problem**: `copy_tree_merge` unconditionally overwrites `.json` files, wiping out custom project rules in `harness.config.json` during `harness init`.
- **Test**: Add test `test_copy_tree_merge_does_not_clobber_existing_config` in `tests/test_harness_fix.py`.
- **Fix**: In `harness.py`, modify `copy_tree_merge` or `cmd_init` so that existing config files (`harness.config.json`, `hooks.json`) are merged rather than blindly overwritten.
- **Validation**: Run `python -m unittest tests/test_harness_fix.py`. Run pre-flight check.

### Task 4: Test Isolation & Environment Override (`GEMINI_CONFIG_DIR`) (RED -> GREEN)
- **Problem**: `cmd_init` and `test_installer_e2e.py` mutate the host's real `~/.gemini/config/plugins/my-harness`.
- **Test**: Add test verifying that setting `GEMINI_CONFIG_DIR` redirects plugin deployment and detection away from `Path.home()`.
- **Fix**: Update `harness.py` to check `os.environ.get("GEMINI_CONFIG_DIR")` before defaulting to `Path.home() / ".gemini" / "config"`.
- **Fix `test_installer_e2e.py`**: Pass `GEMINI_CONFIG_DIR` pointing to temp dir during subprocess runs.
- **Validation**: Run `python -m unittest tests/test_installer_e2e.py`. Run pre-flight check.

### Task 5: Add `harness.schema.json` and Fix Scanner Buffering
- **Problem**: `$schema` referenced in `harness.config.json` does not exist; scanner prints delegation message after child runs.
- **Fix**:
  - Create `harness.schema.json` with JSON schema for harness configuration.
  - Add `flush=True` to `print()` in `scripts/verify_shift_left.py` and `.agents/scripts/verify_shift_left.py`.
- **Validation**: Run `python scripts/verify_shift_left.py --changed`.

### Task 6: Resilient Skill Script Resolution & Cross-Platform Sanitization
- **Problem**: Skills fail when run from global plugin because `.agents/skills/...` is removed; Unix-only commands (`grep`, `xargs`, `2>/dev/null`) fail on Windows PowerShell.
- **Fix**:
  - Update `pr-changelog`, `session-handoff`, and `agent-log-analyzer` to use resilient path resolution (checking local workspace first, then global plugin).
  - Update `commit`, `implement`, and `pr` skills to provide cross-platform alternatives for `grep`, `xargs`, and `2>/dev/null`.
  - Deprecate/alias `fb-comment-style` pointing to canonical `natural-human-writing`.
  - Keep `template/.agents/skills/` and `.agents/skills/` in exact parity.
- **Validation**: Run `python -m unittest discover tests`.

### Task 7: Wire Orphaned Tests & Add GitHub Actions CI
- **Problem**: 21 tests in `pr-changelog` are not discovered; no CI workflow exists.
- **Fix**:
  - Add `tests/test_pr_changelog.py` discovering tests from `template/.agents/skills/pr-changelog/scripts/tests/`.
  - Create `.github/workflows/ci.yml` running matrix tests across Ubuntu, macOS, and Windows.
- **Validation**: Run full test discovery: `python -m unittest discover tests`.

### Task 8: Synchronize & Final Pre-Flight Verification
- **Fix**: Sync all template changes with workspace and Antigravity plugin.
- **Validation**: Run full shift-left verification: `python scripts/verify_shift_left.py --all-checks`.

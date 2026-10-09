# Implementation Report: Installer Scope Selection (Project vs Global)

## Summary
Updated `harness.py`, `install.ps1`, and `install.sh` to support selecting between `project` and `global` installation scopes. Running the installers interactively prompts the user with an option menu; users and scripts can also bypass the prompt via the `-Scope` / `--scope` CLI flag. When global scope is selected, the harness scaffolds `.agents/` into the user's home directory (`~/.agents`) and registers the `harness` command globally in the Python environment using `pip install -e .`.

## Assessment vs Reality

| Metric | Predicted (Plan) | Actual |
|---|---|---|
| Complexity | Medium | Medium |
| Confidence | High | High |
| Files Changed | 5 | 5 |

## Tasks Completed

| # | Task | Status | Notes |
|---|---|---|---|
| 1 | Unit tests for `harness.py init --scope` | [done] Complete | `tests/test_harness_init.py` written using standard `unittest` |
| 2 | Implement `--scope` CLI arg and global init in `harness.py` | [done] Complete | Added `--scope {project,global}`, extracted `build_parser()`, implemented home target and pip registration |
| 3 | Update `install.ps1` with interactive prompt & `-Scope` | [done] Complete | Handles interactive menu with `Read-Host` and `-Scope` parameter |
| 4 | Update `install.sh` with interactive prompt & `--scope` | [done] Complete | Handles interactive menu, `--scope` / `-s` flag, and robust python detection |
| 5 | Update documentation in `README.md` | [done] Complete | Added scope selection guide to Quick Start and CLI tables |

## Validation Results

| Level | Status | Notes |
|---|---|---|
| Pre-Flight Scanner | [done] Pass | Zero architectural violations |
| Static Analysis | [done] Pass | Python syntax check clean across modified files; Bash syntax check clean |
| Unit Tests | [done] Pass | 4 tests passing in `tests/test_harness_init.py` |
| Edge Cases | [done] Pass | Tested non-interactive execution for both `install.ps1` and `install.sh` |

## Files Changed

| File | Action | Lines |
|---|---|---|
| `tests/test_harness_init.py` | CREATED | +70 |
| `harness.py` | UPDATED | +45 / -20 |
| `install.ps1` | UPDATED | +35 / -12 |
| `install.sh` | UPDATED | +65 / -15 |
| `README.md` | UPDATED | +35 / -15 |

## Deviations from Plan
- Enhanced Python detection in `install.sh` to test execution (`python -c "import sys"`) so that Microsoft Store stub aliases on Windows environments are gracefully bypassed in favor of a functional Python interpreter.

## Issues Encountered
- None. All validations and tests passed cleanly.

## Tests Written

| Test File | Tests | Coverage |
|---|---|---|
| `tests/test_harness_init.py` | 4 tests | CLI argument parsing (default, project, global) and `cmd_init` behavior |

## Knowledge Base Updates (Self-Improving)
- None required.

## Next Steps
- Verify git status and commit changes.

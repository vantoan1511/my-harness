# Implementation Plan: Fix CI PowerShell Syntax Check Step

## 1. Overview & Objectives
- **Source PRD**: [.agents/PRPs/prds/ci-powershell-syntax-check-fix.prd.md](file:///d:/Projects/my-harness/.agents/PRPs/prds/ci-powershell-syntax-check-fix.prd.md)
- **Goal**: Make the Windows `ParseFile` step in `ci.yml` work. `$errors` and `$tokens` must be declared before they are passed to `[ref]`.

## 2. Problem & Current Implementation
- `.github/workflows/ci.yml` lines 38-46 call `ParseFile("install.ps1", [ref]$null, [ref]$errors)`, and `$errors` is never defined.
- [tests/test_installer_syntax.py](file:///d:/Projects/my-harness/tests/test_installer_syntax.py) already holds installer syntax tests (`install.sh`). Extend it. Do not add a new file.

## 3. Invariants & Guardrails
- **Branch**: do NOT use `feat/git-post-merge-auto-update`. It holds unrelated uncommitted work. Run `git checkout -b fix/ci-powershell-syntax-check` from `main`, or stash the other work first. Never work on `main` directly.
- Do not change `install.ps1`.
- Python >= 3.10. Use only the stdlib (`unittest`, `subprocess`, `shutil`).
- Keep the test skip-safe: skip the real-parse test when no `powershell`/`pwsh` is on PATH, so Linux/macOS CI is unaffected.

## 4. Files
| File | Action |
|------|--------|
| `.github/workflows/ci.yml` | Modify the Windows PowerShell step |
| `tests/test_installer_syntax.py` | Add 2 tests |

## 5. Step-by-Step TDD Tasks

### Task 1: Regression tests (RED)
- **ACTION**: Add to `TestInstallerSyntax`:
  - `test_ci_powershell_step_declares_ref_variables`: read `.github/workflows/ci.yml`. If it contains `[ref]$errors`, assert that a `$errors =` assignment appears earlier in the text. The same check applies to `$tokens` if `[ref]$tokens` is used.
  - `test_install_ps1_parses_without_errors`: skipped when `powershell`/`pwsh` is missing. Run `ParseFile` on `install.ps1` with pre-declared variables, and assert the output reports 0 errors.
- **TEST_FIRST**: `tests/test_installer_syntax.py::test_ci_powershell_step_declares_ref_variables`. Fixture: the current `ci.yml`. Expected: it fails now, because no assignment precedes `[ref]$errors`.
- **IMPLEMENT**: tests only.
- **MICRO_VALIDATE**: `python -m unittest tests.test_installer_syntax -v` (the CI-step test must FAIL for the expected reason). Then `python .agents/scripts/verify_shift_left.py --changed`.

### Task 2: Fix the CI step (GREEN)
- **ACTION**: Replace the `run:` body of the `Verify PowerShell script syntax (Windows)` step with the contract snippet from the PRD. Declare `$tokens` and `$errors`, pass an absolute path, print `Extent.StartLineNumber` and `Message` per error, and `exit 1` on errors.
- **TEST_FIRST**: the Task 1 tests.
- **IMPLEMENT**: edit `ci.yml` only. Keep the `shell: powershell` and `if: runner.os == 'Windows'` lines.
- **MICRO_VALIDATE**: `python -m unittest tests.test_installer_syntax -v` (GREEN). Then `python .agents/scripts/verify_shift_left.py --changed`.

### Task 3: Negative-path check and full verification
- **ACTION**: Locally run the snippet against a temp file containing `if (` and confirm it exits 1 with a line number. Then run it against `install.ps1` and confirm exit 0.
- **MICRO_VALIDATE**:
  - `python -m unittest discover tests`
  - `python .agents/scripts/verify_shift_left.py --changed`
  - `python .agents/scripts/verify_shift_left.py --all-checks`
  - Push the branch and confirm the Windows CI jobs go green.

## 6. Reusable Existing Code
- `tests/test_installer_syntax.py` (`repo_root`, `install_ps1` fixtures, and the shell-discovery pattern).

## 7. Risks & Mitigations
| Risk | Mitigation |
|------|------------|
| The text-based test is brittle against YAML reformatting | Match only on `[ref]$errors` and a preceding `$errors =`. Do not assert exact whitespace. |
| The real-parse test is flaky on machines without PowerShell | `skipUnless(shutil.which("powershell") or shutil.which("pwsh"))` |
| A relative-path resolution mismatch on the runner | Use `Join-Path $PWD "install.ps1"` |
| Committing alongside the unrelated hook work | Use a separate fix branch and stage only the 2 files above. |

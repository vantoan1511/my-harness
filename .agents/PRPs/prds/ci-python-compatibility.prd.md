# Spec: CI Python 3.10/3.11 Compatibility & Syntax Guardrails

## 1. Intent & Problem Statement
- **User Intent**: Check and fix GitHub Actions CI test failure: `SyntaxError: f-string expression part cannot include a backslash` during `python -m unittest discover tests`.
- **Problem**: In Python versions prior to 3.12 (specifically Python 3.10 and 3.11), backslashes inside f-string expressions (e.g. `f"{...lstrip('\r\n')}"`) are invalid syntax. In `template/.agents/skills/pr-changelog/scripts/generate_changelog.py` and `.agents/skills/pr-changelog/scripts/generate_changelog.py`, lines 388, 396, 404, and 412 use `\r\n` inside `{after_header.lstrip('\r\n')}`. While this compiles in Python 3.12+ (PEP 701), CI runs on Python 3.10 and crashes with `SyntaxError: f-string expression part cannot include a backslash` when loading `test_pr_changelog.py`.
- **Target Outcome**:
  1. `generate_changelog.py` in both `template/` and `.agents/` works across all supported Python versions (`>=3.10`).
  2. A new automated shift-left test (`tests/test_python_syntax.py`) detects any backslash inside f-string expressions across the entire codebase to prevent future regressions.
  3. GitHub Actions CI matrix passes cleanly on Python 3.10 and 3.12 across Ubuntu, macOS, and Windows.

---

## 2. Technical Architecture & Invariants

### Compatibility Contract
- The project contract defined in `pyproject.toml` is `requires-python = ">=3.10"`.
- All Python scripts across `harness.py`, `scripts/`, `template/.agents/`, `.agents/`, and `tests/` must be 100% syntactically valid in Python 3.10.

### Syntax Invariant
- **Rule**: No backslash characters (`\`) may be embedded inside `{...}` replacement fields in f-strings.
- **Remediation Pattern**:
  ```python
  # Non-compliant (fails Python < 3.12):
  return f"{content}\n{suffix.lstrip('\r\n')}"

  # Compliant (works on Python >= 3.7):
  suffix_cleaned = suffix.lstrip('\r\n')
  return f"{content}\n{suffix_cleaned}"
  ```

---

## 3. Scope Boundaries

- **In Scope**:
  - Refactor `insert_into_changelog` in `template/.agents/skills/pr-changelog/scripts/generate_changelog.py` and `.agents/skills/pr-changelog/scripts/generate_changelog.py` to extract `after_header.lstrip('\r\n')` prior to string interpolation.
  - Implement unit test in `tests/test_python_syntax.py` inspecting AST / f-string expressions across the codebase for Python 3.10 compliance.
  - Verify full test suite passes locally.
  - Update global plugin via `python harness.py update --force`.
- **Out of Scope**:
  - Modifying unreleased changelog parsing logic or changing behavior of `insert_into_changelog`.
  - Upgrading minimum Python requirement to 3.12 (Python 3.10 support must be preserved).

---

## 4. Acceptance Criteria

- [x] AC-1: `generate_changelog.py` contains zero backslashes inside f-string expressions.
- [x] AC-2: `template/.agents/skills/pr-changelog/scripts/generate_changelog.py` and `.agents/skills/pr-changelog/scripts/generate_changelog.py` are strictly synchronized.
- [x] AC-3: `tests/test_python_syntax.py` passes and asserts all project `.py` files contain zero backslashes inside f-string expressions.
- [x] AC-4: `python -m unittest discover tests` passes all tests without syntax errors.
- [x] AC-5: `python scripts/verify_shift_left.py --changed` passes with zero violations.

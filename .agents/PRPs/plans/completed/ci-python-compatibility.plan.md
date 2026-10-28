# Implementation Plan: CI Python 3.10/3.11 Compatibility & Syntax Guardrails

## 1. Overview & Objectives
- **Source Spec**: [.agents/PRPs/prds/ci-python-compatibility.prd.md](file:///d:/Projects/my-harness/.agents/PRPs/prds/ci-python-compatibility.prd.md)
- **Goal**: Resolve CI test failure on Python 3.10 where f-strings with backslashes raise `SyntaxError: f-string expression part cannot include a backslash`, and establish automated tests to prevent syntax regressions across Python 3.10+.

---

## 2. Invariants & Guardrails
- **Branch**: Dedicated branch `fix/ci-python-compatibility` (never on `main`).
- **Python Compatibility**: Must remain fully compatible with `Python >= 3.10` per `pyproject.toml`.
- **Shift-Left Micro-Validation**: Execute `python scripts/verify_shift_left.py --changed` after every file edit.
- **Parity**: Keep `template/.agents/skills/pr-changelog/scripts/generate_changelog.py` and `.agents/skills/pr-changelog/scripts/generate_changelog.py` in 100% parity.

---

## 3. Step-by-Step TDD Tasks

### Task 1: Create Python Syntax Guardrail Test (RED Gate)
- **Action**: Create `tests/test_python_syntax.py` to inspect all Python files in the repository.
- **Test First**:
  - Traverse all `.py` files in the repository (skipping `.git`, build directories, and sandbox environments).
  - Parse each file with `ast.parse` and inspect `FormattedValue` / f-string expressions.
  - Fail if any f-string expression contains a backslash (`\`), citing PEP 701 incompatibility with Python 3.10/3.11.
- **Expected Assertion**: The test MUST initially fail (RED) identifying the 8 existing occurrences in `generate_changelog.py`.
- **Micro-Validate**: `python -m unittest tests/test_python_syntax.py`

### Task 2: Remediate `generate_changelog.py` in Template and Workspace (GREEN Gate)
- **Action**: Fix `insert_into_changelog` in both files:
  - `template/.agents/skills/pr-changelog/scripts/generate_changelog.py`
  - `.agents/skills/pr-changelog/scripts/generate_changelog.py`
- **Implementation**:
  - Clean `after_header` into `after_cleaned = after_header.lstrip('\r\n')` prior to returning f-string:
    ```python
    after_cleaned = after_header.lstrip('\r\n')
    return f"{existing_content[:header_end]}\n\n{new_entries_cleaned}\n{after_cleaned}"
    ```
- **Micro-Validate**:
  - `python -m unittest tests/test_python_syntax.py` (Asserts test is now GREEN).
  - `python scripts/verify_shift_left.py --changed`

### Task 3: Full Test Suite & Plugin Synchronization (REFACTOR & VERIFY)
- **Action**:
  - Run full test discovery to confirm all 60+ tests pass.
  - Refresh global plugin via `python harness.py update --force`.
  - Run all shift-left static checks.
- **Validation Commands**:
  - `python -m unittest discover tests`
  - `python scripts/verify_shift_left.py --all-checks`

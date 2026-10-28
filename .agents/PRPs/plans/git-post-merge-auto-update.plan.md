# Implementation Plan: Git Post-Merge Auto-Update Hook

## 1. Overview & Objectives
- **Source Spec**: [.agents/PRPs/prds/git-post-merge-auto-update.prd.md](file:///d:/Projects/my-harness/.agents/PRPs/prds/git-post-merge-auto-update.prd.md)
- **Goal**: Implement `install-hooks` command and git `post-merge` hook installer to auto-sync the global Antigravity plugin upon pulling or merging upstream changes.

---

## 2. Invariants & Guardrails
- **Branch**: Dedicated branch `feat/git-post-merge-auto-update` (never on `main`).
- **Python Compatibility**: Full compatibility with Python >= 3.10.
- **Cross-Platform**: Works seamlessly in Windows Git Bash / POSIX shells without throwing execution errors.
- **Shift-Left Micro-Validation**: Run `python .agents/scripts/verify_shift_left.py --changed` after every file edit.

---

## 3. Step-by-Step TDD Tasks

### Task 1: Create Unit Tests for Git Hooks Installation (RED Gate)
- **Action**: Create `tests/test_git_hooks.py` testing:
  - `is_git_hook_installed(repo_root)` returns False when no hook exists.
  - `install_git_hooks(repo_root)` creates `.git/hooks/post-merge` containing `harness.py update --force`.
  - Hook installation is idempotent.
  - Hook content handles Python interpreter resolution gracefully.
- **Test File**: `tests/test_git_hooks.py`
- **Micro-Validate**: `python -m unittest tests/test_git_hooks.py` (Must fail initially as RED).

### Task 2: Implement Git Hook Logic in `harness.py` (GREEN Gate)
- **Action**:
  - Implement `install_git_hooks(repo_root)` and `is_git_hook_installed(repo_root)`.
  - Add `install-hooks` subcommand in `build_parser()` and dispatch in `main()`.
  - Add hook status check in `cmd_doctor()`.
- **Micro-Validate**: `python -m unittest tests/test_git_hooks.py` (Must PASS as GREEN).

### Task 3: Install the hook in current repo & Full Verification
- **Action**:
  - Run `python harness.py install-hooks` to install the hook in `d:\Projects\my-harness`.
  - Run `python harness.py doctor`.
  - Run full test suite: `python -m unittest discover tests`.
  - Run shift-left pre-flight: `python .agents/scripts/verify_shift_left.py --all-checks`.

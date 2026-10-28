# Spec: Git Post-Merge Auto-Update Hook for my-harness

## 1. Intent & Problem Statement
- **User Intent**: Automatically synchronize and update the globally installed Antigravity plugin (`my-harness`) whenever git merges or pulls take place in the `my-harness` repository.
- **Problem**:
  Currently, after modifying or pulling skills/rules/templates in `d:\Projects\my-harness`, the globally installed Antigravity plugin at `~/.gemini/config/plugins/my-harness` is not automatically refreshed unless the user manually remembers to invoke `python harness.py update --force`. If this step is omitted, the active plugin drifts from the repository state.
- **Target Outcome**:
  1. Add a dedicated `install-hooks` subcommand to `harness.py`.
  2. Implement cross-platform `.git/hooks/post-merge` setup that detects Python on both POSIX and Windows and triggers `harness.py update --force` non-blockingly.
  3. Ensure `harness doctor` verifies and reports the health/presence of the post-merge auto-update hook.
  4. Provide unit tests validating installation, idempotency, execution safety, and doctor diagnostics.

---

## 2. User Experience & Interactions

### CLI Commands
- `harness install-hooks`:
  - Installs `.git/hooks/post-merge` in the repository root.
  - Automatically makes the hook executable (`chmod +x` on Unix).
  - Reports `[PASS] Installed git post-merge auto-update hook (.git/hooks/post-merge)`.
- `harness doctor`:
  - Under Section 4/5 (Git & Environment checks), inspects `.git/hooks/post-merge` and reports:
    - `[PASS] Git post-merge auto-update hook active` (if installed)
    - `[INFO] Git post-merge auto-update hook not installed. Run 'harness install-hooks' to auto-sync on pull/merge.` (if not installed)

---

## 3. Acceptance Criteria
- [ ] AC-1: `harness.py` provides `install_git_hooks(repo_root)` and `is_git_hook_installed(repo_root)` functions.
- [ ] AC-2: Running `harness install-hooks` installs a cross-platform executable post-merge hook.
- [ ] AC-3: `harness doctor` checks and surfaces hook status.
- [ ] AC-4: All unit tests pass (`python -m unittest discover tests`).
- [ ] AC-5: Shift-left pre-flight verification passes cleanly.

# Spec: Antigravity Plugin Auto & Semi-Auto Update System

## 1. Intent & Problem Statement
- **User Intent**: Make the `my-harness` Antigravity plugin auto-update or semi-auto update via script.
- **Problem**:
  Currently, `my-harness` installs its global Antigravity plugin (`~/.gemini/config/plugins/my-harness`) only during initial setup (`harness init --scope global`). When improvements, bug fixes, or new skills/rules are made to `my-harness`, there is no streamlined way to update the installed plugin. Users have to manually remember to re-run init, manually pull git changes, or re-copy files. Furthermore, there is no background check to notify users when a newer commit or release is available upstream.
- **Target Outcome**:
  1. A one-command update workflow (`harness update` and `./install.ps1 -Command update` / `./install.sh update`) that fetches the latest upstream changes (via `git pull` when inside a git clone or HTTP fallback), packages and syncs the plugin into `~/.gemini/config/plugins/my-harness`, updates the global pip CLI, and optionally syncs the active project's `.agents/` folder.
  2. A lightweight, non-blocking update detector that checks for updates (throttled to at most once per 24 hours) and alerts the user with an actionable message during doctor/init/fix operations.
  3. Seamless support across Windows PowerShell (`install.ps1`) and Unix shell (`install.sh`).

---

## 2. User Experience & Interactions

### CLI Commands
- `harness update`:
  - Fetches and pulls latest commits from `origin/main` (if inside git repo).
  - Bundles and updates `~/.gemini/config/plugins/my-harness` (manifest, skills, consolidated `rules/AGENTS.md`, logo assets, README).
  - Re-registers `harness` CLI globally via `pip install -e .`.
  - Displays summary of updated files and informs user whether Antigravity reload/restart is recommended.
- `harness update --check-only`:
  - Checks if an upstream update is available without pulling or mutating files.
- `harness update --sync-project [path]`:
  - Additionally syncs core skills, scripts, and rules to the project `.agents/` directory at `[path]` (default: current directory).
- `harness update --force`:
  - Force re-packages and deploys plugin files even if git says the repository is already up to date.

### Installer Scripts
- Windows (`install.ps1`):
  - Interactive menu includes `[4] Update - Pull latest harness & update global Antigravity plugin`.
  - Direct execution: `.\install.ps1 -Command update` (or `.\install.ps1 update`).
- Unix/macOS (`install.sh`):
  - Interactive menu includes `4) Update - Pull latest harness & update global Antigravity plugin`.
  - Direct execution: `bash install.sh update`.

### Background Notification
- During `harness doctor`, `harness fix`, and CLI runs:
  - If more than 24 hours have elapsed since the last check, performs a background check against upstream `origin/main`.
  - If commits are pending, outputs a non-blocking notification:
    `[UPDATE AVAILABLE] Newer version of my-harness available! Run 'harness update' or '.\install.ps1 -Command update' to refresh.`

---

## 3. Contract-First Boundaries

### CLI Interface Contract
```python
@dataclass
class UpdateCheckResult:
    is_git_repo: bool
    current_commit: str
    remote_commit: str
    has_update: bool
    behind_count: int
    error: Optional[str] = None

@dataclass
class PluginDeploymentResult:
    plugin_dir: Path
    manifest_updated: bool
    skills_copied: int
    rules_consolidated: bool
    assets_copied: bool
    pip_updated: bool
    errors: list[str]
```

### Manifest Schema & Cache Contract (`~/.gemini/config/plugins/my-harness/plugin.json`)
```json
{
  "name": "my-harness",
  "displayName": "Agent Engineering DevKit",
  "version": "0.1.0",
  "description": "Shift-left SDLC workflows: spec-first design, TDD loops, code review, and automated PR delivery.",
  "logo": "assets/logo.svg",
  "suggestedPrompts": [
    "/specify design contract and implementation plan for a new feature",
    "/tdd-workflow implement failing tests first then pass them",
    "/code-review inspect uncommitted changes against quality constitution"
  ]
}
```

### Throttled Check State (`~/.gemini/config/plugins/my-harness/.update_check.json` or `~/.agents/.update_check.json`)
```json
{
  "last_check_timestamp": 1728648000.0,
  "last_known_remote_commit": "abc1234",
  "has_update": false
}
```

### Error Handling & Fallbacks
1. **Offline / No Network**: Update check fails silently without throwing exceptions or blocking the CLI.
2. **Dirty Git Working Tree**: If the local repository has uncommitted changes, `harness update` warns the user and does NOT discard changes; it offers to update the plugin from current working tree files using `--force` without overwriting uncommitted code.
3. **No Git Installed / Standalone**: If git is unavailable or repo is downloaded as zip, update attempts HTTP fetch from GitHub API or falls back to deploying existing source tree into the plugin directory.

---

## 4. Scope Boundaries

### In Scope (v1)
- Add `harness update` command with `--check-only`, `--force`, `--sync-project`, and `--branch` options.
- Refactor and centralize `deploy_antigravity_plugin()` function shared between `init` and `update`.
- Add throttled background update-check helper (`check_for_updates`, `should_check_for_updates`, `save_update_check_state`).
- Update `install.ps1` and `install.sh` to include `update` subcommands and interactive options.
- Comprehensive unit tests covering update check, plugin deployment, and CLI commands.
- Verify zero regressions across `test_harness_init.py`, `test_harness_fix.py`, `test_installer_e2e.py`.

### Out of Scope
- Automatic self-modifying cron daemons modifying files while an IDE session is mid-conversation without user confirmation.
- Windows service registration or system daemon installation.

---

## 5. Acceptance Criteria
- [ ] **AC-1**: Running `harness update` on a machine with global plugin installed successfully updates `~/.gemini/config/plugins/my-harness` with latest skills, consolidated rules, and manifest.
- [ ] **AC-2**: Running `harness update --check-only` reports whether upstream changes are available without modifying filesystem.
- [ ] **AC-3**: Running `harness update --sync-project` updates both global plugin and target project's `.agents/` folder.
- [ ] **AC-4**: `install.ps1` and `install.sh` support `update` argument and interactive selection menu.
- [ ] **AC-5**: Throttled check detects upstream commits and warns non-intrusively without network crashes when offline.
- [ ] **AC-6**: All tests pass (`python -m unittest discover tests`) with zero errors.
- [ ] **AC-7**: Static pre-flight check (`python .agents/scripts/verify_shift_left.py --changed`) passes cleanly.

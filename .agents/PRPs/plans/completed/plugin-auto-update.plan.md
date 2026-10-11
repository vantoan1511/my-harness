# Implementation Plan: Antigravity Plugin Auto & Semi-Auto Update System

## 1. Overview & Source
- **Feature Name**: Antigravity Plugin Auto & Semi-Auto Update System
- **Source PRD**: [.agents/PRPs/prds/plugin-auto-update.prd.md](file:///d:/Projects/my-harness/.agents/PRPs/prds/plugin-auto-update.prd.md)
- **Target Components**:
  - `harness.py`: Core CLI update command, plugin deployer refactor, git update checker, throttled notification logic.
  - `install.ps1`: Windows PowerShell installer update command & menu option.
  - `install.sh`: Unix/macOS Bash installer update command & menu option.
  - `tests/test_harness_update.py`: Unit tests for plugin deployment, update check, and CLI commands.

---

## 2. Interface & Boundary Contracts

### Data Structures (`harness.py`)
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
    errors: list[str] = field(default_factory=list)
```

### Manifest Invariant (`~/.gemini/config/plugins/my-harness/plugin.json`)
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

---

## 3. Step-by-Step TDD Tasks

### Task 1: Refactor and Centralize `deploy_antigravity_plugin`
- **ACTION**: Extract plugin deployment logic from `cmd_init` into a shared, robust function `deploy_antigravity_plugin(harness_root: Path, target_plugin_dir: Path, pack: Optional[str] = None) -> PluginDeploymentResult`. Use it in `cmd_init`.
- **TEST_FIRST**:
  - Test File: `tests/test_harness_update.py`
  - Test Name: `test_deploy_antigravity_plugin_creates_valid_structure`
  - Input: Mock home directory with `.gemini/config/plugins/` structure.
  - Assertions:
    - Returns `PluginDeploymentResult` with `manifest_updated=True`, `rules_consolidated=True`.
    - `plugin.json` exists and parses cleanly.
    - `rules/AGENTS.md` contains combined rules (`shift-left-quality.md`, `review-rules.md`, `natural-human-writing.md`).
    - `skills/` contains core skills (`specify`, `implement`, etc.).
- **IMPLEMENT**:
  - Implement `deploy_antigravity_plugin` in `harness.py`.
  - Update `cmd_init` to call `deploy_antigravity_plugin`.
- **MICRO_VALIDATE**:
  - `python -m unittest tests/test_harness_update.py`
  - `python -m unittest tests/test_harness_init.py`
  - `python .agents/scripts/verify_shift_left.py --changed`

### Task 2: Implement Upstream Git Check & Throttled Notification
- **ACTION**: Add `check_for_updates(harness_root: Path, branch: str = "main") -> UpdateCheckResult` and `should_check_for_updates(cache_file: Path, interval_hours: int = 24) -> bool`.
- **TEST_FIRST**:
  - Test File: `tests/test_harness_update.py`
  - Test Names:
    - `test_check_for_updates_detects_behind_commits`
    - `test_check_for_updates_handles_network_or_git_errors_cleanly`
    - `test_should_check_for_updates_throttling`
  - Input: Subprocess mock returning behind commits and network failures.
  - Assertions:
    - `res.has_update == True`, `res.behind_count == 3` when git rev-list returns 3 commits.
    - Returns `has_update=False`, `error != None` without uncaught exceptions on network failure.
    - Throttling returns `False` if checked within 24 hours.
- **IMPLEMENT**:
  - Implement `check_for_updates` using non-blocking git rev-parse / rev-list commands.
  - Implement cache timestamp read/write at `~/.gemini/config/plugins/my-harness/.update_check.json`.
- **MICRO_VALIDATE**:
  - `python -m unittest tests/test_harness_update.py`
  - `python .agents/scripts/verify_shift_left.py --changed`

### Task 3: Implement `cmd_update` CLI in `harness.py`
- **ACTION**: Add `cmd_update(args)` and register `update` subparser with `--check-only`, `--force`, `--sync-project`, and `--branch`.
- **TEST_FIRST**:
  - Test File: `tests/test_harness_update.py`
  - Test Names:
    - `test_cmd_update_check_only_does_not_mutate_plugin`
    - `test_cmd_update_repackages_plugin_and_updates_manifest`
    - `test_cmd_update_with_sync_project_updates_local_agents`
  - Input: CLI arguments mock with mock target project and mock plugin dir.
  - Assertions:
    - `--check-only` exits with status 0 and does not write files.
    - Default update deploys new skills and rules to `~/.gemini/config/plugins/my-harness`.
    - `--sync-project` syncs template `.agents/` to project directory.
- **IMPLEMENT**:
  - Implement `cmd_update` handling git pull, plugin deployment, pip install, and project sync.
  - Wire into argument parser in `build_parser()` and `main()`.
- **MICRO_VALIDATE**:
  - `python -m unittest tests/test_harness_update.py`
  - `python -m unittest discover tests`
  - `python .agents/scripts/verify_shift_left.py --changed`

### Task 4: Update Installer Scripts (`install.ps1` and `install.sh`)
- **ACTION**: Add `update` command and menu option 4 to `install.ps1` and `install.sh`.
- **TEST_FIRST**:
  - Test File: `tests/test_installer_e2e.py`
  - Test Name: `test_installer_update_subcommand`
  - Input: Running `install.ps1 -Command update` / `install.sh update` in test sandbox.
  - Assertions: Process returns code 0 and executes `harness.py update`.
- **IMPLEMENT**:
  - Update `install.ps1` to handle `-Command update` and interactive menu choice `[4] Update`.
  - Update `install.sh` to handle `update` command and interactive menu choice `4) Update`.
- **MICRO_VALIDATE**:
  - `python -m unittest tests/test_installer_e2e.py`
  - `python .agents/scripts/verify_shift_left.py --changed`

### Task 5: Full Verification & Pre-Flight
- **ACTION**: Run full test suite and shift-left scanner.
- **MICRO_VALIDATE**:
  - `python -m unittest discover tests`
  - `python .agents/scripts/verify_shift_left.py --changed`
  - `git status -s`

---

## 4. Risks & Mitigations
| Risk | Mitigation |
|---|---|
| User has local modifications in `my-harness` clone | `harness update` checks `git status --porcelain` and aborts git pull if dirty, warning user and allowing `--force` to update plugin from local files. |
| Network offline during update check | Exception handled silently, returning cached or no-op state without terminating agent or CLI. |
| Antigravity running while plugin files are overwritten | Antigravity dynamically loads skills on demand and rules on session start; files written atomically so open sessions don't corrupt. User receives a reminder to restart if new skills or commands were added. |

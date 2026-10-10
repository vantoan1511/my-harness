# Spec: Fix Command & Global Deduplication

## 1. Intent & Problem Statement
- **User Intent**: Update the harness script to add a `fix` command that fixes project-scope installed `.agents/`. If users have already installed globally, remove duplicates in project scope to prevent conflicts.
- **Problem**: When a user installs `my-harness` globally (`~/.gemini/config/plugins/my-harness` and/or `~/.agents`), all core skills and rules are registered globally. If a project subsequently or previously initialized a project-scope `.agents/` setup, all skills and rules are duplicated across project and global scopes. This causes duplicate skill registrations in Antigravity prompts, bloats LLM context windows, creates rule duplication, and risks behavioral drift. Additionally, corrupted or incomplete project-scope `.agents` setups have no automated repair mechanism.
- **Target Outcome**: 
  1. A new `harness fix [target] [--dry-run]` CLI subcommand that repairs corrupted/missing project-scope directories, scripts, and configs, and detects global installations to safely prune duplicate skills and rules from the project scope while preserving project-specific custom skills and rules.
  2. `harness doctor` warns when duplicate global skills/rules exist in the project and suggests running `harness fix`.
  3. `harness init [target] --scope project` detects existing global installations and skips installing duplicate skills and rules during initial scaffolding.

## 2. User Experience & Interactions
- **Placement**: CLI subcommands on `harness.py`:
  - `harness fix [target] [--dry-run]`
  - `harness doctor [target]`
  - `harness init [target] [--scope project]`
- **Interaction Flow**:
  1. User runs `harness fix` in a project directory where `my-harness` is already installed globally.
  2. The harness verifies target structure, repairs any missing required directories (`PRPs`, `logs`, `reviews`, `scripts`, etc.) and core scripts.
  3. The harness inspects global plugins (`~/.gemini/config/plugins/my-harness`) and global `.agents` (`~/.agents`).
  4. The harness identifies identical duplicate skills in `<target>/.agents/skills/` and removes them, keeping any user-created custom skills intact.
  5. The harness identifies identical duplicate template rules in `<target>/.agents/rules/` and removes them, keeping any custom rules intact.
  6. The harness prints a color-coded summary of repaired directories, restored scripts, and pruned duplicate items.
  7. If `--dry-run` is passed, it previews the planned repairs and deletions without modifying disk.

## 3. Contract-First Boundaries

### CLI Argument Contract
```python
# Subcommand parser for 'fix'
p_fix = subparsers.add_parser("fix", help="Repair project-scope .agents setup and remove duplicates if globally installed")
p_fix.add_argument("target", nargs="?", default=".", help="Target project directory (default: current directory)")
p_fix.add_argument("--dry-run", action="store_true", help="Preview repairs and deduplications without making changes")
```

### Global Detection Data Model
```python
from dataclasses import dataclass, field
from pathlib import Path
from typing import Set, Optional

@dataclass
class GlobalInstallationInfo:
    is_installed: bool
    plugin_dir: Optional[Path] = None
    global_agents_dir: Optional[Path] = None
    global_skills: Set[str] = field(default_factory=set)
    global_rules: Set[str] = field(default_factory=set)
```

### Function Contracts
```python
def detect_global_installation() -> GlobalInstallationInfo:
    """Inspects ~/.gemini/config/plugins/my-harness and ~/.agents.
    Returns structured info on global installation state, skills, and rules.
    """
    ...

def repair_project_structure(target_agents: Path, dry_run: bool = False) -> dict:
    """Ensures all standard .agents directories and .gitkeep files exist.
    Returns summary dict of created/existing paths.
    """
    ...

def repair_project_scripts(target_agents: Path, template_agents: Path, dry_run: bool = False) -> dict:
    """Restores missing core scripts (verify_shift_left.py, shift_left_hook.py, etc.).
    Returns summary dict of restored scripts.
    """
    ...

def repair_project_configs(target_dir: Path, target_agents: Path, template_agents: Path, dry_run: bool = False) -> dict:
    """Validates and repairs harness.config.json and hooks.json.
    Returns summary dict of repaired configs.
    """
    ...

def deduplicate_project_scope(target_agents: Path, global_info: GlobalInstallationInfo, dry_run: bool = False) -> dict:
    """Removes duplicate skills and rules from target_agents if present in global_info.
    Preserves custom skills and custom rules not present in global installation.
    Returns summary dict of removed skills, removed rules, and preserved items.
    """
    ...

def cmd_fix(args) -> int:
    """Handler for `harness fix` command. Returns exit code (0 on success)."""
    ...
```

## 4. Scope Boundaries
- **In Scope (v1)**:
  - Implement `detect_global_installation()` in `harness.py`.
  - Implement `harness fix` subcommand with optional target and `--dry-run` flag.
  - Structure repair: Recreate missing standard `.agents/` directories and core scripts from template.
  - Config repair: Verify/restore `harness.config.json` and `hooks.json`.
  - Skill deduplication: Remove matching skills from `<target>/.agents/skills/` that exist globally in plugin or global `.agents`.
  - Rule deduplication: Remove matching template rules from `<target>/.agents/rules/` that exist globally in plugin or global `.agents`.
  - Preserve custom skills and custom rules in project scope.
  - Update `harness doctor` to detect duplicates and suggest `harness fix`.
  - Update `harness init` in project scope to skip duplicating skills and rules if global installation is already present.
  - Full unit and integration tests covering detection, repair, deduplication, `--dry-run`, and preservation of custom items.

- **Out of Scope**:
  - Deleting or modifying project root `AGENTS.md` (project-specific rules and instructions must remain under user control).
  - Removing project `.agents/references` or project PRP files.
  - Modifying global installations during a project `fix` run.

## 5. Acceptance Criteria
- [ ] AC-1: `harness fix` runs successfully on a valid project and exits with code 0.
- [ ] AC-2: When global installation is present, `harness fix` removes duplicate skills from `<target>/.agents/skills/` and duplicate rules from `<target>/.agents/rules/`.
- [ ] AC-3: Custom skills and custom rules present in `<target>/.agents/` that do not exist in global installation are preserved untouched.
- [ ] AC-4: When run with `--dry-run`, `harness fix` reports planned changes without deleting or modifying files on disk.
- [ ] AC-5: `harness fix` repairs missing standard directories, missing core scripts (`verify_shift_left.py`, `shift_left_hook.py`, etc.), and missing/invalid configs.
- [ ] AC-6: `harness doctor` detects duplicate skills/rules when global is installed and warns user to run `harness fix`.
- [ ] AC-7: `harness init --scope project` detects global installation and skips installing duplicate skills/rules.
- [ ] AC-8: Full test suite passes and pre-flight static verification (`verify_shift_left.py --changed`) passes with zero errors.

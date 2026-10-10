# Implementation Plan: Fix Command & Global Deduplication

- **Source PRD**: [.agents/PRPs/prds/fix-command-deduplication.prd.md](file:///d:/Projects/my-harness/.agents/PRPs/prds/fix-command-deduplication.prd.md)
- **Target Component**: `harness.py`, `tests/test_harness_fix.py`, `tests/test_harness_init.py`

---

## 1. Problem Statement & Architecture Summary

When `my-harness` is installed globally (`~/.gemini/config/plugins/my-harness` and/or `~/.agents`), Antigravity loads all standard skills and rules globally. When a project also initializes `.agents/`, identical skills and rules exist in both project and global scopes. This causes duplicate skill registrations in Antigravity prompts and LLM context bloat.

This plan introduces:
1. `detect_global_installation()` helper to detect global plugin and `~/.agents` installations and extract available skills and rules.
2. `harness fix [target] [--dry-run]` command to repair missing project directories/scripts/configs and prune duplicate skills and template rules while preserving project-specific custom skills/rules.
3. Enhanced `harness doctor` that flags duplicate project-scope skills/rules and advises running `harness fix`.
4. Enhanced `harness init` that skips copying duplicate skills/rules during fresh project initialization if global is detected.

---

## 2. Contracts & Boundary Models

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

CLI Interface:
```bash
harness fix [target] [--dry-run]
harness doctor [target]
harness init [target] [--scope project|global]
```

---

## 3. Step-by-Step TDD Tasks

### Task 1: Global Installation Detection
- **ACTION**: Add `GlobalInstallationInfo` dataclass and `detect_global_installation()` in `harness.py`.
- **TEST_FIRST**:
  - Test file: `tests/test_harness_fix.py`
  - Test names: `test_detect_global_installation_none`, `test_detect_global_installation_plugin`, `test_detect_global_installation_agents_dir`
  - Input fixtures: Mock `Path.home()` with empty directory, with `.gemini/config/plugins/my-harness`, and with `.agents`.
  - Assertions: `is_installed` boolean is accurate; `global_skills` set contains discovered skill directory names; `global_rules` set contains rule filenames.
- **IMPLEMENT**: Implement `detect_global_installation()` in `harness.py`.
- **MICRO_VALIDATE**:
  ```bash
  python -m unittest tests/test_harness_fix.py
  python .agents/scripts/verify_shift_left.py --changed
  ```

---

### Task 2: Project Deduplication Logic with Custom Item Preservation
- **ACTION**: Implement `deduplicate_project_scope(target_agents, global_info, dry_run=False)` in `harness.py`.
- **TEST_FIRST**:
  - Test file: `tests/test_harness_fix.py`
  - Test names: `test_deduplicate_removes_matching_skills_and_rules`, `test_deduplicate_preserves_custom_skills_and_rules`, `test_deduplicate_dry_run`
  - Input fixtures: Temporary project `.agents` containing standard skills (`code-review`, `specify`) and custom skill (`my-custom-tool`), plus standard rules (`shift-left-quality.md`) and custom rule (`project-conventions.md`).
  - Assertions:
    - Standard skills and rules matching `global_info` are deleted.
    - Custom skill (`my-custom-tool`) and custom rule (`project-conventions.md`) remain untouched.
    - In dry-run mode, no files are unlinked/removed.
- **IMPLEMENT**: Add `deduplicate_project_scope()` in `harness.py`.
- **MICRO_VALIDATE**:
  ```bash
  python -m unittest tests/test_harness_fix.py
  python .agents/scripts/verify_shift_left.py --changed
  ```

---

### Task 3: Comprehensive Project Repair Helpers
- **ACTION**: Implement `repair_project_structure()`, `repair_project_scripts()`, and `repair_project_configs()` in `harness.py`.
- **TEST_FIRST**:
  - Test file: `tests/test_harness_fix.py`
  - Test names: `test_repair_project_missing_dirs_and_scripts`, `test_repair_project_configs`
  - Input fixtures: Incomplete target directory missing `PRPs/plans`, missing `verify_shift_left.py`, corrupted or missing `harness.config.json`.
  - Assertions:
    - All expected directories created (`PRPs`, `logs`, `reviews`, etc.).
    - Core scripts copied from `template/.agents/scripts`.
    - Valid `harness.config.json` generated/merged with detected stack commands.
    - Valid `hooks.json` restored if missing.
- **IMPLEMENT**: Implement repair helpers in `harness.py`.
- **MICRO_VALIDATE**:
  ```bash
  python -m unittest tests/test_harness_fix.py
  python .agents/scripts/verify_shift_left.py --changed
  ```

---

### Task 4: CLI Parser Integration & `cmd_fix` Handler
- **ACTION**: Register `fix` subcommand in `build_parser()` and implement `cmd_fix()` handler.
- **TEST_FIRST**:
  - Test file: `tests/test_harness_fix.py`
  - Test names: `test_parser_fix_args`, `test_cmd_fix_e2e_execution`
  - Input fixtures: CLI invocations `harness.py fix` and `harness.py fix path/to/project --dry-run`.
  - Assertions: Parser populates `target` and `dry_run` fields; `cmd_fix` coordinates repair and deduplication, returning 0 on success.
- **IMPLEMENT**: Add `p_fix` subparser and `cmd_fix` in `harness.py`.
- **MICRO_VALIDATE**:
  ```bash
  python -m unittest tests/test_harness_fix.py
  python .agents/scripts/verify_shift_left.py --changed
  ```

---

### Task 5: Enhance `harness doctor` with Duplicate Detection
- **ACTION**: Update `cmd_doctor` in `harness.py` to check for duplicate skills/rules when global is installed.
- **TEST_FIRST**:
  - Test file: `tests/test_harness_fix.py`
  - Test name: `test_doctor_warns_on_duplicates`
  - Input fixtures: Project with duplicate skills while global installation is mocked.
  - Assertions: Output contains warning highlighting duplicate items and recommending `harness fix`.
- **IMPLEMENT**: Add duplicate scan step to `cmd_doctor()` in `harness.py`.
- **MICRO_VALIDATE**:
  ```bash
  python -m unittest tests/test_harness_fix.py
  python .agents/scripts/verify_shift_left.py --changed
  ```

---

### Task 6: Enhance `harness init` to Prevent Scaffolding Duplicates
- **ACTION**: Update `cmd_init` in `harness.py` so project-scope init avoids scaffolding duplicate skills/rules if global installation is detected.
- **TEST_FIRST**:
  - Test file: `tests/test_harness_init.py`
  - Test name: `test_cmd_init_project_skips_duplicates_when_global_exists`
  - Input fixtures: Mock global installation during `harness init --scope project`.
  - Assertions: Project `.agents/skills` is created but empty; core scripts, configs, and directories are present; duplicate template skills/rules are not copied.
- **IMPLEMENT**: Update skill and rule copy logic in `cmd_init()` when global is detected.
- **MICRO_VALIDATE**:
  ```bash
  python -m unittest tests/test_harness_init.py tests/test_harness_fix.py
  python .agents/scripts/verify_shift_left.py --changed
  ```

---

### Task 7: Full Test Suite & Shift-Left Pre-Flight Verification
- **ACTION**: Run full test discovery and pre-flight static verification.
- **VERIFY_COMMANDS**:
  ```bash
  python -m unittest discover tests
  python .agents/scripts/verify_shift_left.py --all-checks
  ```

# Plan: Installer Scope Selection (Project vs Global)

## Summary
Update the installer scripts (`install.ps1`, `install.sh`) and CLI (`harness.py`) to support choosing between `project` and `global` installation scopes. When running interactively, the installer prompts the user with a choice; users can also bypass the prompt via the `-Scope` / `--scope` command-line argument. Global scope installs `.agents/` into the user's home directory (`~/.agents`) and registers the `harness` CLI globally via `pip install -e .`.

## User Story
As a developer setting up AI coding workflows,
I want to choose between project-scoped and global-scoped installation in `install.ps1` and `install.sh`,
So that I can either initialize an individual project or enable agent skills/rules globally across all projects on my machine.

## Problem → Solution
- **Current State**: `install.ps1` and `install.sh` only take a target directory (defaulting to `.`) and always run `python harness.py init $Target`. There is no way to choose a global scope or install `harness` globally without manual commands.
- **Desired State**: Both installer scripts allow choosing between `project` and `global` scopes—interactively via menu prompts or directly via `-Scope` / `--scope` arguments. `harness.py init` supports `--scope {project,global}`. Selecting global initializes `~/.agents` and registers `harness` in the Python environment using `pip install -e .`.

## Metadata
- **Complexity**: Medium
- **Source PRD**: N/A
- **PRD Phase**: N/A
- **Estimated Files**: 5 (`tests/test_harness_init.py`, `harness.py`, `install.ps1`, `install.sh`, `README.md`)

---

## Mandatory Reading

| Priority | File | Lines | Why |
|---|---|---|---|
| P0 (critical) | [harness.py](file:///d:/Projects/my-harness/harness.py) | 125-192 | Current `cmd_init` behavior and argument setup |
| P0 (critical) | [install.ps1](file:///d:/Projects/my-harness/install.ps1) | 1-21 | Current PowerShell installer structure and parameter bindings |
| P0 (critical) | [install.sh](file:///d:/Projects/my-harness/install.sh) | 1-21 | Current Bash installer structure and positional args |
| P1 (important) | [README.md](file:///d:/Projects/my-harness/README.md) | 53-84 | Documented installation commands to update |

---

## Patterns to Mirror

### CLI_ARGPARSE
```python
# SOURCE: harness.py:389-393
p_init = subparsers.add_parser("init", help="Initialize .agents harness in a target project")
p_init.add_argument("target", nargs="?", default=".", help="Target project directory (default: current directory)")
p_init.add_argument("--preset", default="universal", help="Configuration preset name")
p_init.add_argument("--pack", help="Optional pack to install during init (e.g. orbit-desktop, vue-primevue)")
```

### COLOR_MESSAGING
```python
# SOURCE: harness.py:131, 139, 181
print(f"{COLOR_CYAN}==> Initializing my-harness in: {target_dir}{COLOR_RESET}")
print(f"{COLOR_GREEN}[PASS] Scaffolding .agents/ directories and core skills{COLOR_RESET}")
print(f"\n{COLOR_BOLD}{COLOR_GREEN}✓ my-harness initialization complete!{COLOR_RESET}")
```

### SHELL_ERROR_HANDLING
```powershell
# SOURCE: install.ps1:10-13
if (-not (Test-Path $harnessPy)) {
    Write-Error "harness.py not found at $harnessPy"
    exit 1
}
```

---

## Files to Change

| File | Action | Justification |
|---|---|---|
| `tests/test_harness_init.py` | CREATE | Unit tests for `--scope project` and `--scope global` handling |
| `harness.py` | UPDATE | Add `--scope` argument to `init` subparser, implement global home target and `pip install -e` execution |
| `install.ps1` | UPDATE | Add `-Scope` parameter, interactive selection prompt when omitted, forward arguments |
| `install.sh` | UPDATE | Add `--scope` / `-s` parsing, interactive menu prompt when omitted, forward arguments |
| `README.md` | UPDATE | Document project vs global installation commands and options |

## NOT Building
- Creating a separate global daemon process.
- Modifying packs internal structure.
- Breaking backwards compatibility for existing command invocations (`install.ps1 -Target dir` and `install.sh dir`).

---

## Step-by-Step Tasks

### Task 1: Unit Tests for `harness.py init --scope`
- **ACTION**: Create `tests/test_harness_init.py` using Python's standard `unittest` library.
- **TEST_FIRST**: Define test cases:
  1. `test_parse_args_default_scope`: Verifies `--scope` defaults to `"project"`.
  2. `test_parse_args_global_scope`: Verifies `--scope global` is parsed.
  3. `test_cmd_init_project_scope`: Verifies scaffolding into a custom project directory.
  4. `test_cmd_init_global_scope`: Mocks `Path.home()` and `subprocess.run` to verify scaffolding in `~/.agents` and `pip install -e .` invocation.
- **IMPLEMENT**: Write the unit tests covering argument parser and `cmd_init` branch logic.
- **MIRROR**: Follow standard Python `unittest.TestCase` pattern.
- **IMPORTS**: `unittest`, `tempfile`, `pathlib.Path`, `unittest.mock`, `harness`.
- **GOTCHA**: Ensure mock for `Path.home` does not pollute user's actual home directory during test runs.
- **MICRO_VALIDATE**: `python -m unittest tests/test_harness_init.py`

### Task 2: Implement `--scope` in `harness.py`
- **ACTION**: Update `p_init` argument parser and `cmd_init` in `harness.py`.
- **TEST_FIRST**: Run tests from Task 1 (should fail before update, pass after).
- **IMPLEMENT**:
  1. In `main()`: Add `p_init.add_argument("--scope", choices=["project", "global"], default="project", help="Installation scope: project (target directory) or global (user home ~/.agents and CLI)")`.
  2. In `cmd_init(args)`:
     - Check `args.scope`. If `"global"`:
       - Set `target_dir` to `Path.home()` if `args.target == "."` or not explicitly overridden.
       - Proceed with scaffolding `.agents/` inside `target_dir`.
       - Execute `subprocess.run([sys.executable, "-m", "pip", "install", "-e", str(harness_root)], check=True)` to install CLI globally.
       - Print clear status messages indicating global `.agents/` setup and `harness` CLI registration.
- **MIRROR**: Reuse `copy_tree_merge`, `print_banner`, and ANSI color formatting.
- **IMPORTS**: `subprocess`, `sys`, `Path` (already present).
- **GOTCHA**: Catch pip install errors gracefully with a helpful warning message if pip is unavailable or permissions are restricted.
- **MICRO_VALIDATE**: `python -m unittest tests/test_harness_init.py && python .agents/scripts/verify_shift_left.py --changed`

### Task 3: Update `install.ps1` with Interactive Scope Selection
- **ACTION**: Enhance `install.ps1` to accept `-Scope` parameter and present interactive prompt when omitted.
- **TEST_FIRST**: Test manually with PowerShell commands:
  - `powershell -File install.ps1 -Scope project -Target <testdir>`
  - `powershell -File install.ps1 -Scope global` (dry run / mock)
- **IMPLEMENT**:
  1. Update `param ([string]$Scope = "", [string]$Target = ".", [string]$Pack = "")`.
  2. If `$Scope` is empty and interactive session:
     - Print interactive choice menu:
       `[1] Project (Default) - Install .agents in current project or target directory`
       `[2] Global            - Install .agents in ~/.agents and register 'harness' CLI globally`
     - Prompt with `Read-Host`. Map `2` or `global` to `"global"`, otherwise `"project"`.
  3. If `$Scope` is empty and non-interactive: default to `"project"`.
  4. Build `$argsList`:
     - If `$Scope -eq "global"`: `@($harnessPy, "init", "--scope", "global")`
     - Else: `@($harnessPy, "init", $Target, "--scope", "project")`
     - Append `--pack $Pack` if specified.
  5. Invoke `python @argsList`.
- **MIRROR**: Follow existing `install.ps1` argument structure and PowerShell idioms.
- **GOTCHA**: Ensure non-interactive / automated calls (`-Scope project` or CI) do not hang on `Read-Host`.
- **MICRO_VALIDATE**: `powershell -File install.ps1 -Scope project -Target .tmp_test && Remove-Item -Recurse -Force .tmp_test`

### Task 4: Update `install.sh` with Interactive Scope Selection
- **ACTION**: Enhance `install.sh` to parse `--scope` / `-s` flag and present interactive prompt when omitted.
- **TEST_FIRST**: Test shell script syntax via `bash -n install.sh`.
- **IMPLEMENT**:
  1. Support `--scope [project|global]`, `-s [project|global]`, `--target [dir]`, `--pack [name]`, while maintaining backward-compatible positional args (`$1` target, `$2` pack).
  2. If `SCOPE` is empty:
     - Check `[ -t 0 ]` (interactive terminal).
     - If interactive, prompt:
       `1) Project (Default) - Install .agents in current project or target directory`
       `2) Global            - Install .agents in ~/.agents and register 'harness' CLI globally`
       Map choice `2` to `"global"`, else `"project"`.
     - If non-interactive, default to `"project"`.
  3. Build command:
     - If `SCOPE == "global"`: `python3 "$HARNESS_PY" init --scope global ...`
     - Else: `python3 "$HARNESS_PY" init "$TARGET" --scope project ...`
- **MIRROR**: Follow existing `install.sh` structure and portable POSIX/bash idioms.
- **GOTCHA**: Stdin check `[ -t 0 ]` prevents script hangs in piped curl/bash executions (`curl ... | bash`).
- **MICRO_VALIDATE**: `bash -n install.sh && python .agents/scripts/verify_shift_left.py --changed`

### Task 5: Documentation Updates in `README.md`
- **ACTION**: Update `README.md` to reflect scope options in both scripts and CLI.
- **IMPLEMENT**:
  - Add documentation for `-Scope global` in PowerShell and `--scope global` in Bash.
  - Document the interactive selection menu.
  - Document `harness init --scope global`.
- **MICRO_VALIDATE**: `python .agents/scripts/verify_shift_left.py --changed`

---

## Test-Driven Strategy

### Unit Tests
| Test | Input | Expected Output | Edge Case? |
|---|---|---|---|
| `test_scope_flag_default` | `harness.py init` | `args.scope == "project"` | No |
| `test_scope_flag_global` | `harness.py init --scope global` | `args.scope == "global"` | No |
| `test_scope_flag_invalid` | `harness.py init --scope invalid` | SystemExit (argparse error) | Yes |
| `test_init_project_scaffolding` | `cmd_init(args)` with scope="project" | `.agents/` created in target dir | No |
| `test_init_global_scaffolding` | `cmd_init(args)` with scope="global" | `~/.agents/` created in home dir, pip install called | Yes |

### Edge Cases Checklist
- [x] Non-interactive execution in PowerShell (e.g. piped or redirected stdin) defaults to project without hanging
- [x] Non-interactive execution in Bash (`[ ! -t 0 ]`) defaults to project without hanging
- [x] Passing `-Scope global` / `--scope global` directly bypasses interactive prompt
- [x] Invalid scope selection defaults safely to project or reports clear error
- [x] Failure in `pip install -e .` does not corrupt `.agents/` scaffolding

---

## Validation Commands

### Level 0: Shift-Left Pre-Flight Scanner (< 1s)
```bash
python .agents/scripts/verify_shift_left.py --changed
```

### Level 1: Static / Syntax Analysis
```bash
bash -n install.sh
```

### Level 2: Unit Tests
```bash
python -m unittest discover tests
```

---

## Acceptance Criteria
- [ ] `harness.py init` supports `--scope project` and `--scope global`.
- [ ] Global scope sets target to user home `~/.agents` and registers `harness` via `pip install -e .`.
- [ ] `install.ps1` supports `-Scope [project|global]` and presents an interactive menu when unspecified in interactive terminals.
- [ ] `install.sh` supports `--scope [project|global]` and presents an interactive menu when unspecified in interactive terminals.
- [ ] Non-interactive shell executions default smoothly to `project` scope without hanging.
- [ ] Unit tests pass cleanly with `python -m unittest`.
- [ ] Pre-flight shift-left checks pass with zero violations.

## Risks
| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| User runs installer via pipe (`curl ... \| bash`) and prompt blocks | Medium | High | Guard interactive prompts with `[ -t 0 ]` in bash and `[Console]::IsInputRedirected` in PowerShell |
| `pip` fails due to permissions or virtual environment constraints during global install | Low | Medium | Catch exceptions in `subprocess.run` and emit actionable guidance to user rather than crashing |

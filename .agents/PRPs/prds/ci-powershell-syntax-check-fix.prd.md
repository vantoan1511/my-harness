# Spec: Fix CI PowerShell Syntax Check Step

## 1. Intent & Problem Statement
- **User Intent**: GitHub CI fails at step "Verify PowerShell script syntax (Windows)" with `[ref] cannot be applied to a variable that does not exist.`
- **Problem**: In [.github/workflows/ci.yml](file:///d:/Projects/my-harness/.github/workflows/ci.yml) the step runs
  `[Parser]::ParseFile("install.ps1", [ref]$null, [ref]$errors)`.
  `$errors` was never assigned, and `[ref]` needs an existing variable. The step therefore fails on every Windows runner, before it checks anything. It is a CI script bug, not a bug in `install.ps1`.
- **Root cause evidence**: Reproduced locally. The original one-liner throws the same `NonExistingVariableReference`. Pre-declaring `$errors` and `$tokens` parses `install.ps1` with 0 errors.
- **Target Outcome**: The Windows CI step passes on a valid `install.ps1`. It fails with a readable message on a real parse error.

## 2. User Experience & Interactions
- **Placement**: `.github/workflows/ci.yml`, step `Verify PowerShell script syntax (Windows)`.
- **Interaction Flow**:
  1. Declare `$tokens = $null` and `$errors = $null`.
  2. Call `ParseFile("install.ps1", [ref]$tokens, [ref]$errors)`.
  3. If `$errors.Count -gt 0`, print each error's `Message` and line number, then `exit 1`.
- **Component Strategy**: None (CI only).

## 3. Contract-First Boundaries

### Step contract
```powershell
# Pre-condition: install.ps1 exists in the repo root (checkout done)
# Post-condition: exit 0 if there are no parse errors, exit 1 otherwise
$tokens = $null
$errors = $null
$null = [System.Management.Automation.Language.Parser]::ParseFile(
    (Join-Path $PWD "install.ps1"), [ref]$tokens, [ref]$errors)
if ($errors.Count -gt 0) {
    $errors | ForEach-Object { Write-Host "install.ps1:$($_.Extent.StartLineNumber): $($_.Message)" }
    exit 1
}
```
- `ParseFile` resolves relative paths against the .NET process directory, not the PowerShell location. Passing an absolute path via `$PWD` avoids that mismatch.
- `shell: powershell` (Windows PowerShell 5.1) stays as is. The API exists in both 5.1 and 7.

### State & Storage Invariants
- None. No stored state.

## 4. Scope Boundaries
- **In Scope (v1)**:
  - Fix the CI step.
  - Add a regression test that guards against an unassigned `[ref]` variable in `ci.yml`, and a test that actually parses `install.ps1` where PowerShell is available.
- **Out of Scope**:
  - Changes to `install.ps1`.
  - The matrix, other CI steps, and the unrelated `feat/git-post-merge-auto-update` work.

## 5. Acceptance Criteria
- [ ] AC-1: The Windows CI step passes on the current `install.ps1`.
- [ ] AC-2: A deliberately broken script (e.g. `if (`) makes the same snippet exit 1 and print the error line.
- [ ] AC-3: A unit test fails if `ci.yml` uses `[ref]$errors` without assigning `$errors` first.
- [ ] AC-4: `python -m unittest discover tests` and `verify_shift_left.py --changed` pass.

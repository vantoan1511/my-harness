# Implementation Report: Fix Command & Global Deduplication

## Summary
Implemented the `harness fix` command to repair project-scope `.agents/` installations (restoring missing standard directories, core scripts, and repairing configs/hooks) and automatically detect global installations (`~/.gemini/config/plugins/my-harness` and `~/.agents`). When global installation is detected, matching duplicate skills in `.agents/skills/` and matching template rules in `.agents/rules/` are pruned from the project scope to prevent conflicts in AI agent context windows, while preserving any custom project-specific skills and rules. Also updated `harness doctor` to detect and warn about duplicates, and updated `harness init` to prevent copying duplicates during fresh project initializations. Supported `fix` in `install.ps1` and `install.sh`.

## Assessment vs Reality

| Metric | Predicted (Plan) | Actual |
|---|---|---|
| Complexity | Medium | Medium |
| Confidence | High | High |
| Files Changed | 6 | 6 |

## Tasks Completed

| # | Task | Status | Notes |
|---|---|---|---|
| 1 | Global Installation Detection (`detect_global_installation()`) | [done] Complete | Detects plugin and `~/.agents`, enumerates skills and rules |
| 2 | Deduplication Logic with Custom Preservation (`deduplicate_project_scope()`) | [done] Complete | Prunes duplicate skills/rules, preserves custom items, supports dry-run |
| 3 | Project Structure & Script Repair Helpers | [done] Complete | Restores missing directories, core scripts, and repairs `harness.config.json` & `hooks.json` |
| 4 | CLI Parser Integration & `cmd_fix` Handler | [done] Complete | Registers `fix` parser with target and `--dry-run`, wires into `main()` |
| 5 | Doctor Warning for Global Duplicates | [done] Complete | Warns in `cmd_doctor()` if duplicate items are found and advises `harness fix` |
| 6 | Init Deduplication Prevention | [done] Complete | In `cmd_init()`, skips scaffolding duplicate skills/rules if global exists |
| 7 | Full Validation & Pre-Flight Checks | [done] Complete | All 19 tests pass, shift-left pre-flight verified |

## Validation Results

| Level | Status | Notes |
|---|---|---|
| Pre-Flight Scanner | [done] Pass | Zero architectural violations |
| Static Analysis | [done] Pass | Pattern checks clean |
| Unit Tests | [done] Pass | 19 tests passing (12 new tests added) |
| Build / Scripts | [done] Pass | `install.ps1` and `install.sh` updated |
| Integration / E2E | [done] Pass | E2E installation and fix tests passing |
| Edge Cases | [done] Pass | Dry-run, empty directory, custom preservation verified |

## Files Changed

| File | Action | Lines |
|---|---|---|
| `harness.py` | UPDATED | +180 / -2 |
| `tests/test_harness_fix.py` | CREATED | +265 |
| `tests/test_harness_init.py` | UPDATED | +30 |
| `install.ps1` | UPDATED | +18 / -2 |
| `install.sh` | UPDATED | +32 / -12 |
| `.agents/PRPs/prds/fix-command-deduplication.prd.md` | CREATED | +85 |
| `.agents/PRPs/plans/completed/fix-command-deduplication.plan.md` | ARCHIVED | +157 |

## Deviations from Plan
None. All components were implemented following the plan and contracts. Additionally enhanced `install.ps1` and `install.sh` to allow triggering `fix` directly.

## Issues Encountered
None.

## Tests Written

| Test File | Tests | Coverage |
|---|---|---|
| `tests/test_harness_fix.py` | 11 tests | Detection (none, plugin, agents dir), deduplication (matching removal, custom preservation, dry-run), repair (missing dirs, core scripts, config/hooks), CLI parser args, E2E cmd_fix execution, doctor duplicate warning |
| `tests/test_harness_init.py` | 1 new test | Project init skipping duplicates when global exists |

## Knowledge Base Updates (Self-Improving)
None.

## Next Steps
- [ ] Review PR
- [ ] Merge PR when approved

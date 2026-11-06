# Auto-Curated Gotchas & Operational Traps

> Synthesized automatically by `curate_knowledge.py` from Phase 4.5 Self-Review logs and PRP reports.

### [DEVIATION] Deviations in ci-powershell-syntax-check-fix-report.md
- **Insight**: None.

### [DEVIATION] Issues in ci-powershell-syntax-check-fix-report.md
- **Insight**: None.

### [DEVIATION] Deviations in ci-python-compatibility-report.md
- **Insight**: None.

### [DEVIATION] Issues in ci-python-compatibility-report.md
- **Insight**: None.

### [DEVIATION] Deviations in fix-command-deduplication-report.md
- **Insight**: None. All components were implemented following the plan and contracts. Additionally enhanced `install.ps1` and `install.sh` to allow triggering `fix` directly.

### [DEVIATION] Issues in fix-command-deduplication-report.md
- **Insight**: None.

### [DEVIATION] Deviations in implement-review-adapt-loop-report.md
- **Insight**: None.

### [DEVIATION] Issues in implement-review-adapt-loop-report.md
- **Insight**: None. All tests and shift-left gates passed cleanly on the first pass.

### [DEVIATION] Deviations in installer-scope-selection-report.md
- **Insight**: - Enhanced Python detection in `install.sh` to test execution (`python -c "import sys"`) so that Microsoft Store stub aliases on Windows environments are gracefully bypassed in favor of a functional Python interpreter.

### [DEVIATION] Issues in installer-scope-selection-report.md
- **Insight**: - None. All validations and tests passed cleanly.

### [DEVIATION] Deviations in plugin-auto-update-report.md
- **Insight**: - Preserved existing filesystem safety by ensuring `save_update_check_state` does not preemptively create empty plugin folders during `--check-only` runs when no plugin was previously installed.

### [DEVIATION] Issues in plugin-auto-update-report.md
- **Insight**: None.

### [DEVIATION] Deviations in specify-handoff-format-report.md
- **Insight**: None.

### [DEVIATION] Issues in specify-handoff-format-report.md
- **Insight**: None.


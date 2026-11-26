# Plan: [Feature Name]

## Summary
[2-3 sentence overview]

## User Story
As a [user], I want [capability], so that [benefit].

## Problem → Solution
[Current state] → [Desired state]

## Metadata
- **Complexity**: [Small | Medium | Large | XL]
- **GitHub Issue**: [#number or "N/A"]
- **Parent Epic**: [#epic-number or "N/A"]
- **Source PRD**: [path or "N/A"]
- **PRD Phase**: [phase name or "N/A"]
- **Branch Name**: [feat/<name> | fix/<name> | <current-branch>]
- **Auto-Create PR**: [true | false (local: true)]
- **Base Branch**: [main | <target-branch>]
- **Estimated Files**: [count]

---

## Mandatory Reading

| Priority | File | Lines | Why |
|---|---|---|---|
| P0 (critical) | `path/to/file` | 1-50 | Core pattern to follow |
| P1 (important) | `path/to/file` | 10-30 | Related types/contracts |

---

## Patterns to Mirror

Follow existing codebase patterns:

### NAMING_CONVENTION
// SOURCE: [file:lines]
[actual snippet]

### ERROR_HANDLING
// SOURCE: [file:lines]
[actual snippet]

### TEST_STRUCTURE
// SOURCE: [file:lines]
[actual snippet]

---

## Senior Design & Resilience Gate

- **Blast Radius & Callers**: [Existing callers, backward-compatibility constraints, and legacy code reused or deleted]
- **Chosen Trade-off**: [Selected approach vs. rejected alternative — favoring simplicity and reversibility]
- **PR Slicing**: [Single PR | Slice 1 (Prep) → Slice 2 (Core + Tests) → Slice 3 (Wiring)]

### Failure Modes & Rollback
| Failure Mode | Expected Behavior | Rollback / Mitigation |
|---|---|---|
| Timeout / Network Error | ... | ... |
| Duplicate Submit / Race | ... | ... |
| Partial Failure / Bad Deploy | ... | ... |

---

## Files to Change

| File | Action | Justification |
|---|---|---|
| `path/to/file` | CREATE | New module for feature |
| `path/to/existing` | UPDATE | Extend functionality |

## NOT Building
- [Out of scope item 1]
- [Out of scope item 2]

---

## Step-by-Step Tasks

### Task 1: [Name]
- **ACTION**: [What to do]
- **TEST_FIRST**: [Exact test file, test description, input, and expected assertion to write before implementing]
- **IMPLEMENT**: [Specific minimal code to make test pass]
- **MIRROR**: [Discovered pattern to follow]
- **IMPORTS**: [Required imports]
- **GOTCHA**: [Known pitfall to avoid]
- **MICRO_VALIDATE**: [Fast check command: e.g. `npm test`, `pytest`, `cargo test`, or `verify_shift_left.py --changed` from `.agents/scripts/` or `~/.gemini/config/plugins/my-harness/scripts/`]

### Task 2: [Name]
- **ACTION**: ...
- **TEST_FIRST**: ...
- **IMPLEMENT**: ...
- **MIRROR**: ...
- **IMPORTS**: ...
- **GOTCHA**: ...
- **MICRO_VALIDATE**: ...

---

## Test-Driven Strategy

All implementation MUST be preceded by writing failing tests.

### Unit Tests
| Test | Input | Expected Output | Edge Case? |
|---|---|---|---|
| ... | ... | ... | ... |

### Edge Cases Checklist
- [ ] Empty / nullish input
- [ ] Boundary limits
- [ ] Network failure or timeout
- [ ] Permission / authorization denied

---

## Validation Commands

### Level 0: Shift-Left Pre-Flight Scanner (< 1s)
```bash
python -c "import os, subprocess, sys; p = '.agents/scripts/verify_shift_left.py'; p = p if os.path.exists(p) else os.path.expanduser('~/.gemini/config/plugins/my-harness/scripts/verify_shift_left.py'); sys.exit(subprocess.call([sys.executable, p, '--changed']) if os.path.exists(p) else 0)"
```

### Level 1: Static Analysis
```bash
[configured type-check or lint command]
```

### Level 2: Unit Tests
```bash
[configured test command]
```

### Level 3: Build Verification
```bash
[configured build command]
```

---

## Acceptance Criteria
- [ ] All tasks completed
- [ ] All validation commands pass
- [ ] Tests written first and passing
- [ ] No type errors or lint warnings
- [ ] Zero shift-left architectural violations

## Risks
| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| ... | ... | ... | ... |

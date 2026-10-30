---
name: tdd-workflow
description: Enforces test-driven development (TDD) and shift-left quality across projects. Write tests before production code.
---

# Test-Driven Development (TDD) Workflow

This project follows a **Shift-Left Test-Driven Development** methodology. Tests are written **before** production code to clarify requirements, define interface contracts, catch edge cases upfront, and guarantee that new features and bug fixes never introduce regressions.

---

## Testing Workflow Overview

```
┌────────────────────────────────────────────────────────────────────────┐
│                          TDD INNER LOOP                                │
│                                                                        │
│   1. RED         2. RUN FAIL      3. GREEN      4. PRE-FLIGHT 5. REFACTOR
│  Write test   ►  Verify fail   ►  Write code ►  Fast check  ►  Clean up  │
│  first           assertion        to pass       & types pass    & re-test │
└────────────────────────────────────────────────────────────────────────┘
```

### Step 1: Write Test First (RED)
Write the test case before modifying or creating production files. Define:
- Happy path inputs and expected outputs.
- Boundary conditions (empty strings, `null`, `undefined`, zero, max limits).
- Error paths (network failure, timeout, invalid format, permission denied).

### Step 2: Verify Test Failure
Run the test runner to ensure the test fails for the expected reason:
```bash
python -c "import os, subprocess, sys; p = '.agents/scripts/verify_shift_left.py'; p = p if os.path.exists(p) else os.path.expanduser('~/.gemini/config/plugins/my-harness/scripts/verify_shift_left.py'); sys.exit(subprocess.call([sys.executable, p, '--test']) if os.path.exists(p) else 0)"
```
*If the test passes before writing code, the test is invalid or testing already-existing behavior!*

### Step 3: Implement Minimal Code (GREEN)
Write only the minimal code necessary to make the test pass. Avoid premature over-engineering.

### Step 4: Run Shift-Left Pre-Flight
Run the fast shift-left pre-flight tool immediately after editing:
```bash
python -c "import os, subprocess, sys; p = '.agents/scripts/verify_shift_left.py'; p = p if os.path.exists(p) else os.path.expanduser('~/.gemini/config/plugins/my-harness/scripts/verify_shift_left.py'); sys.exit(subprocess.call([sys.executable, p, '--changed']) if os.path.exists(p) else 0)"
```
Ensure zero type errors, zero lint warnings, and zero architectural violations.

### Step 5: Refactor & Confirm
Clean up code, eliminate duplication, improve naming, and verify that the test suite remains green.

---

## Testing Patterns by Stack

### 1. TypeScript / JavaScript (Node Native Runner)
```typescript
import { describe, it } from 'node:test'
import assert from 'node:assert/strict'
import { calculateDiscount } from '../pricing.js'

describe('calculateDiscount', () => {
  it('applies percentage discount correctly', () => {
    assert.strictEqual(calculateDiscount(100, 0.2), 80)
  })

  it('handles zero discount', () => {
    assert.strictEqual(calculateDiscount(100, 0), 100)
  })

  it('rejects negative prices', () => {
    assert.throws(() => calculateDiscount(-10, 0.1), /Invalid price/)
  })
})
```

### 2. Python (`pytest`)
```python
import pytest
from app.services import parse_config

def test_parse_valid_config():
    data = {"timeout": 30, "enabled": True}
    cfg = parse_config(data)
    assert cfg.timeout == 30
    assert cfg.enabled is True

def test_parse_missing_keys_raises_error():
    with pytest.raises(ValueError, match="Missing required key"):
        parse_config({})
```

### 3. Rust (`cargo test`)
```rust
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_format_label() {
        assert_eq!(format_label("app", "orbit"), "app=orbit");
    }

    #[test]
    fn test_empty_key_fails() {
        assert!(format_label("", "value").is_err());
    }
}
```

### 4. Go (`go test`)
```go
package service

import "testing"

func TestCalculateTotal(t *testing.T) {
    total := CalculateTotal([]int{10, 20, 30})
    if total != 60 {
        t.Fatalf("expected 60, got %d", total)
    }
}
```

---

## Definition of Done (TDD Gate)

Before declaring any feature, bug fix, or refactor complete:
1. **Tests Written First**: Unit test exists for each new function, class, or endpoint.
2. **All Tests Green**: Test runner passes with 0 failures.
3. **Pre-Flight Passes**: `python .agents/scripts/verify_shift_left.py --changed` reports 0 violations.
4. **Static Analysis Passes**: Type checker and linter report 0 errors.

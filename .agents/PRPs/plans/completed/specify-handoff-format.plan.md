# Implementation Plan: Standard Markdown Heading & Bullet Formatting for Specify Handoff

## 1. Overview & Source
- **Feature Name**: Standard Markdown Heading & Bullet Formatting for Specify Handoff
- **Source PRD**: [.agents/PRPs/prds/specify-handoff-format.prd.md](file:///d:/Projects/my-harness/.agents/PRPs/prds/specify-handoff-format.prd.md)
- **Target Components**:
  - `.agents/skills/specify/SKILL.md`: Update Phase 5 Handoff format to use Markdown headings, bullet lists, and double newlines.
  - `template/.agents/skills/specify/SKILL.md`: Keep in sync with `.agents/skills/specify/SKILL.md`.
  - `tests/test_specify_format.py`: Unit test verifying structure and sync invariants.
  - Global Antigravity Plugin deployment.

---

## 2. Interface & Boundary Contracts

### Handoff Template Specification
```markdown
## Specification & Implementation Plan Ready

- **Feature**: [Feature Name]
- **Spec**: [name].prd.md
- **Plan**: [name].plan.md
- **Test Strategy**: [Test runners and command, e.g., cargo test, npm test, pytest]

### Contracts Defined
- [Contract 1, e.g. API request/response schema or endpoint parameters]
- [Contract 2, e.g. State store action or storage model]

### Summary of Decisions
- **[Decision Area 1]**: [Explanation of decision]
- **[Decision Area 2]**: [Explanation of decision]

Next Step: Run /implement .agents/PRPs/plans/{name}.plan.md to begin test-driven implementation.
```

### Invariants & Guardrails
1. **No Collapsed Blocks**: Sections must be delineated by standard Markdown headings (`##`, `###`) and empty lines (`\n\n`).
2. **List Items**: Contracts and decision items must use standard markdown bullet markers (`- `).
3. **Template Parity**: `template/.agents/skills/specify/SKILL.md` must be byte-for-byte identical to `.agents/skills/specify/SKILL.md`.

---

## 3. Step-by-Step TDD Tasks

### Task 1: Add Unit Tests for Specify Handoff Format & Parity (RED)
- **ACTION**: Create `tests/test_specify_format.py` validating that both `.agents/skills/specify/SKILL.md` and `template/.agents/skills/specify/SKILL.md` define the markdown heading and bullet layout in Phase 5, and that the two files are completely identical.
- **TEST_FIRST**:
  - Test File: `tests/test_specify_format.py`
  - Test Names:
    - `test_specify_skills_are_identical`: Asserts `.agents/skills/specify/SKILL.md` content matches `template/.agents/skills/specify/SKILL.md`.
    - `test_specify_handoff_has_markdown_headers_and_bullets`: Asserts Phase 5 contains `## Specification & Implementation Plan Ready`, `### Contracts Defined`, `### Summary of Decisions`, and bullet markers for items.
    - `test_specify_handoff_has_next_step`: Asserts `Next Step: Run /implement` is preserved.
  - Input: Reading the skill files.
  - Assertions: Fails initially on missing markdown headers (`## Specification & Implementation Plan Ready`, `### Contracts Defined`, `### Summary of Decisions`).
- **IMPLEMENT**:
  - Write test case in `tests/test_specify_format.py`.
- **MICRO_VALIDATE**:
  - `python -m unittest tests/test_specify_format.py` (Must fail initially as RED).
  - `python .agents/scripts/verify_shift_left.py --changed`

### Task 2: Update Phase 5 in `.agents/skills/specify/SKILL.md` & `template/` (GREEN)
- **ACTION**: Update Phase 5 in `.agents/skills/specify/SKILL.md` and `template/.agents/skills/specify/SKILL.md` to use the markdown heading and bullet format with blank line separation and an explicit rendering rule.
- **TEST_FIRST**:
  - Test File: `tests/test_specify_format.py`
- **IMPLEMENT**:
  - Replace Phase 5 content in `.agents/skills/specify/SKILL.md`.
  - Copy/update `template/.agents/skills/specify/SKILL.md` to ensure exact parity.
- **MICRO_VALIDATE**:
  - `python -m unittest tests/test_specify_format.py` (Must PASS).
  - `python -m unittest discover tests`
  - `python .agents/scripts/verify_shift_left.py --changed`

### Task 3: Deploy Updated Skill to Global Antigravity Plugin & Verify
- **ACTION**: Deploy updated skill to `~/.gemini/config/plugins/my-harness` using `python harness.py update --force` or deployment command, and verify that the global plugin's `skills/specify/SKILL.md` reflects the changes.
- **TEST_FIRST**:
  - Check that global plugin directory has updated content.
- **IMPLEMENT**:
  - Execute deployment via `harness` CLI.
- **MICRO_VALIDATE**:
  - `python -m unittest discover tests`
  - `python .agents/scripts/verify_shift_left.py --changed`

---

## 4. Validation Commands

### Level 0: Shift-Left Pre-Flight Scanner (< 1s)
```bash
python .agents/scripts/verify_shift_left.py --changed
```

### Level 1: Static & Structural Analysis
```bash
git diff --check
```

### Level 2: Unit Tests
```bash
python -m unittest discover tests
```

---

## 5. Acceptance Criteria
- [ ] All tasks completed.
- [ ] Tests written first and passing.
- [ ] `tests/test_specify_format.py` passes.
- [ ] Full test suite (`python -m unittest discover tests`) passes.
- [ ] Zero shift-left architectural violations.

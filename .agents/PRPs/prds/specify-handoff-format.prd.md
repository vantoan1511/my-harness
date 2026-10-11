# Spec: Standard Markdown Heading & Bullet Formatting for Specify Handoff

## 1. Intent & Problem Statement
- **User Intent**: Fix the `/specify` Phase 5 handoff format which sometimes collapses all lines into a single run of text in chat renderers.
- **Problem**:
  In `.agents/skills/specify/SKILL.md` (and `template/.agents/skills/specify/SKILL.md`), the Phase 5 handoff template currently uses plain text lines without blank lines (`\n\n`), markdown headings, or bullet list markers. Because standard Markdown (and LLM generation adhering strictly to the template) treats single line breaks as soft breaks, markdown renderers collapse the entire block:
  `Specification & Implementation Plan Ready Feature: ... Spec: ... Plan: ... Contracts Defined: ... Summary of Decisions ...` into a single continuous wall of text.
- **Target Outcome**:
  1. Revise the `/specify` Phase 5 handoff template to use standard Markdown headers (`## Specification & Implementation Plan Ready`, `### Contracts Defined`, `### Summary of Decisions`), bullet lists (`- `) with bold labels, and explicit blank lines.
  2. Add an explicit rendering guardrail instruction to ensure agents preserve markdown line breaks and list structure.
  3. Keep `.agents/skills/specify/SKILL.md`, `template/.agents/skills/specify/SKILL.md`, and the installed global Antigravity plugin in sync.

---

## 2. User Experience & Interactions

### Output Format of `/specify` Phase 5 Handoff
When an agent concludes `/specify`, it must output clean, structured Markdown that renders identically across all chat interfaces and markdown viewers:

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

### Contrast Matrix
- **Previous Unsafe Template**: Plain single lines with zero blank lines -> soft line breaks collapsed all text into one paragraph.
- **New Robust Template**: Headings + bullet lists + double newlines -> structurally immune to Markdown soft-line collapse.

---

## 3. Contract-First Boundaries

### Template Invariant (`SKILL.md` Phase 5 Contract)
The template defined in Phase 5 of both `.agents/skills/specify/SKILL.md` and `template/.agents/skills/specify/SKILL.md` must strictly define:
1. `## Specification & Implementation Plan Ready` as a level-2 markdown header.
2. Metadata fields formatted as a bullet list (`- **Feature**:`, `- **Spec**:`, `- **Plan**:`, `- **Test Strategy**:`) separated by a blank line before the next section.
3. `### Contracts Defined` as a level-3 header with bullet points for individual contracts.
4. `### Summary of Decisions` as a level-3 header with bullet points (`- **[Area]**: [Details]`) for each decision area.
5. Standalone paragraph for `Next Step: Run /implement .agents/PRPs/plans/{name}.plan.md to begin test-driven implementation.`.
6. Explicit instruction requiring blank lines between sections and bullet items.

### Synchronization Contract
- `template/.agents/skills/specify/SKILL.md` and `.agents/skills/specify/SKILL.md` must be byte-for-byte identical.
- Global plugin deployment (`~/.gemini/config/plugins/my-harness/skills/specify/SKILL.md`) must receive the updated skill file.

---

## 4. Scope Boundaries
- **In Scope (v1)**:
  - Update `.agents/skills/specify/SKILL.md`.
  - Update `template/.agents/skills/specify/SKILL.md`.
  - Unit test ensuring template validity, synchronicity, and markdown structure compliance.
  - Deploy updated skill to global Antigravity plugin via `harness update --force` or deployment helper.
- **Out of Scope**:
  - Changing the `/prp-plan` handoff format (which already uses markdown headings and bullet lists).
  - Altering the core 5-phase structure of `specify`.

---

## 5. Acceptance Criteria
- [ ] AC-1: `.agents/skills/specify/SKILL.md` contains the updated Phase 5 template with markdown headings, bullet lists, and double newline separation.
- [ ] AC-2: `template/.agents/skills/specify/SKILL.md` is strictly identical to `.agents/skills/specify/SKILL.md`.
- [ ] AC-3: Unit test in `tests/test_specify_format.py` asserts required headers, bullet structure, and synchronization between files.
- [ ] AC-4: Global Antigravity plugin receives the updated specify skill.
- [ ] AC-5: Zero architectural violations (`python .agents/scripts/verify_shift_left.py --changed` passes).

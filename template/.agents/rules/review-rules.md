# Primary Question

Does this improve the codebase?

Not:

Does this compile?

---

# Architecture Review

Check:

- Architecture consistency
- Dependency direction
- Layer boundaries
- Encapsulation
- Separation of concerns

---

# Reuse Review

Ask:

Could existing code have been reused?

Could an existing component have been extended?

Was a duplicate introduced?

---

# Design Review

Evaluate:

- DRY
- SOLID
- KISS
- YAGNI

Look for unnecessary abstractions.

Look for unnecessary APIs.

Look for unnecessary files.

---

# Maintainability Review

Does this increase future maintenance?

Does it introduce hidden complexity?

Does it create another way of doing the same thing?

---

# Consistency Review

Verify:

- Naming
- Folder organization
- UI patterns (if applicable)
- State management
- Error handling
- Logging
- Testing

Everything should feel native to the repository.

---

# Smell Detection

Flag:

- Duplicate business logic
- Duplicate UI / styling
- Duplicate utilities
- Large methods (>50 lines)
- Deep nesting (>4 levels)
- Feature envy
- God objects
- Tight coupling
- Magic constants
- Inconsistent naming
- Temporary solutions
- Parallel implementations

---

# Final Questions

Reviewers should ask:

"Why is this different?"

not automatically:

"This is different, therefore it is wrong."

Would I approve this PR?

Would I merge it without modifications?

Would I proudly maintain this code for five years?

If any answer is "No",

explain why and propose improvements.

---

# Approval Criteria

Approve only if:

- Code quality is high.
- Complexity is minimized.
- Maintenance cost is low.
- The implementation feels native to the project.
- Consistency is evidence.
- Correctness and appropriate architecture are the goal.

# When a PR introduces an abstraction or pattern:

- Is there a concrete problem it solves?
- Does it reduce coupling?
- Does it isolate variation?
- Does it establish a meaningful boundary?
- Does it improve testability?
- Is the additional complexity justified?

Do not reject an abstraction solely because the repository has not used it before.
Do not approve an abstraction solely because it is a recognized design pattern.

---

# Anti-Slop Craft Rules (Always-On)

Avoid typical AI-generated code slop during authoring and self-review:

- **No additive band-aids**: Fix root structure instead of stacking special-case flags or patch branches.
- **No speculative abstractions**: Do not introduce single-use helpers, wrappers, or interfaces without ≥2 concrete callers or a real boundary.
- **No defensive bloat inside trust boundaries**: Validate at external edges; trust type contracts internally instead of adding redundant null checks or silent fallbacks.
- **No error swallowing**: Fail fast with context instead of catching errors to return dummy defaults.
- **No narrator comments**: Never comment what the code already says; document only non-obvious *why* or invariants.
- **Match repo exemplars**: Mirror existing native conventions, naming, and error idioms.
- **Mandatory Auto-Trigger**:
  - **When coding / refactoring** non-trivial changes (new logic, bug fixes, or edits spanning ≥ 2 files): you MUST load and follow the `anti-slop` skill (exemplar lock, invariant lock, and bounded Self-Audit & Auto-Fix loop on `git diff`) before reporting completion.
  - **When reviewing code** (local diff or PR): you MUST audit against the `anti-slop` 8-Point Slop Audit Rubric in addition to security and architecture checks.

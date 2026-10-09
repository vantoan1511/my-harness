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

---
name: learn
description: Persist reusable behaviors, corrections, constraints, or successful patterns from recent interactions into workspace or global rules and skills.
---

# Learn Skill

Persist reusable behaviors, user corrections, constraints, and successful patterns from recent conversations into permanent institutional memory (Rules, Skills, or Scripts).

---

## Core Philosophy

> **Turn corrections into permanent guardrails.**
>
> When a user corrects the agent, establishes a design constraint, or fixes a tricky workflow, that insight must not be lost when the conversation ends. It should be distilled into an unambiguous Rule or Skill with a clear proposal workflow.

---

## Workflow Overview

```
┌────────────────────────────────────────────────────────────────────────┐
│                         LEARN WORKFLOW                                 │
│                                                                        │
│  [Analyze] ──► [Determine Root Cause] ──► [Classify] ──► [Propose]     │
│      │                  │                     │             │          │
│  Extract user       Universal vs           Rule vs     Mandatory       │
│  corrections &      Project-specific       Skill       Proposal Gate   │
│  key fixes          underlying need                    (learning_      │
│                                                         proposal.md)   │
│                                                             │          │
│                                                  [User Approves]       │
│                                                             │          │
│                                                  [Apply & Verify]      │
└────────────────────────────────────────────────────────────────────────┘
```

---

## Phase 1: Identify What to Learn

1. **Analyze Recent Messages**:
   - Prioritize analyzing recent user messages for explicit corrections, constraints, overrides, or negative feedback (e.g., *"no"*, *"instead"*, *"that failed"*, *"our principle is tone shift, avoid borders"*, *"never branch automatically"*).
   - Inspect tool call outputs and errors to pinpoint what went wrong during the task.

2. **Isolate the Pivotal Fix**:
   - Compare the failed attempts or initial assumptions with the final successful resolution.
   - Identify the exact principle, pattern, or constraint that produced the correct outcome.

3. **Determine Root Cause & Scope**:
   - Address the root architectural or behavioral cause, not transient surface symptoms.
   - Determine whether this is **Universal** (applies across all projects/global harness) or **Domain/Project-Specific** (belongs only in this repository).

4. **Exit Early if No Learning Needed**:
   - If the interaction was routine and did not reveal any new reusable behaviors, constraints, or edge cases, explain this clearly to the user and exit without proposing unnecessary changes.

---

## Phase 2: Classify Target Customization

| Type | Best For | Typical Target Locations |
| :--- | :--- | :--- |
| **Rule** | Universal constraints, coding standards, design-system invariants, Git rules, behavioral guardrails. | Workspace: `AGENTS.md`, `GEMINI.md`, `.agents/rules/*.md`<br>Global: `~/.gemini/config/plugins/<plugin>/rules/` |
| **Skill** | Multi-step actionable procedures, tool sequences, runbooks, parameter combinations, cheatsheets. | Workspace: `.agents/skills/<name>/SKILL.md`<br>Global: `~/.gemini/config/plugins/<plugin>/skills/<name>/SKILL.md` |
| **Script** | Deterministic automation, verification scripts, recurring CLI helpers. | `.agents/scripts/` |

---

## Phase 3: Create vs. Update (Preference Matrix)

- **Update Existing (Strong Preference)**:
  - If an active Rule or Skill covers this domain but failed, was outdated, missed edge cases, or diverged from reality, update that existing file.
  - Keeps rules consolidated and prevents fragmentation.
- **Create New**:
  - Only create a new Rule or Skill when the behavior introduces an entirely new domain, lifecycle stage, or guardrail that has no natural home in existing files.

---

## Phase 4: Mandatory Proposal Workflow (Strict Gate)

> [!CAUTION]
> **NEVER modify configuration, rule, or skill files immediately.**
> Always present a learning proposal artifact and wait for explicit user approval before touching files.

1. **Inspect Target Conventions**:
   - Review existing rules/skills or refer to `agy-customizations` to follow exact naming conventions, YAML frontmatter schemas, and markdown styles.
2. **Create the Proposal Artifact**:
   - Path: `<Artifact Directory>/learning_proposal.md`
   - Metadata: `RequestFeedback: true`, `UserFacing: true`
   - Outline:
     - **Context & Motivation**: What happened? Quote the user's correction or the problem encountered.
     - **Root Cause & Scope**: Why did it happen? Is it workspace-specific or global?
     - **Classification & Target**: State Rule vs. Skill, and provide the exact file path.
     - **Proposed Changes**: Provide the full text or clean diff format showing additions/modifications.
3. **Await User Approval**:
   - Stop execution and invite the user to review the proposal artifact and click **Proceed** or reply with approval.

---

## Phase 5: Apply & Verify

Once approved by the user:
1. Apply the edits cleanly using file editing tools.
2. Verify YAML frontmatter, headers, links, and formatting.
3. If scripts or tests are involved, run validation checks to ensure zero errors.
4. Report completion concisely with links to the updated files.

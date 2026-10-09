# AGENTS.md

# Project

my-harness

Tech stack:
- Python

---

# Agent Workflow

Agents must follow this workflow for every task.

## Phase 1 — Understand

Before modifying code:
1. Inspect the relevant existing implementation and neighboring components for established patterns.
2. Search for reusable modules, functions, services, utilities, and types.
3. Identify the smallest set of files that should change.

Do not begin implementation before completing this phase.

## Phase 2 — Plan

For non-trivial tasks:
1. Use `/specify` or `/prp-plan` to create or update the plan under `.agents/PRPs/plans/`.
2. Record:
   - problem
   - current implementation
   - proposed solution
   - files to modify / create
   - reusable existing code
   - risks & mitigations
   - verification steps
3. **Plan Handoff**: The planning turn must conclude strictly with the standard handoff block pointing to the plan file (`Next Step: Run /implement ...`). Never begin writing implementation or feature code during the planning phase.

## Phase 3 — Implement

Execute plans via `/implement <plan-path>` for a seamless implementation-to-PR workflow:
- Write failing tests first (RED).
- Implement minimal code to pass (GREEN).
- Run micro-validation after EVERY file edit:
  ```bash
  python .agents/scripts/verify_shift_left.py --changed
  ```
- Do not refactor unrelated code.
- Do not add speculative features or abstractions for hypothetical future requirements.
- Upon successful validation, `/implement` automatically writes the implementation report, archives the plan, commits changes, and opens a GitHub pull request.

## Phase 4 — Verify

After implementation:
1. Run pre-flight static checks:
   ```bash
   python .agents/scripts/verify_shift_left.py --changed
   ```
2. Run full validation checks (type check, lint, tests):
   ```bash
   python .agents/scripts/verify_shift_left.py --all-checks
   ```
3. Inspect `git diff` and `git status`. Verify no unrelated files were touched.

## Phase 5 — Report

The final response must contain:
- What changed
- Files changed
- Verification performed
- Remaining issues or limitations

---

# Git Workflow

1. Do not work directly on `main` or `master`.
2. Verify the current branch: `git branch --show-current`.
3. Create or checkout a dedicated branch before making changes: `git checkout -b feat/<name>` or `fix/<name>`.
4. Keep changes focused and atomic.

---

# Natural Human Writing & Social Conversation

## Natural Human Writing

Use the `natural-human-writing` / `fb-comment-style` skill as a general natural-writing harness whenever the goal is for agent output to feel human, conversational, and naturally written rather than polished or AI-generated.

It can be applied across contexts such as:
- chat and everyday conversation
- social-media comments
- debate, rebuttal, or argumentative replies
- emails and messages
- documentation and notes
- explanations and technical writing
- drafts intended to sound like the user's own writing

The style should adapt to the context. Do not force slang or deliberate typos into formal documents when they would be inappropriate. The core goal is natural human writing.

### Priority
Preserve factual correctness, intent, context, and required professionalism first.
Then apply the natural-writing constraints from the skill.

## Social Conversation

For casual social messaging, flirting, dating, teasing, banter, or interpersonal chat, also use `.agents/skills/social-conversation/SKILL.md`.

Use `natural-human-writing` for the writing surface and `social-conversation` for conversational behavior/calibration.

Do not let social-conversation rules leak into unrelated formal or technical writing.


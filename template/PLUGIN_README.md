# Agent Engineering DevKit (`my-harness`)

Reusable engineering harness and autonomous SDLC workflows for AI pair-programmers.

---

## Overview

**Agent Engineering DevKit** equips your AI coding agents with shift-left engineering discipline, contract-first design, test-driven development (TDD), and continuous verification.

Whether working in TypeScript, Python, Rust, or Go, this plugin turns general AI chat into an autonomous senior pair programmer that tests before coding, prevents architectural drift, and verifies changes at every step.

---

## Core Capabilities & Workflows

### 1. Contract-First Specification (`/specify`)
- Supports both raw feature intent and GitHub Issues (`/specify #42`), evaluating the **"Clear?" Gate** via `gh_project.py check-ready` before asking questions.
- Autonomous reconnaissance of existing patterns and types before questioning, plus syncing clarified Acceptance Criteria back to GitHub Issues (`gh issue edit`).
- Generates precise, contract-first design specifications and implementation plans under `.agents/PRPs/plans/`.

### 2. Comprehensive Feature Planning (`/prp-plan`)
- Ingests `.prd.md`, free-form features, or `#<issue>` tickets with Parent Epic context.
- Explores codebase architecture, component hierarchies, and established conventions.
- Formulates atomic TDD task checklists, verification gates, and risk mitigations.

### 3. Continuous Shift-Left Implementation (`/implement`)
- Reads the plan, moves linked GitHub Project issues to `In Progress`, and executes changes step-by-step.
- Enforces test-first (RED) and minimal implementation (GREEN).
- Runs micro-validation after every single file edit (`python .agents/scripts/verify_shift_left.py --changed`).
- Runs autonomous Critic Subagent review and adapts high/medium findings via bounded TDD micro-loops.
- Automatically produces implementation reports, commits changes, opens a PR (`Closes #N`), and handles PR merge, issue closure (`Done`), and follow-up known-issue creation.

### 4. Test-Driven Development Gate (`/tdd-workflow`)
- Strict Red-Green-Refactor loop.
- Prohibits writing production code before reproducing failures in automated tests.

### 5. Shift-Left Code Review (`/code-review`)
- Evaluates uncommitted changes or GitHub pull requests against the shift-left quality constitution.
- Flags layer violations, duplicate logic, leaky abstractions, and missing tests.

### 6. Git, GitHub Projects & Delivery Workflows
- **`/github-project-setup`**: Creates and links a GitHub Project (v2) with 2-week sprints, Roadmap dates, Priority, Board/Table/Roadmap views, and caches metadata via `gh_project.py sync`.
- **`/github-backlog-management`**: Refines issues with codebase reconnaissance, audits sprint carryover & dependencies, assigns sprints + Roadmap dates (`gh_project.py assign-sprint`), rolls up Epic dates (`gh_project.py rollup-epic`), and updates statuses (`gh_project.py set-status`).
- **`/commit`**: Conventional commits with smart file staging.
- **`/pr`**: Automated pull request generation, merge & issue closure (`Done`), and follow-up ticket triage.
- **`/pr-changelog`**: PR and release notes summarizer based on git diffs.

---

## Suggested Starter Prompts

- `/specify design contract and implementation plan for a new feature`
- `/tdd-workflow implement failing tests first then pass them`
- `/code-review inspect uncommitted changes against quality constitution`

---

## Quality Constitution & Rules

When this plugin is active, agents strictly abide by:
- **Branch Protection**: Never commit directly to `main` or `master`.
- **Shift-Left Prevention**: Catch defects, type issues, and style violations at edit time rather than review time.
- **Natural Human Writing**: Ensure all technical explanations and PR notes sound authentic, natural, and free of generic AI boilerplate.

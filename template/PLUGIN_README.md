# Agent Engineering DevKit (`my-harness`)

Reusable engineering harness and autonomous SDLC workflows for AI pair-programmers.

---

## Overview

**Agent Engineering DevKit** equips your AI coding agents with shift-left engineering discipline, contract-first design, test-driven development (TDD), and continuous verification.

Whether working in TypeScript, Python, Rust, or Go, this plugin turns general AI chat into an autonomous senior pair programmer that tests before coding, prevents architectural drift, and verifies changes at every step.

---

## Core Capabilities & Workflows

### 1. Contract-First Specification (`/specify`)
- Autonomous reconnaissance of existing patterns and types before questioning.
- Interactive ambiguity resolution via `ask_question`.
- Generates precise, contract-first design specifications and implementation plans under `.agents/PRPs/plans/`.

### 2. Comprehensive Feature Planning (`/prp-plan`)
- Explores codebase architecture, component hierarchies, and established conventions.
- Formulates atomic TDD task checklists, verification gates, and risk mitigations.

### 3. Continuous Shift-Left Implementation (`/implement`)
- Reads the plan and executes changes step-by-step.
- Enforces test-first (RED) and minimal implementation (GREEN).
- Runs micro-validation after every single file edit (`python .agents/scripts/verify_shift_left.py --changed`).
- Automatically produces implementation reports and stages changes.

### 4. Test-Driven Development Gate (`/tdd-workflow`)
- Strict Red-Green-Refactor loop.
- Prohibits writing production code before reproducing failures in automated tests.

### 5. Shift-Left Code Review (`/code-review`)
- Evaluates uncommitted changes or GitHub pull requests against the shift-left quality constitution.
- Flags layer violations, duplicate logic, leaky abstractions, and missing tests.

### 6. Git & Delivery Workflows
- **`/commit`**: Conventional commits with smart file staging.
- **`/pr`**: Automated pull request generation with rich markdown descriptions.
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

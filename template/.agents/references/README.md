# Project Knowledge Base & Reference Catalog

This directory contains on-demand architectural decisions (ADRs), canonical implementation recipes, and domain gotchas for this project.

> **Progressive Disclosure Principle**:
> Do not read all files at once. Read this index first, then inspect only the specific document relevant to your task.

---

## Catalog Index

### 1. Architecture Decision Records (`architecture/`)
Deep rationale explaining **why** the system is built this way.
- Document architectural choices, storage models, and design trade-offs here.

### 2. Canonical Recipes & Starter Templates (`recipes/`)
The authoritative "Gold Standard" patterns to mirror when adding new code.
- [canonical-node-test.md](file://recipes/canonical-node-test.md) — Node native test runner (`node:test`, `node:assert/strict`) starter templates.

### 3. Hard-Earned Gotchas & Troubleshooting (`gotchas/`)
Domain traps and non-obvious syntax quirks discovered during development.
- Document framework quirks, edge-case bugs, and environment gotchas here.

---

## How This Knowledge Base is Maintained
1. **Self-Improving via `/implement`**: When an unexpected deviation or gotcha is solved during implementation, record it into `gotchas/`.
2. **Curated from User Corrections**: Synthesize user corrections in `.agents/logs/` using `curate_knowledge.py`.
3. **Repository Evidence Over Doc Text**: If a doc and the source code disagree, the source code and tests are authoritative. Docs capture invariants and rationale.

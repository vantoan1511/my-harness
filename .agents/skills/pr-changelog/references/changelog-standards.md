# PR Changelog Standards & Best Practices

A pull request changelog translates technical code modifications into meaningful, readable changes for reviewers, maintainers, and users.

---

## Core Principles

### 1. User & Consumer Impact Over Code Mechanics
- **Bad**: "Changed boolean flag `is_isolated` in `watchers.rs` and added parameter to IPC handler."
- **Good**: "Isolate Kubernetes resources by cluster during context switches to prevent stale resources from leaking into Search Everywhere."

### 2. Highlight Breaking Changes Early
Breaking changes must always be placed at the top of the changelog with clear migration instructions:
- What broke?
- Why was the breaking change necessary?
- How should consumers/callers update their code or configuration?

### 3. Categorize by Intent
Group changes by semantic intent rather than file locations:
- 🚀 **Features**: New user-facing capabilities or APIs.
- 🐛 **Bug Fixes**: Resolved issues, prevented crashes, fixed regressions.
- ⚡ **Performance**: Latency reductions, caching, memory optimizations.
- 🔄 **Refactoring & Architecture**: Internal restructuring with no functional change.
- 🛠️ **Maintenance & Dependencies**: Dependency bumps, tool updates, build configurations.
- 📖 **Documentation**: README, architecture docs, guides.
- 🧪 **Tests & Verification**: New test suites, regression tests.

### 4. Traceability
Always link:
- Commit hashes (`abc1234`)
- Issue numbers (`#42` or `Fixes #42`)
- Pull request numbers

---

## Conventional Commits Mapping

| Conventional Commit Prefix | Changelog Section | User-Facing? |
|---|---|---|
| `feat:` / `feat(scope):` | 🚀 Features | Yes |
| `fix:` / `fix(scope):` | 🐛 Bug Fixes | Yes |
| `perf:` / `perf(scope):` | ⚡ Performance | Often |
| `refactor:` / `refactor(scope):` | 🔄 Refactoring & Architecture | Internal |
| `docs:` / `docs(scope):` | 📖 Documentation | Documentation |
| `test:` / `test(scope):` | 🧪 Tests & Verification | Internal |
| `chore:` / `build:` / `ci:` | 🛠️ Maintenance & Dependencies | Internal |
| `feat!:` / `fix!:` / `BREAKING CHANGE:` | ⚠️ Breaking Changes | **Critical** |

---

## Keep a Changelog Format

When exporting for release notes or `CHANGELOG.md`, follow the [Keep a Changelog](https://keepachangelog.com/) standard:

- **Added**: for new features.
- **Changed**: for changes in existing functionality.
- **Deprecated**: for soon-to-be removed features.
- **Removed**: for now removed features.
- **Fixed**: for any bug fixes.
- **Security**: in case of vulnerabilities.

---

## Concise & Focused Guidelines

1. **High Signal-to-Noise Ratio**:
   - Filter out low-value commits (formatting, chore bumps, typo fixes).
   - Consolidate multiple commits for the same feature/fix into one clear entry.
2. **Omit Empty Categories**:
   - Only render headers for categories that contain actual entries.
3. **Inserting into `CHANGELOG.md`**:
   - Always target the latest entry:
     - If `## [Unreleased]` exists, inject under it.
     - Otherwise, inject under the topmost version header (e.g. `## [1.2.0]`).
     - Never overwrite past release history.

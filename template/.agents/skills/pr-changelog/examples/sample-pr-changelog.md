# Example PR Changelog

## 1. Concise Format (PR or Chat)

### 🐛 Bug Fixes
- **search**: prevent stale cluster resource events from polluting Search Everywhere modal (`8c47818`)
- **watchers**: cancel active watcher streams immediately upon cluster disconnect (`a3b109e`)

### 🔄 Improvements & Architecture
- **ipc**: include `cluster_id` in `ResourceBatchUpdated` broadcast payload to ensure client-side receiver filtering (`8c47818`)

---

## 2. Injected into Latest Entry of `CHANGELOG.md`

```markdown
# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### 🐛 Bug Fixes
- **search**: prevent stale cluster resource events from polluting Search Everywhere modal (`8c47818`)
- **watchers**: cancel active watcher streams immediately upon cluster disconnect (`a3b109e`)

### 🔄 Improvements & Architecture
- **ipc**: include `cluster_id` in `ResourceBatchUpdated` broadcast payload to ensure client-side receiver filtering (`8c47818`)

## [1.2.0] - 2026-09-15
### Added
- Multi-cluster context switcher
```

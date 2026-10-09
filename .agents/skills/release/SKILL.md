---
name: release
description: Release management — version bump, changelog update, lockfile sync, and release PR creation
---

# Release Workflow

When the user requests a new version release:

## Step 1: Identify Target Version
1. Check current version across project config files (`package.json`, `Cargo.toml`, `pyproject.toml`, etc.).
2. Validate semantic versioning (`MAJOR.MINOR.PATCH`).

## Step 2: Bump Version Numbers
Update version strings in project manifest files.

## Step 3: Update Lockfiles
Run package manager commands to synchronize lockfiles (e.g. `npm install`, `cargo check`, `poetry lock`, etc.).

## Step 4: Branch, Commit, and PR
1. Create release branch `release/v<VERSION>`.
2. Commit with conventional prefix `chore: release v<VERSION>`.
3. Push to remote and open a Pull Request.

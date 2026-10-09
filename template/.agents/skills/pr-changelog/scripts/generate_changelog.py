#!/usr/bin/env python3
"""
generate_changelog.py — PR Changelog Generator

Inspects Git commits, diffs, and GitHub PR metadata to generate
structured, categorized changelogs (PR description, Keep a Changelog, Compact, JSON).
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, List, Optional, Tuple

# Ensure UTF-8 output on Windows consoles
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
if sys.stderr.encoding and sys.stderr.encoding.lower() != "utf-8":
    try:
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


@dataclass
class CommitInfo:
    hash: str
    commit_type: str
    scope: Optional[str] = None
    subject: str = ""
    body: str = ""
    is_breaking: bool = False
    breaking_description: str = ""
    issue_refs: List[str] = field(default_factory=list)


@dataclass
class ChangelogReport:
    base_ref: str
    head_ref: str
    commits: List[CommitInfo] = field(default_factory=list)
    changed_files: List[Tuple[str, str]] = field(default_factory=list)  # (status, path)
    additions: int = 0
    deletions: int = 0
    pr_number: Optional[int] = None
    pr_title: Optional[str] = None
    pr_url: Optional[str] = None


CONVENTIONAL_COMMIT_REGEX = re.compile(
    r"^([a-zA-Z]+)(?:\(([^)]+)\))?(!)?:\s*(.+)$"
)
BREAKING_CHANGE_REGEX = re.compile(
    r"BREAKING[ -]CHANGE:\s*(.+)", re.IGNORECASE
)
ISSUE_REF_REGEX = re.compile(
    r"(?:(?:fix(?:es)?|close[sd]?|resolve[sd]?)\s+)?(#\d+|gh-\d+)", re.IGNORECASE
)


def run_cmd(cmd: List[str], cwd: Optional[str] = None) -> Tuple[int, str, str]:
    """Execute a system command and return (exit_code, stdout, stderr)."""
    try:
        proc = subprocess.run(
            cmd,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        return proc.returncode, proc.stdout.strip(), proc.stderr.strip()
    except Exception as e:
        return 1, "", str(e)


def parse_commit_message(commit_hash: str, raw_message: str) -> CommitInfo:
    """Parse a git commit message into structured CommitInfo."""
    lines = raw_message.strip().splitlines()
    first_line = lines[0].strip() if lines else ""
    body = "\n".join(lines[1:]).strip() if len(lines) > 1 else ""

    commit_type = "other"
    scope = None
    subject = first_line
    is_breaking = False
    breaking_desc = ""

    match = CONVENTIONAL_COMMIT_REGEX.match(first_line)
    if match:
        raw_type, raw_scope, bang, raw_subject = match.groups()
        commit_type = raw_type.lower()
        scope = raw_scope.strip() if raw_scope else None
        subject = raw_subject.strip()
        if bang == "!":
            is_breaking = True
    else:
        # Heuristic fallback for non-conventional commit messages
        lower_line = first_line.lower()
        if lower_line.startswith(("feat", "add", "implement", "support", "new")):
            commit_type = "feat"
        elif lower_line.startswith(("fix", "resolve", "patch", "prevent", "bug")):
            commit_type = "fix"
        elif lower_line.startswith(("perf", "speed", "optimize")):
            commit_type = "perf"
        elif lower_line.startswith(("refactor", "restructure", "clean")):
            commit_type = "refactor"
        elif lower_line.startswith(("doc", "docs")):
            commit_type = "docs"
        elif lower_line.startswith(("test", "tests")):
            commit_type = "test"
        elif lower_line.startswith(("chore", "deps", "bump", "ci", "build")):
            commit_type = "chore"

    # Check for breaking change annotations in body
    breaking_match = BREAKING_CHANGE_REGEX.search(raw_message)
    if breaking_match:
        is_breaking = True
        breaking_desc = breaking_match.group(1).strip()
    elif is_breaking and not breaking_desc:
        breaking_desc = subject

    # Extract issue references (#123, gh-456)
    issue_refs = []
    for match_ref in ISSUE_REF_REGEX.finditer(raw_message):
        ref = match_ref.group(1)
        if ref and ref not in issue_refs:
            issue_refs.append(ref)

    return CommitInfo(
        hash=commit_hash[:7],
        commit_type=commit_type,
        scope=scope,
        subject=subject,
        body=body,
        is_breaking=is_breaking,
        breaking_description=breaking_desc,
        issue_refs=issue_refs,
    )


def categorize_commit(info: CommitInfo) -> str:
    """Map commit type to user-facing changelog category."""
    mapping = {
        "feat": "Features",
        "fix": "Bug Fixes",
        "perf": "Performance",
        "refactor": "Refactoring & Architecture",
        "docs": "Documentation",
        "test": "Tests & Verification",
        "chore": "Maintenance & Dependencies",
        "build": "Maintenance & Dependencies",
        "ci": "Maintenance & Dependencies",
        "style": "Maintenance & Dependencies",
    }
    return mapping.get(info.commit_type, "Other Changes")


def detect_affected_areas(file_paths: List[str]) -> List[str]:
    """Identify functional areas impacted by the set of changed files."""
    areas = set()
    for path in file_paths:
        norm = path.replace("\\", "/")
        if norm.startswith(("src/", "frontend/", "ui/")) or norm.endswith((".vue", ".css")):
            areas.add("Frontend (Vue / TypeScript / UI)")
        elif norm.startswith(("core/", "backend/", "src-tauri/", "crates/")) or norm.endswith((".rs", "Cargo.toml")):
            areas.add("Backend (Rust / Engine / IPC)")
        elif norm.startswith((".github/", "scripts/", ".agents/scripts/")):
            areas.add("CI & Workflows")
        elif norm.startswith(("docs/", ".agents/PRPs/")) or norm.endswith((".md", ".txt")):
            areas.add("Documentation")
        elif "test" in norm or norm.endswith((".test.ts", ".spec.ts")):
            areas.add("Tests & Verification")
        elif norm.endswith((".json", ".toml", ".yaml", ".yml")):
            areas.add("Tooling & Configuration")
    return sorted(areas)


def format_pr_changelog(report: ChangelogReport) -> str:
    """Generate Markdown formatted for GitHub PR description or release overview."""
    categories: dict[str, list[CommitInfo]] = {
        "Features": [],
        "Bug Fixes": [],
        "Performance": [],
        "Refactoring & Architecture": [],
        "Maintenance & Dependencies": [],
        "Documentation": [],
        "Tests & Verification": [],
        "Other Changes": [],
    }

    breaking_changes: list[CommitInfo] = []
    all_issue_refs: set[str] = set()

    for commit in report.commits:
        if commit.is_breaking:
            breaking_changes.append(commit)
        cat = categorize_commit(commit)
        categories.setdefault(cat, []).append(commit)
        for ref in commit.issue_refs:
            all_issue_refs.add(ref)

    sections: list[str] = []

    # Title & Summary
    sections.append("## Summary")
    if report.pr_title:
        sections.append(f"**PR**: {report.pr_title}\n")
    sections.append(
        f"This PR introduces changes comparing `{report.head_ref}` against `{report.base_ref}`.\n"
        f"- **Commits**: {len(report.commits)}\n"
        f"- **Files Changed**: {len(report.changed_files)} (+{report.additions} / -{report.deletions} lines)\n"
    )

    # Breaking Changes (top priority!)
    if breaking_changes:
        sections.append("## ⚠️ Breaking Changes")
        for item in breaking_changes:
            scope_prefix = f"**{item.scope}**: " if item.scope else ""
            desc = item.breaking_description or item.subject
            sections.append(f"- 🚨 {scope_prefix}{desc} (`{item.hash}`)")
        sections.append("")

    # Standard Categories
    category_emojis = {
        "Features": "🚀",
        "Bug Fixes": "🐛",
        "Performance": "⚡",
        "Refactoring & Architecture": "🔄",
        "Documentation": "📖",
        "Maintenance & Dependencies": "🛠️",
        "Tests & Verification": "🧪",
        "Other Changes": "📌",
    }

    for cat_name, emoji in category_emojis.items():
        items = categories.get(cat_name, [])
        if not items:
            continue
        sections.append(f"## {emoji} {cat_name}")
        for item in items:
            scope_prefix = f"**{item.scope}**: " if item.scope else ""
            ref_suffix = f" ({', '.join(item.issue_refs)})" if item.issue_refs else ""
            sections.append(f"- {scope_prefix}{item.subject}{ref_suffix} (`{item.hash}`)")
        sections.append("")

    # Affected Areas
    file_list = [path for _, path in report.changed_files]
    areas = detect_affected_areas(file_list)
    if areas:
        sections.append("## 📦 Affected Areas")
        for area in areas:
            sections.append(f"- {area}")
        sections.append("")

    # Related Issues
    if all_issue_refs:
        sections.append("## 🔗 Related Issues")
        sections.append(", ".join(sorted(all_issue_refs)))
        sections.append("")

    return "\n".join(sections).strip()


def format_keep_a_changelog(report: ChangelogReport) -> str:
    """Generate Markdown following the Keep a Changelog standard."""
    sections: list[str] = []
    sections.append(f"## [{report.head_ref}] - Changes compared to {report.base_ref}\n")

    mapping = {
        "Features": "### Added",
        "Bug Fixes": "### Fixed",
        "Performance": "### Performance",
        "Refactoring & Architecture": "### Changed",
        "Maintenance & Dependencies": "### Maintenance",
        "Documentation": "### Documentation",
    }

    categorized: dict[str, list[CommitInfo]] = {}
    for commit in report.commits:
        cat = categorize_commit(commit)
        categorized.setdefault(cat, []).append(commit)

    for cat_name, header in mapping.items():
        items = categorized.get(cat_name, [])
        if items:
            sections.append(header)
            for item in items:
                scope_str = f"**{item.scope}**: " if item.scope else ""
                sections.append(f"- {scope_str}{item.subject} ({item.hash})")
            sections.append("")

    return "\n".join(sections).strip()


def format_concise_changelog(report: ChangelogReport) -> str:
    """Generate a concise, focused, and clear changelog prioritizing high-signal changes."""
    breaking_changes: list[CommitInfo] = []
    features: list[CommitInfo] = []
    fixes: list[CommitInfo] = []
    improvements: list[CommitInfo] = []
    maintenance: list[CommitInfo] = []

    for commit in report.commits:
        if commit.is_breaking:
            breaking_changes.append(commit)

        cat = categorize_commit(commit)
        if cat == "Features":
            features.append(commit)
        elif cat == "Bug Fixes":
            fixes.append(commit)
        elif cat in ("Performance", "Refactoring & Architecture"):
            improvements.append(commit)
        elif cat in ("Maintenance & Dependencies", "Documentation"):
            maintenance.append(commit)

    sections: list[str] = []

    if breaking_changes:
        sections.append("### ⚠️ Breaking Changes")
        for item in breaking_changes:
            scope_prefix = f"**{item.scope}**: " if item.scope else ""
            desc = item.breaking_description or item.subject
            sections.append(f"- 🚨 {scope_prefix}{desc} (`{item.hash}`)")
        sections.append("")

    if features:
        sections.append("### 🚀 Features")
        for item in features:
            scope_prefix = f"**{item.scope}**: " if item.scope else ""
            ref = f" ({', '.join(item.issue_refs)})" if item.issue_refs else ""
            sections.append(f"- {scope_prefix}{item.subject}{ref} (`{item.hash}`)")
        sections.append("")

    if fixes:
        sections.append("### 🐛 Bug Fixes")
        for item in fixes:
            scope_prefix = f"**{item.scope}**: " if item.scope else ""
            ref = f" ({', '.join(item.issue_refs)})" if item.issue_refs else ""
            sections.append(f"- {scope_prefix}{item.subject}{ref} (`{item.hash}`)")
        sections.append("")

    if improvements:
        sections.append("### 🔄 Improvements & Architecture")
        for item in improvements:
            scope_prefix = f"**{item.scope}**: " if item.scope else ""
            sections.append(f"- {scope_prefix}{item.subject} (`{item.hash}`)")
        sections.append("")

    if maintenance:
        sections.append("### 🛠️ Maintenance")
        for item in maintenance:
            scope_prefix = f"**{item.scope}**: " if item.scope else ""
            sections.append(f"- {scope_prefix}{item.subject} (`{item.hash}`)")
        sections.append("")

    return "\n".join(sections).strip()


def insert_into_changelog(existing_content: str, new_entries: str) -> str:
    """
    Insert new changelog entries into the latest entry of CHANGELOG.md.
    If '## [Unreleased]' exists, injects under it.
    Otherwise, injects under the latest '## [...]' version entry.
    If no version headings exist, appends to the file or places after main header.
    """
    new_entries_cleaned = new_entries.strip()
    if not new_entries_cleaned:
        return existing_content

    # 1. Check for Unreleased heading: ## [Unreleased] or ## Unreleased
    unreleased_pattern = re.compile(r"^(##\s+\[?unreleased\]?.*)$", re.IGNORECASE | re.MULTILINE)
    match_unreleased = unreleased_pattern.search(existing_content)
    if match_unreleased:
        header_end = match_unreleased.end()
        after_header = existing_content[header_end:]
        return f"{existing_content[:header_end]}\n\n{new_entries_cleaned}\n{after_header.lstrip('\r\n')}"

    # 2. Check for latest version heading: ## [x.y.z] or ## x.y.z
    version_pattern = re.compile(r"^(##\s+\[?[0-9]+\.[0-9]+(?:\.[0-9]+)?[^\]\n]*\]?.*)$", re.MULTILINE)
    match_version = version_pattern.search(existing_content)
    if match_version:
        header_end = match_version.end()
        after_header = existing_content[header_end:]
        return f"{existing_content[:header_end]}\n\n{new_entries_cleaned}\n{after_header.lstrip('\r\n')}"

    # 3. Check for any top ## heading
    h2_pattern = re.compile(r"^(##\s+.*)$", re.MULTILINE)
    match_h2 = h2_pattern.search(existing_content)
    if match_h2:
        header_end = match_h2.end()
        after_header = existing_content[header_end:]
        return f"{existing_content[:header_end]}\n\n{new_entries_cleaned}\n{after_header.lstrip('\r\n')}"

    # 4. If only # Header exists
    h1_pattern = re.compile(r"^(#\s+.*)$", re.MULTILINE)
    match_h1 = h1_pattern.search(existing_content)
    if match_h1:
        header_end = match_h1.end()
        after_header = existing_content[header_end:]
        return f"{existing_content[:header_end]}\n\n{new_entries_cleaned}\n{after_header.lstrip('\r\n')}"

    # 5. Fallback: append
    return f"{existing_content.strip()}\n\n{new_entries_cleaned}\n"


def find_and_update_changelog(repo_root: Optional[Path], new_entries: str) -> Optional[Path]:
    """
    Search for CHANGELOG.md in repository root or current directory,
    and update its latest entry if found.
    """
    candidates: list[Path] = []
    if repo_root:
        candidates.extend([repo_root / "CHANGELOG.md", repo_root / "changelog.md"])
    candidates.extend([Path("CHANGELOG.md"), Path("changelog.md")])

    for path in candidates:
        if path.is_file():
            existing = path.read_text(encoding="utf-8", errors="replace")
            updated = insert_into_changelog(existing, new_entries)
            path.write_text(updated, encoding="utf-8")
            return path
    return None


def format_compact_changelog(report: ChangelogReport) -> str:
    """Generate a compact single-section list of changes."""
    lines: list[str] = []
    lines.append(f"### Changes (`{report.head_ref}` → `{report.base_ref}`)")
    for c in report.commits:
        scope_str = f"({c.scope})" if c.scope else ""
        type_str = f"`{c.commit_type}{scope_str}`"
        lines.append(f"- {type_str}: {c.subject} ({c.hash})")
    return "\n".join(lines)


def get_git_base_branch() -> str:
    """Detect default remote branch (origin/main or origin/master)."""
    code, out, _ = run_cmd(["git", "symbolic-ref", "refs/remotes/origin/HEAD"])
    if code == 0 and out:
        return out.strip().replace("refs/remotes/", "")

    # Try common defaults
    for candidate in ["origin/main", "origin/master", "main", "master"]:
        code, _, _ = run_cmd(["git", "rev-parse", "--verify", candidate])
        if code == 0:
            return candidate

    return "origin/main"


def fetch_commits(base_ref: str, head_ref: str = "HEAD") -> List[CommitInfo]:
    """Extract commits between base_ref and head_ref."""
    delimiter = "---COMMITSPLIT---"
    cmd = [
        "git",
        "log",
        f"{base_ref}..{head_ref}",
        f'--format=%H%x1f%B{delimiter}',
    ]
    code, stdout, stderr = run_cmd(cmd)
    if code != 0:
        return []

    commits: list[CommitInfo] = []
    entries = stdout.split(delimiter)
    for entry in entries:
        entry = entry.strip()
        if not entry:
            continue
        parts = entry.split("\x1f", 1)
        commit_hash = parts[0].strip()
        commit_msg = parts[1].strip() if len(parts) > 1 else ""
        commits.append(parse_commit_message(commit_hash, commit_msg))

    return commits


def fetch_diff_stats(base_ref: str, head_ref: str = "HEAD") -> Tuple[List[Tuple[str, str]], int, int]:
    """Extract changed files and (+additions / -deletions)."""
    code, stdout, _ = run_cmd(["git", "diff", f"{base_ref}..{head_ref}", "--name-status"])
    files: list[Tuple[str, str]] = []
    if code == 0 and stdout:
        for line in stdout.splitlines():
            line = line.strip()
            if not line:
                continue
            parts = line.split(None, 1)
            if len(parts) == 2:
                files.append((parts[0], parts[1]))

    additions = 0
    deletions = 0
    code, numstat, _ = run_cmd(["git", "diff", f"{base_ref}..{head_ref}", "--numstat"])
    if code == 0 and numstat:
        for line in numstat.splitlines():
            parts = line.split()
            if len(parts) >= 2:
                try:
                    if parts[0] != "-":
                        additions += int(parts[0])
                    if parts[1] != "-":
                        deletions += int(parts[1])
                except ValueError:
                    pass

    return files, additions, deletions


def fetch_pr_details(pr_id: str) -> Optional[dict[str, Any]]:
    """Fetch PR details using GitHub CLI (`gh`)."""
    cmd = [
        "gh",
        "pr",
        "view",
        str(pr_id),
        "--json",
        "number,title,url,baseRefName,headRefName,additions,deletions,commits",
    ]
    code, stdout, _ = run_cmd(cmd)
    if code != 0 or not stdout:
        return None
    try:
        return json.loads(stdout)
    except Exception:
        return None


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate structured changelogs for pull requests based on git changes."
    )
    parser.add_argument(
        "--base",
        type=str,
        help="Base branch/ref (default: auto-detected, e.g., origin/main)",
    )
    parser.add_argument(
        "--head",
        type=str,
        default="HEAD",
        help="Head branch/ref (default: HEAD)",
    )
    parser.add_argument(
        "--pr",
        type=str,
        help="GitHub PR number or URL to generate changelog for",
    )
    parser.add_argument(
        "--format",
        choices=["pr", "concise", "keepachangelog", "compact", "json"],
        default="pr",
        help="Output format (default: pr)",
    )
    parser.add_argument(
        "--output",
        type=str,
        help="File path to save the changelog output (default: print to stdout)",
    )
    parser.add_argument(
        "--changelog-file",
        type=str,
        help="Path to CHANGELOG.md to update (default: checks repository root)",
    )
    parser.add_argument(
        "--no-changelog",
        action="store_true",
        help="Disable automatic updating of CHANGELOG.md when it exists",
    )
    parser.add_argument(
        "--update-pr",
        action="store_true",
        help="Automatically update the GitHub PR body using `gh pr edit`",
    )

    args = parser.parse_args()

    pr_number = None
    pr_title = None
    pr_url = None
    base_ref = args.base
    head_ref = args.head

    # Handle PR mode via GitHub CLI
    if args.pr:
        pr_data = fetch_pr_details(args.pr)
        if pr_data:
            pr_number = pr_data.get("number")
            pr_title = pr_data.get("title")
            pr_url = pr_data.get("url")
            if not base_ref:
                base_ref = f"origin/{pr_data.get('baseRefName', 'main')}"
            if head_ref == "HEAD":
                head_ref = pr_data.get("headRefName", "HEAD")

    # Fallback to local git detection
    if not base_ref:
        base_ref = get_git_base_branch()

    # Get branch name if head is HEAD
    if head_ref == "HEAD":
        _, current_branch, _ = run_cmd(["git", "branch", "--show-current"])
        head_display = current_branch if current_branch else "HEAD"
    else:
        head_display = head_ref

    commits = fetch_commits(base_ref, head_ref)
    files, additions, deletions = fetch_diff_stats(base_ref, head_ref)

    report = ChangelogReport(
        base_ref=base_ref,
        head_ref=head_display,
        commits=commits,
        changed_files=files,
        additions=additions,
        deletions=deletions,
        pr_number=pr_number,
        pr_title=pr_title,
        pr_url=pr_url,
    )

    # Format the report
    if args.format == "json":
        output_content = json.dumps(asdict(report), indent=2)
    elif args.format == "concise":
        output_content = format_concise_changelog(report)
    elif args.format == "keepachangelog":
        output_content = format_keep_a_changelog(report)
    elif args.format == "compact":
        output_content = format_compact_changelog(report)
    else:
        output_content = format_pr_changelog(report)

    # Output destination
    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(output_content, encoding="utf-8")
        print(f"Changelog written to {out_path}")
    else:
        print(output_content)

    # Check and update CHANGELOG.md if it exists (unless --no-changelog)
    if not args.no_changelog:
        target_cl_path = Path(args.changelog_file) if args.changelog_file else None
        concise_entry = format_concise_changelog(report)
        if target_cl_path and target_cl_path.is_file():
            existing = target_cl_path.read_text(encoding="utf-8", errors="replace")
            updated = insert_into_changelog(existing, concise_entry)
            target_cl_path.write_text(updated, encoding="utf-8")
            print(f"\n[CHANGELOG.md] Successfully updated latest entry in {target_cl_path}")
        else:
            updated_path = find_and_update_changelog(Path.cwd(), concise_entry)
            if updated_path:
                print(f"\n[CHANGELOG.md] Successfully updated latest entry in {updated_path}")

    # Optional: Update PR description
    if args.update_pr:
        target_pr = str(pr_number) if pr_number else args.pr
        if not target_pr:
            # Check if current branch has an open PR
            code, stdout, _ = run_cmd(["gh", "pr", "view", "--json", "number"])
            if code == 0 and stdout:
                try:
                    target_pr = str(json.loads(stdout).get("number"))
                except Exception:
                    pass

        if target_pr:
            code, _, err = run_cmd(["gh", "pr", "edit", str(target_pr), "--body", output_content])
            if code == 0:
                print(f"\n[SUCCESS] Successfully updated PR #{target_pr} body.")
            else:
                print(f"\n[ERROR] Failed to update PR #{target_pr}: {err}", file=sys.stderr)
        else:
            print("\n[WARNING] Could not determine PR number to update.", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())

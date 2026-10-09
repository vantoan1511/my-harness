"""
Unit tests for PR changelog generator script.
Verifies conventional commit parsing, classification, area detection, and formatting.
"""

import unittest
import sys
from pathlib import Path

# Add scripts directory to sys.path
scripts_dir = Path(__file__).parent.parent
sys.path.insert(0, str(scripts_dir))

from generate_changelog import (
    CommitInfo,
    parse_commit_message,
    categorize_commit,
    detect_affected_areas,
    format_pr_changelog,
    format_keep_a_changelog,
    format_compact_changelog,
    format_concise_changelog,
    insert_into_changelog,
    ChangelogReport,
)


class TestParseCommitMessage(unittest.TestCase):
    def test_standard_conventional_commit(self):
        msg = "feat(auth): add OAuth2 token refresh support\n\nCloses #123"
        info = parse_commit_message("abc1234", msg)
        self.assertEqual(info.hash, "abc1234")
        self.assertEqual(info.commit_type, "feat")
        self.assertEqual(info.scope, "auth")
        self.assertEqual(info.subject, "add OAuth2 token refresh support")
        self.assertFalse(info.is_breaking)
        self.assertEqual(info.issue_refs, ["#123"])

    def test_breaking_change_bang(self):
        msg = "fix(ipc)!: change payload structure for cluster status\n\nBREAKING CHANGE: payload now requires clusterId"
        info = parse_commit_message("def5678", msg)
        self.assertEqual(info.commit_type, "fix")
        self.assertEqual(info.scope, "ipc")
        self.assertTrue(info.is_breaking)
        self.assertIn("payload now requires clusterId", info.breaking_description)

    def test_commit_without_scope(self):
        msg = "docs: update architecture diagram in README"
        info = parse_commit_message("789abcd", msg)
        self.assertEqual(info.commit_type, "docs")
        self.assertIsNone(info.scope)
        self.assertEqual(info.subject, "update architecture diagram in README")
        self.assertFalse(info.is_breaking)

    def test_non_conventional_commit_fallback(self):
        msg = "Fix subtle issue with table row height on Windows"
        info = parse_commit_message("1112223", msg)
        self.assertEqual(info.commit_type, "fix")
        self.assertIsNone(info.scope)
        self.assertEqual(info.subject, "Fix subtle issue with table row height on Windows")


class TestCategorizeCommit(unittest.TestCase):
    def test_features(self):
        info = CommitInfo(hash="1", commit_type="feat", scope="ui", subject="add dark mode toggle")
        self.assertEqual(categorize_commit(info), "Features")

    def test_fixes(self):
        info = CommitInfo(hash="2", commit_type="fix", scope="core", subject="prevent null dereference")
        self.assertEqual(categorize_commit(info), "Bug Fixes")

    def test_performance(self):
        info = CommitInfo(hash="3", commit_type="perf", scope="engine", subject="optimize cluster cache")
        self.assertEqual(categorize_commit(info), "Performance")

    def test_refactoring(self):
        info = CommitInfo(hash="4", commit_type="refactor", scope="store", subject="extract settings store")
        self.assertEqual(categorize_commit(info), "Refactoring & Architecture")

    def test_documentation(self):
        info = CommitInfo(hash="5", commit_type="docs", scope=None, subject="document IPC protocol")
        self.assertEqual(categorize_commit(info), "Documentation")

    def test_maintenance(self):
        info = CommitInfo(hash="6", commit_type="chore", scope="deps", subject="upgrade primevue to 4.2.0")
        self.assertEqual(categorize_commit(info), "Maintenance & Dependencies")


class TestAreaDetection(unittest.TestCase):
    def test_frontend_files(self):
        files = ["src/components/MyTable.vue", "src/stores/clusterStore.ts", "src/assets/base.css"]
        areas = detect_affected_areas(files)
        self.assertIn("Frontend (Vue / TypeScript / UI)", areas)

    def test_backend_files(self):
        files = ["core/engine/src/ipc/handlers.rs", "core/Cargo.toml"]
        areas = detect_affected_areas(files)
        self.assertIn("Backend (Rust / Engine / IPC)", areas)

    def test_ci_and_docs(self):
        files = [".github/workflows/ci.yml", "README.md", "docs/api.md"]
        areas = detect_affected_areas(files)
        self.assertIn("CI & Workflows", areas)
        self.assertIn("Documentation", areas)


class TestFormatting(unittest.TestCase):
    def setUp(self):
        self.commits = [
            CommitInfo(
                hash="a1b2c3d",
                commit_type="feat",
                scope="search",
                subject="add cluster-level isolation to search everywhere",
                is_breaking=False,
                issue_refs=["#45"],
            ),
            CommitInfo(
                hash="e5f6a7b",
                commit_type="fix",
                scope="ipc",
                subject="handle socket reconnection timeout gracefully",
                is_breaking=True,
                breaking_description="Reconnection interval is now enforced in backend config",
            ),
        ]
        self.changed_files = [
            ("M", "src/components/search/SearchEverywhereModal.vue"),
            ("M", "core/engine/src/ipc/handlers.rs"),
        ]
        self.report = ChangelogReport(
            base_ref="main",
            head_ref="feat/search-isolation",
            commits=self.commits,
            changed_files=self.changed_files,
            additions=120,
            deletions=35,
        )

    def test_pr_format(self):
        output = format_pr_changelog(self.report)
        self.assertIn("## Summary", output)
        self.assertIn("## 🚀 Features", output)
        self.assertIn("## 🐛 Bug Fixes", output)
        self.assertIn("## ⚠️ Breaking Changes", output)
        self.assertIn("cluster-level isolation", output)
        self.assertIn("socket reconnection timeout gracefully", output)
        self.assertIn("Reconnection interval is now enforced", output)

    def test_keep_a_changelog_format(self):
        output = format_keep_a_changelog(self.report)
        self.assertIn("### Added", output)
        self.assertIn("### Fixed", output)

    def test_compact_format(self):
        output = format_compact_changelog(self.report)
        self.assertIn("- `feat(search)`:", output)
        self.assertIn("- `fix(ipc)`:", output)

    def test_concise_format(self):
        output = format_concise_changelog(self.report)
        self.assertIn("### ⚠️ Breaking Changes", output)
        self.assertIn("### 🚀 Features", output)
        self.assertIn("### 🐛 Bug Fixes", output)
        self.assertIn("- **search**: add cluster-level isolation", output)
        self.assertNotIn("## Summary", output)  # Concise format omits heavy boilerplate


class TestInsertIntoChangelog(unittest.TestCase):
    def test_insert_into_unreleased_section(self):
        existing = """# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added
- Previous unreleased feature

## [1.0.0] - 2026-09-01
### Fixed
- Old bug fix
"""
        new_entries = """### Fixed
- **ipc**: handle socket reconnection timeout gracefully (e5f6a7b)"""

        updated = insert_into_changelog(existing, new_entries)
        self.assertIn("## [Unreleased]", updated)
        self.assertIn("- **ipc**: handle socket reconnection timeout gracefully", updated)
        # Verify it came BEFORE 1.0.0
        pos_new = updated.find("- **ipc**: handle socket reconnection")
        pos_old = updated.find("## [1.0.0]")
        self.assertTrue(pos_new < pos_old)

    def test_insert_into_latest_version_when_no_unreleased(self):
        existing = """# Changelog

## [1.2.0] - 2026-10-01
### Added
- Feature in 1.2.0

## [1.1.0] - 2026-09-15
### Fixed
- Feature in 1.1.0
"""
        new_entries = """### 🐛 Bug Fixes
- **search**: isolate resources by cluster (8c47818)"""

        updated = insert_into_changelog(existing, new_entries)
        self.assertIn("## [1.2.0] - 2026-10-01", updated)
        self.assertIn("- **search**: isolate resources by cluster (8c47818)", updated)
        pos_new = updated.find("- **search**: isolate resources by cluster")
        pos_next_version = updated.find("## [1.1.0]")
        self.assertTrue(pos_new < pos_next_version)

    def test_insert_when_no_headers_exist(self):
        existing = "# Changelog\n\nNo releases yet.\n"
        new_entries = "### Features\n- New feature"
        updated = insert_into_changelog(existing, new_entries)
        self.assertIn("### Features\n- New feature", updated)

    def test_find_and_update_changelog_file(self):
        import tempfile
        from generate_changelog import find_and_update_changelog

        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            changelog_file = tmppath / "CHANGELOG.md"
            changelog_file.write_text(
                "# Changelog\n\n## [Unreleased]\n\n### Added\n- Init",
                encoding="utf-8",
            )
            result = find_and_update_changelog(tmppath, "### Fixed\n- Fix something")
            self.assertIsNotNone(result)
            self.assertEqual(result, changelog_file)
            updated_content = changelog_file.read_text(encoding="utf-8")
            self.assertIn("### Fixed\n- Fix something", updated_content)


if __name__ == "__main__":
    unittest.main()

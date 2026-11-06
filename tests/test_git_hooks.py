import unittest
import tempfile
import shutil
import subprocess
from pathlib import Path
from unittest.mock import MagicMock

import harness

class TestGitHooks(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.addCleanup(lambda: shutil.rmtree(self.temp_dir, ignore_errors=True))
        self.repo = Path(self.temp_dir)
        # Initialize mock git repository
        subprocess.run(["git", "init", "-b", "main"], cwd=self.repo, capture_output=True, check=True)

    def test_is_git_hook_installed_false_when_missing(self):
        self.assertFalse(harness.is_git_hook_installed(self.repo))

    def test_install_git_hooks_creates_post_merge_and_pre_commit_hooks(self):
        installed = harness.install_git_hooks(self.repo)
        self.assertTrue(installed)
        self.assertTrue(harness.is_git_hook_installed(self.repo))

        # Check post-merge hook
        pm_path = self.repo / ".git" / "hooks" / "post-merge"
        self.assertTrue(pm_path.exists())
        pm_content = pm_path.read_text(encoding="utf-8")
        self.assertIn('"$REPO_DIR/harness.py" update --force', pm_content)
        self.assertIn("#!/bin/sh", pm_content)

        # Check pre-commit hook
        pc_path = self.repo / ".git" / "hooks" / "pre-commit"
        self.assertTrue(pc_path.exists())
        pc_content = pc_path.read_text(encoding="utf-8")
        self.assertIn("verify_shift_left.py", pc_content)
        self.assertIn("--staged", pc_content)
        self.assertIn("#!/bin/sh", pc_content)

    def test_is_git_hook_installed_false_if_one_hook_missing(self):
        harness.install_git_hooks(self.repo)
        self.assertTrue(harness.is_git_hook_installed(self.repo))
        # Remove pre-commit
        (self.repo / ".git" / "hooks" / "pre-commit").unlink()
        self.assertFalse(harness.is_git_hook_installed(self.repo))

    def test_install_git_hooks_idempotent(self):
        harness.install_git_hooks(self.repo)
        installed_again = harness.install_git_hooks(self.repo)
        self.assertTrue(installed_again)
        self.assertTrue(harness.is_git_hook_installed(self.repo))

    def test_cmd_init_installs_git_hooks_for_project_repo(self):
        parser = harness.build_parser()
        args = parser.parse_args(["init", str(self.repo)])
        harness.cmd_init(args)
        self.assertTrue(harness.is_git_hook_installed(self.repo))

    def test_install_git_hooks_fails_gracefully_when_not_git_repo(self):
        non_git = Path(self.temp_dir) / "not_git"
        non_git.mkdir()
        installed = harness.install_git_hooks(non_git)
        self.assertFalse(installed)
        self.assertFalse(harness.is_git_hook_installed(non_git))

    def test_cmd_install_hooks_cli_subcommand(self):
        parser = harness.build_parser()
        args = parser.parse_args(["install-hooks", str(self.repo)])
        self.assertEqual(args.subcommand, "install-hooks")
        self.assertEqual(args.target, str(self.repo))

        ret = harness.cmd_install_hooks(args)
        self.assertEqual(ret, 0)
        self.assertTrue(harness.is_git_hook_installed(self.repo))

if __name__ == "__main__":
    unittest.main()

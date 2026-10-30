import unittest
import tempfile
import shutil
import sys
import json
from pathlib import Path
from unittest.mock import patch, MagicMock

import harness

class TestHarnessUpdate(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.addCleanup(lambda: shutil.rmtree(self.temp_dir, ignore_errors=True))
        self.harness_root = harness.get_harness_root()

    def test_deploy_antigravity_plugin_creates_valid_structure(self):
        mock_home = Path(self.temp_dir) / "mock_home"
        mock_plugin_dir = mock_home / ".gemini" / "config" / "plugins" / "my-harness"

        res = harness.deploy_antigravity_plugin(self.harness_root, mock_plugin_dir)

        self.assertTrue(mock_plugin_dir.exists())
        self.assertTrue(res.manifest_updated)
        self.assertTrue(res.rules_consolidated)
        self.assertGreater(res.skills_copied, 0)

        # Check plugin.json
        manifest_file = mock_plugin_dir / "plugin.json"
        self.assertTrue(manifest_file.exists())
        manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
        self.assertEqual(manifest["name"], "my-harness")

        # Check rules/AGENTS.md
        rules_agents = mock_plugin_dir / "rules" / "AGENTS.md"
        self.assertTrue(rules_agents.exists())
        content = rules_agents.read_text(encoding="utf-8")
        self.assertIn("Shift-Left Quality", content)
        self.assertIn("Natural Human Writing", content)

        # Check skills
        self.assertTrue((mock_plugin_dir / "skills" / "specify" / "SKILL.md").exists())
        self.assertTrue((mock_plugin_dir / "skills" / "implement" / "SKILL.md").exists())

        # Check assets
        self.assertTrue((mock_plugin_dir / "assets" / "logo.svg").exists())

        # Check plugin cleanliness (no __pycache__, .pyc, tests/, evals/, openai.yaml, or .update_check.json inside plugin)
        for p in mock_plugin_dir.rglob("*"):
            self.assertNotEqual(p.name, "__pycache__", f"Found __pycache__ in plugin: {p}")
            self.assertNotEqual(p.suffix, ".pyc", f"Found .pyc in plugin: {p}")
            self.assertNotIn("tests", p.parts, f"Found tests/ dir in plugin: {p}")
            self.assertNotIn("evals", p.parts, f"Found evals/ dir in plugin: {p}")
            self.assertNotEqual(p.name, "openai.yaml", f"Found openai.yaml in plugin: {p}")
        self.assertFalse((mock_plugin_dir / ".update_check.json").exists())

        # Check portable scripts and cross-path rules/skills
        self.assertTrue((mock_plugin_dir / "scripts" / "verify_shift_left.py").exists())
        self.assertTrue((mock_plugin_dir / "scripts" / "shift_left_hook.py").exists())
        self.assertTrue((mock_plugin_dir / "scripts" / "memory_logger.py").exists())
        self.assertIn("~/.gemini/config/plugins/my-harness/scripts/verify_shift_left.py", content)

        # Check progressive disclosure resource templates for large skills
        self.assertTrue((mock_plugin_dir / "skills" / "implement" / "resources" / "report-template.md").exists())
        self.assertTrue((mock_plugin_dir / "skills" / "prd" / "resources" / "prd-template.md").exists())
        self.assertTrue((mock_plugin_dir / "skills" / "prp-plan" / "resources" / "plan-template.md").exists())

        # Check SessionStart auto-update hook and script
        self.assertTrue((mock_plugin_dir / "scripts" / "auto_update_hook.py").exists())
        self.assertTrue((mock_plugin_dir / "hooks.json").exists())
        hooks_cfg = json.loads((mock_plugin_dir / "hooks.json").read_text(encoding="utf-8"))
        self.assertIn("my-harness-auto-updater", hooks_cfg)
        self.assertIn("SessionStart", hooks_cfg["my-harness-auto-updater"])

    @patch("subprocess.run")
    def test_check_for_updates_detects_behind_commits(self, mock_run):
        # Mock git rev-parse HEAD, git rev-parse origin/main, git rev-list
        def side_effect(cmd, **kwargs):
            mock_res = MagicMock()
            mock_res.returncode = 0
            if "rev-parse" in cmd and "HEAD" in cmd:
                mock_res.stdout = "1111111\n"
            elif "rev-parse" in cmd and any("origin" in arg for arg in cmd):
                mock_res.stdout = "2222222\n"
            elif "rev-list" in cmd:
                mock_res.stdout = "commit1\ncommit2\ncommit3\n"
            return mock_res

        mock_run.side_effect = side_effect
        res = harness.check_for_updates(self.harness_root, branch="main")

        self.assertTrue(res.is_git_repo)
        self.assertTrue(res.has_update)
        self.assertEqual(res.behind_count, 3)
        self.assertIsNone(res.error)

    @patch("subprocess.run")
    def test_check_for_updates_handles_network_or_git_errors_cleanly(self, mock_run):
        mock_run.side_effect = Exception("network unreachable")

        res = harness.check_for_updates(self.harness_root, branch="main")

        self.assertFalse(res.has_update)
        self.assertEqual(res.behind_count, 0)
        self.assertIsNotNone(res.error)

    def test_should_check_for_updates_throttling(self):
        cache_file = Path(self.temp_dir) / ".update_check.json"
        import time

        # Case 1: No cache file -> should check
        self.assertTrue(harness.should_check_for_updates(cache_file, interval_hours=24))

        # Case 2: Fresh cache file -> should not check
        harness.save_update_check_state(cache_file, {"last_check_timestamp": time.time(), "has_update": False})
        self.assertFalse(harness.should_check_for_updates(cache_file, interval_hours=24))

        # Case 3: Expired cache file -> should check
        harness.save_update_check_state(cache_file, {"last_check_timestamp": time.time() - (25 * 3600), "has_update": False})
        self.assertTrue(harness.should_check_for_updates(cache_file, interval_hours=24))

    @patch("harness.check_for_updates")
    def test_cmd_update_check_only_does_not_mutate_plugin(self, mock_check):
        mock_check.return_value = harness.UpdateCheckResult(
            is_git_repo=True,
            current_commit="1111111",
            remote_commit="2222222",
            has_update=True,
            behind_count=2,
            error=None
        )

        mock_home = Path(self.temp_dir) / "mock_home"
        plugin_dir = mock_home / ".gemini" / "config" / "plugins" / "my-harness"

        args = MagicMock()
        args.check_only = True
        args.force = False
        args.sync_project = False
        args.target = "."
        args.branch = "main"

        with patch("pathlib.Path.home", return_value=mock_home):
            ret = harness.cmd_update(args)
            self.assertEqual(ret, 0)
            self.assertFalse(plugin_dir.exists())

    @patch("subprocess.run")
    def test_cmd_update_repackages_plugin_and_updates_manifest(self, mock_run):
        mock_res = MagicMock()
        mock_res.returncode = 0
        mock_res.stdout = ""
        mock_run.return_value = mock_res

        mock_home = Path(self.temp_dir) / "mock_home"
        plugin_dir = mock_home / ".gemini" / "config" / "plugins" / "my-harness"

        args = MagicMock()
        args.check_only = False
        args.force = True
        args.sync_project = False
        args.target = "."
        args.branch = "main"

        with patch("pathlib.Path.home", return_value=mock_home):
            ret = harness.cmd_update(args)
            self.assertEqual(ret, 0)
            self.assertTrue(plugin_dir.exists())
            self.assertTrue((plugin_dir / "plugin.json").exists())
            self.assertTrue((plugin_dir / "rules" / "AGENTS.md").exists())
            self.assertTrue((plugin_dir / "skills" / "specify").exists())

    @patch("subprocess.run")
    def test_cmd_update_with_sync_project_updates_local_agents(self, mock_run):
        mock_res = MagicMock()
        mock_res.returncode = 0
        mock_res.stdout = ""
        mock_run.return_value = mock_res

        mock_home = Path(self.temp_dir) / "mock_home"
        proj_dir = Path(self.temp_dir) / "test_project"
        (proj_dir / ".agents").mkdir(parents=True)

        args = MagicMock()
        args.check_only = False
        args.force = True
        args.sync_project = True
        args.target = str(proj_dir)
        args.branch = "main"

        with patch("pathlib.Path.home", return_value=mock_home):
            ret = harness.cmd_update(args)
            self.assertEqual(ret, 0)
            self.assertTrue((proj_dir / ".agents" / "scripts" / "verify_shift_left.py").exists())

    def test_auto_update_hook_spawns_background_update_when_due(self):
        import importlib.util
        hook_script = self.harness_root / "template" / ".agents" / "scripts" / "auto_update_hook.py"
        self.assertTrue(hook_script.exists(), "auto_update_hook.py must exist in template/.agents/scripts/")

        spec = importlib.util.spec_from_file_location("auto_update_hook", str(hook_script))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        cache_file = Path(self.temp_dir) / ".update_check.json"
        fake_repo = Path(self.temp_dir) / "fake_repo"
        fake_repo.mkdir()
        (fake_repo / "harness.py").write_text("# fake", encoding="utf-8")

        # Expired timestamp -> should spawn Popen and return {}
        cache_file.write_text(json.dumps({
            "last_check_timestamp": 0,
            "source_repo": str(fake_repo),
            "just_updated": False
        }), encoding="utf-8")

        with patch("subprocess.Popen") as mock_popen:
            result = mod.run_session_start_check(cache_file, interval_hours=6)
            self.assertEqual(result, {})
            self.assertTrue(mock_popen.called, "Popen should be called when update check is due")

    def test_auto_update_hook_injects_notification_after_background_update(self):
        import importlib.util
        import time
        hook_script = self.harness_root / "template" / ".agents" / "scripts" / "auto_update_hook.py"
        self.assertTrue(hook_script.exists(), "auto_update_hook.py must exist in template/.agents/scripts/")

        spec = importlib.util.spec_from_file_location("auto_update_hook", str(hook_script))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        cache_file = Path(self.temp_dir) / ".update_check.json"
        cache_file.write_text(json.dumps({
            "last_check_timestamp": time.time(),
            "just_updated": True,
            "updated_to_commit": "abc1234",
            "behind_count": 2
        }), encoding="utf-8")

        with patch("subprocess.Popen") as mock_popen:
            result = mod.run_session_start_check(cache_file, interval_hours=6)
            self.assertFalse(mock_popen.called, "Popen should NOT be called when cache is fresh")
            self.assertIn("injectSteps", result)
            msg = result["injectSteps"][0]["systemMessage"]["systemMessage"]
            self.assertIn("abc1234", msg)

        # Verify just_updated flag was cleared so it only notifies once
        updated_cache = json.loads(cache_file.read_text(encoding="utf-8"))
        self.assertFalse(updated_cache.get("just_updated"))

if __name__ == "__main__":
    unittest.main()

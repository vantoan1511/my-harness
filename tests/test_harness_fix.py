import unittest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

import harness

class TestHarnessFix(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.addCleanup(lambda: shutil.rmtree(self.temp_dir, ignore_errors=True))

    def test_detect_global_installation_none(self):
        mock_home = Path(self.temp_dir) / "empty_home"
        mock_home.mkdir()

        with patch("pathlib.Path.home", return_value=mock_home):
            info = harness.detect_global_installation()
            self.assertFalse(info.is_installed)
            self.assertIsNone(info.plugin_dir)
            self.assertIsNone(info.global_agents_dir)
            self.assertEqual(info.global_skills, set())
            self.assertEqual(info.global_rules, set())

    def test_detect_global_installation_honors_gemini_config_dir(self):
        fake_config = Path(self.temp_dir) / "fake_gemini_config"
        fake_plugin = fake_config / "plugins" / "my-harness"
        (fake_plugin / "skills" / "custom").mkdir(parents=True)
        (fake_plugin / "skills" / "custom" / "SKILL.md").write_text("custom", encoding="utf-8")

        with patch.dict("os.environ", {"GEMINI_CONFIG_DIR": str(fake_config)}):
            info = harness.detect_global_installation()
            self.assertTrue(info.is_installed)
            self.assertEqual(info.plugin_dir, fake_plugin)
            self.assertIn("custom", info.global_skills)

    def test_detect_global_installation_plugin(self):
        mock_home = Path(self.temp_dir) / "home_with_plugin"
        plugin_dir = mock_home / ".gemini" / "config" / "plugins" / "my-harness"
        plugin_skills = plugin_dir / "skills"
        (plugin_skills / "code-review").mkdir(parents=True)
        (plugin_skills / "code-review" / "SKILL.md").write_text("skill: code-review", encoding="utf-8")
        (plugin_skills / "specify").mkdir(parents=True)
        (plugin_skills / "specify" / "SKILL.md").write_text("skill: specify", encoding="utf-8")

        plugin_rules = plugin_dir / "rules"
        plugin_rules.mkdir(parents=True)
        (plugin_rules / "AGENTS.md").write_text("canonical rules", encoding="utf-8")

        with patch("pathlib.Path.home", return_value=mock_home):
            info = harness.detect_global_installation()
            self.assertTrue(info.is_installed)
            self.assertEqual(info.plugin_dir, plugin_dir)
            self.assertIn("code-review", info.global_skills)
            self.assertIn("specify", info.global_skills)
            self.assertIn("AGENTS.md", info.global_rules)
            # When plugin has AGENTS.md, template rules (shift-left-quality.md, etc.) are also considered covered
            self.assertIn("shift-left-quality.md", info.global_rules)

    def test_detect_global_installation_agents_dir(self):
        mock_home = Path(self.temp_dir) / "home_with_agents"
        agents_dir = mock_home / ".agents"
        skills_dir = agents_dir / "skills"
        (skills_dir / "commit").mkdir(parents=True)
        (skills_dir / "commit" / "SKILL.md").write_text("skill: commit", encoding="utf-8")

        rules_dir = agents_dir / "rules"
        rules_dir.mkdir(parents=True)
        (rules_dir / "review-rules.md").write_text("review rules", encoding="utf-8")

        with patch("pathlib.Path.home", return_value=mock_home):
            info = harness.detect_global_installation()
            self.assertTrue(info.is_installed)
            self.assertEqual(info.global_agents_dir, agents_dir)
            self.assertIn("commit", info.global_skills)
            self.assertIn("review-rules.md", info.global_rules)

    def test_deduplicate_removes_matching_skills_and_rules(self):
        project_agents = Path(self.temp_dir) / "project_agents"
        skills_dir = project_agents / "skills"
        rules_dir = project_agents / "rules"
        (skills_dir / "code-review").mkdir(parents=True)
        (skills_dir / "code-review" / "SKILL.md").write_text("cr", encoding="utf-8")
        (skills_dir / "specify").mkdir(parents=True)
        (skills_dir / "specify" / "SKILL.md").write_text("spec", encoding="utf-8")

        rules_dir.mkdir(parents=True)
        (rules_dir / "shift-left-quality.md").write_text("rule", encoding="utf-8")

        global_info = harness.GlobalInstallationInfo(
            is_installed=True,
            global_skills={"code-review", "specify"},
            global_rules={"shift-left-quality.md", "review-rules.md"}
        )

        res = harness.deduplicate_project_scope(project_agents, global_info, dry_run=False)
        self.assertEqual(set(res["removed_skills"]), {"code-review", "specify"})
        self.assertEqual(set(res["removed_rules"]), {"shift-left-quality.md"})
        self.assertFalse((skills_dir / "code-review").exists())
        self.assertFalse((skills_dir / "specify").exists())
        self.assertFalse((rules_dir / "shift-left-quality.md").exists())
        # The skills and rules directory themselves should remain existing
        self.assertTrue(skills_dir.exists())
        self.assertTrue(rules_dir.exists())

    def test_deduplicate_preserves_custom_skills_and_rules(self):
        project_agents = Path(self.temp_dir) / "project_custom_agents"
        skills_dir = project_agents / "skills"
        rules_dir = project_agents / "rules"
        (skills_dir / "code-review").mkdir(parents=True)
        (skills_dir / "code-review" / "SKILL.md").write_text("cr", encoding="utf-8")
        (skills_dir / "my-custom-tool").mkdir(parents=True)
        (skills_dir / "my-custom-tool" / "SKILL.md").write_text("custom", encoding="utf-8")

        rules_dir.mkdir(parents=True)
        (rules_dir / "shift-left-quality.md").write_text("rule", encoding="utf-8")
        (rules_dir / "project-conventions.md").write_text("conventions", encoding="utf-8")

        global_info = harness.GlobalInstallationInfo(
            is_installed=True,
            global_skills={"code-review"},
            global_rules={"shift-left-quality.md"}
        )

        res = harness.deduplicate_project_scope(project_agents, global_info, dry_run=False)
        self.assertIn("code-review", res["removed_skills"])
        self.assertNotIn("my-custom-tool", res["removed_skills"])
        self.assertIn("my-custom-tool", res["preserved_skills"])

        self.assertIn("shift-left-quality.md", res["removed_rules"])
        self.assertNotIn("project-conventions.md", res["removed_rules"])
        self.assertIn("project-conventions.md", res["preserved_rules"])

        self.assertFalse((skills_dir / "code-review").exists())
        self.assertTrue((skills_dir / "my-custom-tool").exists())
        self.assertFalse((rules_dir / "shift-left-quality.md").exists())
        self.assertTrue((rules_dir / "project-conventions.md").exists())

    def test_deduplicate_dry_run(self):
        project_agents = Path(self.temp_dir) / "project_dry_run"
        skills_dir = project_agents / "skills"
        (skills_dir / "code-review").mkdir(parents=True)
        (skills_dir / "code-review" / "SKILL.md").write_text("cr", encoding="utf-8")

        rules_dir = project_agents / "rules"
        rules_dir.mkdir(parents=True)
        (rules_dir / "shift-left-quality.md").write_text("rule", encoding="utf-8")

        global_info = harness.GlobalInstallationInfo(
            is_installed=True,
            global_skills={"code-review"},
            global_rules={"shift-left-quality.md"}
        )

        res = harness.deduplicate_project_scope(project_agents, global_info, dry_run=True)
        self.assertIn("code-review", res["removed_skills"])
        self.assertIn("shift-left-quality.md", res["removed_rules"])
        # In dry run, files must NOT be deleted
        self.assertTrue((skills_dir / "code-review").exists())
        self.assertTrue((rules_dir / "shift-left-quality.md").exists())

    def test_repair_project_missing_dirs_and_scripts(self):
        project_dir = Path(self.temp_dir) / "repair_project"
        project_agents = project_dir / ".agents"
        project_agents.mkdir(parents=True)
        template_agents = harness.get_harness_root() / "template" / ".agents"

        # Repair structure
        struct_res = harness.repair_project_structure(project_agents, dry_run=False)
        self.assertIn("PRPs/plans", struct_res["created_dirs"])
        self.assertTrue((project_agents / "PRPs" / "plans").exists())
        self.assertTrue((project_agents / "logs").exists())
        self.assertTrue((project_agents / "reviews").exists())

        # Repair scripts
        scripts_res = harness.repair_project_scripts(project_agents, template_agents, dry_run=False)
        self.assertIn("verify_shift_left.py", scripts_res["restored_scripts"])
        self.assertTrue((project_agents / "scripts" / "verify_shift_left.py").exists())
        self.assertTrue((project_agents / "scripts" / "shift_left_hook.py").exists())

    def test_repair_project_configs(self):
        project_dir = Path(self.temp_dir) / "repair_configs_project"
        project_agents = project_dir / ".agents"
        project_agents.mkdir(parents=True)
        (project_dir / "package.json").write_text('{"scripts": {"test": "npm test"}}', encoding="utf-8")
        template_agents = harness.get_harness_root() / "template" / ".agents"

        # Missing configs
        cfg_res = harness.repair_project_configs(project_dir, project_agents, template_agents, dry_run=False)
        self.assertIn("harness.config.json", cfg_res["repaired_configs"])
        self.assertIn("hooks.json", cfg_res["repaired_configs"])
        self.assertTrue((project_agents / "harness.config.json").exists())
        self.assertTrue((project_agents / "hooks.json").exists())

        import json
        cfg = json.loads((project_agents / "harness.config.json").read_text(encoding="utf-8"))
        self.assertEqual(cfg["project_name"], "repair_configs_project")
        self.assertEqual(cfg["commands"]["test"], "npm test")

    def test_parser_fix_args(self):
        parser = harness.build_parser()
        args = parser.parse_args(["fix", "my_app", "--dry-run"])
        self.assertEqual(args.target, "my_app")
        self.assertTrue(args.dry_run)

        args_default = parser.parse_args(["fix"])
        self.assertEqual(args_default.target, ".")
        self.assertFalse(args_default.dry_run)

    def test_cmd_fix_e2e_execution(self):
        mock_home = Path(self.temp_dir) / "e2e_home"
        plugin_dir = mock_home / ".gemini" / "config" / "plugins" / "my-harness"
        (plugin_dir / "skills" / "code-review").mkdir(parents=True)
        (plugin_dir / "skills" / "code-review" / "SKILL.md").write_text("skill", encoding="utf-8")
        (plugin_dir / "rules").mkdir(parents=True)
        (plugin_dir / "rules" / "AGENTS.md").write_text("rules", encoding="utf-8")

        project_dir = Path(self.temp_dir) / "e2e_project"
        project_agents = project_dir / ".agents"
        project_agents.mkdir(parents=True)
        # Duplicate skill and rule
        (project_agents / "skills" / "code-review").mkdir(parents=True)
        (project_agents / "skills" / "code-review" / "SKILL.md").write_text("duplicate", encoding="utf-8")
        # Custom skill
        (project_agents / "skills" / "my-own-skill").mkdir(parents=True)
        (project_agents / "skills" / "my-own-skill" / "SKILL.md").write_text("custom", encoding="utf-8")
        # Duplicate rule
        (project_agents / "rules").mkdir(parents=True)
        (project_agents / "rules" / "shift-left-quality.md").write_text("rule", encoding="utf-8")

        args = MagicMock()
        args.target = str(project_dir)
        args.dry_run = False

        with patch("pathlib.Path.home", return_value=mock_home):
            ret = harness.cmd_fix(args)
            self.assertEqual(ret, 0)

            # Check that structure and scripts are repaired
            self.assertTrue((project_agents / "PRPs" / "plans").exists())
            self.assertTrue((project_agents / "scripts" / "verify_shift_left.py").exists())
            self.assertTrue((project_agents / "harness.config.json").exists())

            # Check deduplication
            self.assertFalse((project_agents / "skills" / "code-review").exists())
            self.assertTrue((project_agents / "skills" / "my-own-skill").exists())
            self.assertFalse((project_agents / "rules" / "shift-left-quality.md").exists())

    def test_doctor_warns_on_duplicates(self):
        import io
        mock_home = Path(self.temp_dir) / "doc_home"
        plugin_dir = mock_home / ".gemini" / "config" / "plugins" / "my-harness"
        (plugin_dir / "skills" / "code-review").mkdir(parents=True)
        (plugin_dir / "skills" / "code-review" / "SKILL.md").write_text("skill", encoding="utf-8")

        project_dir = Path(self.temp_dir) / "doc_project"
        project_agents = project_dir / ".agents"
        # Setup basic directories so doctor passes structure checks
        harness.repair_project_structure(project_agents, dry_run=False)
        (project_agents / "skills" / "code-review").mkdir(parents=True)
        (project_agents / "skills" / "code-review" / "SKILL.md").write_text("dup", encoding="utf-8")
        template_agents = harness.get_harness_root() / "template" / ".agents"
        harness.repair_project_scripts(project_agents, template_agents, dry_run=False)
        harness.repair_project_configs(project_dir, project_agents, template_agents, dry_run=False)

        args = MagicMock()
        args.target = str(project_dir)

        captured_out = io.StringIO()
        with patch("pathlib.Path.home", return_value=mock_home), \
             patch("sys.stdout", captured_out):
            harness.cmd_doctor(args)

        output = captured_out.getvalue()
        self.assertIn("duplicate", output.lower())
        self.assertIn("harness fix", output)





if __name__ == "__main__":
    unittest.main()

import importlib.util
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import harness

REPO_ROOT = Path(__file__).resolve().parent.parent


def _load_gh_project():
    script_path = REPO_ROOT / ".agents" / "scripts" / "gh_project.py"
    if not script_path.exists():
        raise FileNotFoundError(f"Missing script: {script_path}")
    spec = importlib.util.spec_from_file_location("gh_project", str(script_path))
    mod = importlib.util.module_from_spec(spec)
    sys.modules["gh_project"] = mod
    spec.loader.exec_module(mod)
    return mod


class TestGhProjectScript(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.addCleanup(lambda: shutil.rmtree(self.temp_dir, ignore_errors=True))
        self.repo_root = REPO_ROOT

    def test_gh_project_script_exists_and_has_parity(self):
        agent_script = self.repo_root / ".agents" / "scripts" / "gh_project.py"
        tmpl_script = self.repo_root / "template" / ".agents" / "scripts" / "gh_project.py"
        root_script = self.repo_root / "scripts" / "gh_project.py"

        self.assertTrue(agent_script.exists(), ".agents/scripts/gh_project.py must exist")
        self.assertTrue(tmpl_script.exists(), "template/.agents/scripts/gh_project.py must exist")
        self.assertTrue(root_script.exists(), "scripts/gh_project.py must exist")

        agent_text = agent_script.read_text(encoding="utf-8")
        self.assertEqual(agent_text, tmpl_script.read_text(encoding="utf-8"))
        self.assertEqual(agent_text, root_script.read_text(encoding="utf-8"))

    def test_calculate_iteration_end_date(self):
        gh_project = _load_gh_project()
        self.assertEqual(gh_project.calculate_iteration_end_date("2026-11-01", 14), "2026-11-14")
        self.assertEqual(gh_project.calculate_iteration_end_date("2026-02-20", 14), "2026-03-05")

    def test_parse_project_metadata(self):
        gh_project = _load_gh_project()
        sample_node = {
            "id": "PVT_kwDOABC123",
            "title": "Engineering Roadmap",
            "number": 7,
            "fields": {
                "nodes": [
                    {
                        "id": "PVTSSF_status",
                        "name": "Status",
                        "dataType": "SINGLE_SELECT",
                        "options": [
                            {"id": "opt_todo", "name": "Todo"},
                            {"id": "opt_prog", "name": "In Progress"},
                            {"id": "opt_done", "name": "Done"},
                        ],
                    },
                    {
                        "id": "PVTSSF_prio",
                        "name": "Priority",
                        "dataType": "SINGLE_SELECT",
                        "options": [
                            {"id": "opt_p0", "name": "P0 - Critical"},
                            {"id": "opt_p1", "name": "P1 - High"},
                        ],
                    },
                    {
                        "id": "PVTF_start",
                        "name": "Start date",
                        "dataType": "DATE",
                    },
                    {
                        "id": "PVTF_target",
                        "name": "Target date",
                        "dataType": "DATE",
                    },
                    {
                        "id": "PVTIF_sprint",
                        "name": "Sprint",
                        "dataType": "ITERATION",
                        "configuration": {
                            "iterations": [
                                {
                                    "id": "iter_a",
                                    "title": "2026.11.A",
                                    "startDate": "2026-11-01",
                                    "duration": 14,
                                },
                                {
                                    "id": "iter_b",
                                    "title": "2026.11.B",
                                    "startDate": "2026-11-15",
                                    "duration": 14,
                                },
                            ]
                        },
                    },
                ]
            },
        }
        parsed = gh_project.parse_project_metadata(sample_node)
        self.assertEqual(parsed["project_id"], "PVT_kwDOABC123")
        self.assertEqual(parsed["fields"]["Status"]["id"], "PVTSSF_status")
        self.assertEqual(parsed["fields"]["Status"]["options"]["In Progress"], "opt_prog")
        self.assertEqual(parsed["fields"]["Priority"]["options"]["P0 - Critical"], "opt_p0")
        self.assertEqual(parsed["fields"]["Start date"]["id"], "PVTF_start")
        self.assertEqual(parsed["fields"]["Target date"]["id"], "PVTF_target")
        sprints = parsed["fields"]["Sprint"]["iterations"]
        self.assertEqual(sprints["2026.11.A"]["id"], "iter_a")
        self.assertEqual(sprints["2026.11.A"]["endDate"], "2026-11-14")
        self.assertEqual(sprints["2026.11.B"]["endDate"], "2026-11-28")

    def test_compute_epic_date_rollup(self):
        gh_project = _load_gh_project()
        self.assertIsNone(gh_project.compute_epic_date_rollup([]))
        self.assertIsNone(gh_project.compute_epic_date_rollup([(None, None)]))
        rollup = gh_project.compute_epic_date_rollup([
            ("2026-11-15", "2026-11-28"),
            ("2026-11-01", "2026-11-14"),
            ("2026-11-08", "2026-12-05"),
        ])
        self.assertEqual(rollup, {"start_date": "2026-11-01", "target_date": "2026-12-05"})

    def test_check_issue_readiness_clear_and_unclear(self):
        gh_project = _load_gh_project()
        clear_issue = {
            "number": 42,
            "title": "Support exporting sprint metrics",
            "body": (
                "### Parent Epic\n"
                "Part of #10\n\n"
                "### Summary\n"
                "Allow engineering leads to export sprint velocity metrics as JSON.\n\n"
                "### Acceptance Criteria\n"
                "- [ ] Running export outputs valid JSON with sprint totals\n"
                "- [ ] Empty sprints report zero completed points\n\n"
                "### Technical Notes / Dependencies\n"
                "Reuse metrics aggregator in `src/metrics.py`.\n"
            ),
        }
        res_clear = gh_project.check_issue_readiness(clear_issue)
        self.assertTrue(res_clear["is_clear"])
        self.assertEqual(res_clear["epic_ref"], "#10")
        self.assertEqual(res_clear["ac_count"], 2)
        self.assertEqual(res_clear["missing"], [])

        unclear_issue = {
            "number": 43,
            "title": "Improve UI performance",
            "body": (
                "### Summary\n"
                "TBD - make it faster.\n\n"
                "### Acceptance Criteria\n"
                "Needs investigation.\n"
            ),
        }
        res_unclear = gh_project.check_issue_readiness(unclear_issue)
        self.assertFalse(res_unclear["is_clear"])
        self.assertTrue(len(res_unclear["missing"]) > 0)

    def test_format_issue_body(self):
        gh_project = _load_gh_project()
        body = gh_project.format_issue_body(
            summary="Add webhook retry backoff.",
            acceptance_criteria=["Retries up to 3 times", "Logs permanent failure"],
            epic="#10",
            notes="Discovered in PR #88",
        )
        self.assertIn("### Parent Epic\nPart of #10", body)
        self.assertIn("### Summary\nAdd webhook retry backoff.", body)
        self.assertIn("### Acceptance Criteria\n- [ ] Retries up to 3 times\n- [ ] Logs permanent failure", body)
        self.assertIn("### Technical Notes / Dependencies\nDiscovered in PR #88", body)

    def test_load_and_save_project_config(self):
        gh_project = _load_gh_project()
        fake_repo = Path(self.temp_dir) / "repo"
        (fake_repo / ".agents").mkdir(parents=True)
        cfg_file = fake_repo / ".agents" / "harness.config.json"
        cfg_file.write_text(json.dumps({"project_name": "demo"}), encoding="utf-8")

        self.assertEqual(gh_project.load_project_config(fake_repo), {})

        sample_cfg = {"owner": "octocat", "project_number": 3, "project_id": "PVT_123"}
        saved_path = gh_project.save_project_config(fake_repo, sample_cfg)
        self.assertEqual(saved_path, cfg_file)
        loaded_full = json.loads(cfg_file.read_text(encoding="utf-8"))
        self.assertEqual(loaded_full["project_name"], "demo")
        self.assertEqual(gh_project.load_project_config(fake_repo), sample_cfg)


class TestGitHubProjectsSkillsAndWorkflow(unittest.TestCase):
    def setUp(self):
        self.repo_root = REPO_ROOT

    def _assert_pair_identical(self, rel_path: Path):
        proj = self.repo_root / ".agents" / rel_path
        tmpl = self.repo_root / "template" / ".agents" / rel_path
        self.assertTrue(proj.exists(), f"Missing .agents/{rel_path.as_posix()}")
        self.assertTrue(tmpl.exists(), f"Missing template/.agents/{rel_path.as_posix()}")
        self.assertEqual(
            proj.read_text(encoding="utf-8"),
            tmpl.read_text(encoding="utf-8"),
            f".agents/{rel_path.as_posix()} and template/.agents/{rel_path.as_posix()} must be identical",
        )
        return proj.read_text(encoding="utf-8")

    def test_schema_includes_github_project(self):
        schema = json.loads((self.repo_root / "harness.schema.json").read_text(encoding="utf-8"))
        self.assertIn("github_project", schema["properties"])

    def test_github_skills_moved_into_template_and_top_level_removed(self):
        self.assertFalse((self.repo_root / "skills").exists(), "Top-level skills/ should be removed after moving into template")
        setup_text = self._assert_pair_identical(Path("skills") / "github-project-setup" / "SKILL.md")
        backlog_text = self._assert_pair_identical(Path("skills") / "github-backlog-management" / "SKILL.md")

        self.assertIn("gh_project.py sync", setup_text)
        self.assertIn("gh_project.py", backlog_text)
        self.assertIn("check-ready", backlog_text)
        self.assertIn("rollup-epic", backlog_text)
        self.assertIn("Carryover", backlog_text)
        self.assertIn("Depends on", backlog_text)

    def test_specify_supports_issue_and_clear_gate(self):
        text = self._assert_pair_identical(Path("skills") / "specify" / "SKILL.md")
        self.assertIn("gh issue view", text)
        self.assertIn("Clear?", text)
        self.assertIn("check-ready", text)
        self.assertIn("gh issue edit", text)
        self.assertIn("## Specification & Implementation Plan Ready", text)

    def test_prp_plan_and_template_support_github_issue(self):
        plan_skill = self._assert_pair_identical(Path("skills") / "prp-plan" / "SKILL.md")
        plan_tpl = self._assert_pair_identical(Path("skills") / "prp-plan" / "resources" / "plan-template.md")
        self.assertIn("gh issue view", plan_skill)
        self.assertIn("check-ready", plan_skill)
        self.assertIn("GitHub Issue", plan_tpl)
        self.assertIn("Parent Epic", plan_tpl)

    def test_implement_and_report_template_support_merge_close_and_known_issues(self):
        impl_text = self._assert_pair_identical(Path("skills") / "implement" / "SKILL.md")
        report_tpl = self._assert_pair_identical(Path("skills") / "implement" / "resources" / "report-template.md")

        self.assertIn("In Progress", impl_text)
        self.assertIn("set-status", impl_text)
        self.assertIn("## Phase 9 — MERGE, CLOSE ISSUE & FOLLOW-UP TRIAGE", impl_text)
        self.assertIn("gh pr merge", impl_text)
        self.assertIn("gh issue create", impl_text)
        self.assertIn("rollup-epic", impl_text)
        self.assertIn("## Known Issues & Follow-Up Tickets", report_tpl)

    def test_pr_skill_supports_merge_close_and_followup_triage(self):
        pr_text = self._assert_pair_identical(Path("skills") / "pr" / "SKILL.md")
        self.assertIn("Phase 7 — MERGE, CLOSE ISSUE & FOLLOW-UP TRIAGE", pr_text)
        self.assertIn("gh pr merge", pr_text)
        self.assertIn("gh issue create", pr_text)
        self.assertIn("set-status", pr_text)

    def test_deduplicate_protects_harness_source_repo(self):
        temp_dir = tempfile.mkdtemp()
        self.addCleanup(lambda: shutil.rmtree(temp_dir, ignore_errors=True))
        fake_root = Path(temp_dir) / "harness_repo"
        harness_agents = fake_root / ".agents"
        (harness_agents / "skills" / "implement").mkdir(parents=True)
        (harness_agents / "skills" / "implement" / "SKILL.md").write_text("impl", encoding="utf-8")
        (harness_agents / "rules").mkdir(parents=True)
        (harness_agents / "rules" / "shift-left-quality.md").write_text("rule", encoding="utf-8")

        fake_global = harness.GlobalInstallationInfo(
            is_installed=True,
            global_skills={"code-review", "specify", "implement"},
            global_rules={"shift-left-quality.md", "review-rules.md"},
        )
        with patch.object(harness, "get_harness_root", return_value=fake_root):
            res = harness.deduplicate_project_scope(harness_agents, fake_global, dry_run=False)
        self.assertEqual(res["removed_skills"], [])
        self.assertEqual(res["removed_rules"], [])
        self.assertTrue((harness_agents / "skills" / "implement" / "SKILL.md").exists())
        self.assertTrue((harness_agents / "rules" / "shift-left-quality.md").exists())

        real_agents = harness.get_harness_root() / ".agents"
        real_res = harness.deduplicate_project_scope(real_agents, fake_global, dry_run=True)
        self.assertEqual(real_res["removed_skills"], [])
        self.assertEqual(real_res["removed_rules"], [])


if __name__ == "__main__":
    unittest.main()

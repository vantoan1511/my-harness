import unittest
from pathlib import Path


class TestImplementSkill(unittest.TestCase):
    def setUp(self):
        self.repo_root = Path(__file__).resolve().parent.parent
        self.project_skill_dir = self.repo_root / ".agents" / "skills" / "implement"
        self.template_skill_dir = self.repo_root / "template" / ".agents" / "skills" / "implement"
        self.agents_md = self.repo_root / "AGENTS.md"
        self.template_agents_md = self.repo_root / "template" / "AGENTS.md.template"

    def test_implement_skills_and_templates_exist(self):
        self.assertTrue((self.project_skill_dir / "SKILL.md").exists(), "Project implement SKILL.md must exist")
        self.assertTrue((self.template_skill_dir / "SKILL.md").exists(), "Template implement SKILL.md must exist")
        self.assertTrue(
            (self.project_skill_dir / "resources" / "report-template.md").exists(),
            "Project report-template.md must exist",
        )
        self.assertTrue(
            (self.template_skill_dir / "resources" / "report-template.md").exists(),
            "Template report-template.md must exist",
        )

    def test_implement_files_are_identical(self):
        rel_files = [
            Path("SKILL.md"),
            Path("resources") / "report-template.md",
        ]
        for rel in rel_files:
            proj_text = (self.project_skill_dir / rel).read_text(encoding="utf-8")
            tmpl_text = (self.template_skill_dir / rel).read_text(encoding="utf-8")
            self.assertEqual(proj_text, tmpl_text, f"Project and template {rel} must be byte-for-byte identical")

    def test_implement_skill_has_phase_4_5_review_adapt_loop(self):
        for skill_path in [self.project_skill_dir / "SKILL.md", self.template_skill_dir / "SKILL.md"]:
            content = skill_path.read_text(encoding="utf-8")
            self.assertIn("## Phase 4.5 — REVIEW, SIMPLIFY & ADAPT", content)
            self.assertIn("Fresh-Context Critic Subagent", content)
            self.assertIn("invoke_subagent", content)
            self.assertIn("CRITICAL", content)
            self.assertIn("HIGH", content)
            self.assertIn("MEDIUM", content)
            self.assertIn("simplifier", content)
            self.assertIn("Bounded Convergence", content)
            self.assertIn("Max 2 Passes", content)
            self.assertIn("REVIEW_ADAPT_PASS", content)

    def test_report_template_has_self_review_log(self):
        for tpl_path in [
            self.project_skill_dir / "resources" / "report-template.md",
            self.template_skill_dir / "resources" / "report-template.md",
        ]:
            content = tpl_path.read_text(encoding="utf-8")
            self.assertIn("## Self-Review & Adaptation Log", content)
            self.assertIn("Self-Review & Adapt", content)

    def test_agents_md_documents_review_adapt_in_implement(self):
        for md_path in [self.agents_md, self.template_agents_md]:
            content = md_path.read_text(encoding="utf-8")
            self.assertIn("Phase 3 — Implement", content)
            self.assertTrue(
                "review" in content.lower() and "adapt" in content.lower(),
                f"{md_path} Phase 3 must document review and adaptation loop",
            )


if __name__ == "__main__":
    unittest.main()

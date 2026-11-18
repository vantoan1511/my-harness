import unittest
from pathlib import Path

class TestSpecifyHandoffFormat(unittest.TestCase):
    def setUp(self):
        self.repo_root = Path(__file__).resolve().parent.parent
        self.project_skill = self.repo_root / ".agents" / "skills" / "specify" / "SKILL.md"
        self.template_skill = self.repo_root / "template" / ".agents" / "skills" / "specify" / "SKILL.md"

    def test_specify_skills_exist(self):
        self.assertTrue(self.project_skill.exists(), "Project specify SKILL.md must exist")
        self.assertTrue(self.template_skill.exists(), "Template specify SKILL.md must exist")

    def test_specify_skills_are_identical(self):
        project_content = self.project_skill.read_text(encoding="utf-8")
        template_content = self.template_skill.read_text(encoding="utf-8")
        self.assertEqual(project_content, template_content, "Project and template specify SKILL.md must be byte-for-byte identical")

    def test_specify_handoff_has_markdown_headers_and_bullets(self):
        for path in [self.project_skill, self.template_skill]:
            content = path.read_text(encoding="utf-8")
            self.assertIn("## Specification & Implementation Plan Ready", content, f"{path} must contain ## Specification & Implementation Plan Ready")
            self.assertIn("### Contracts Defined", content, f"{path} must contain ### Contracts Defined")
            self.assertIn("### Summary of Decisions", content, f"{path} must contain ### Summary of Decisions")
            self.assertIn("- **Feature**:", content, f"{path} must contain bulleted - **Feature**:")
            self.assertIn("- **Spec**:", content, f"{path} must contain bulleted - **Spec**:")
            self.assertIn("- **Plan**:", content, f"{path} must contain bulleted - **Plan**:")
            self.assertIn("- **Test Strategy**:", content, f"{path} must contain bulleted - **Test Strategy**:")
            self.assertIn("> **Recommended Next Step (Clean Context & Low Effort)**:", content, f"{path} must contain Recommended Next Step header")
            self.assertIn("```text\n> /implement @.agents/PRPs/plans/{name}.plan.md\n> ```", content, f"{path} must contain copyable code block for /implement")

    def test_specify_asks_about_auto_create_pr_and_target_branch(self):
        for path in [self.project_skill, self.template_skill]:
            content = path.read_text(encoding="utf-8")
            self.assertIn("git branch --show-current", content)
            self.assertIn("Branch Name", content)
            self.assertIn("Auto-Create PR", content)
            self.assertIn("Seamless Mode", content)
            self.assertIn("Base Branch", content)
            self.assertIn("PR Target Branch", content)
            self.assertIn("Delivery & PR Preferences", content)

    def test_plan_template_has_auto_create_pr_and_base_branch_metadata(self):
        proj_tpl = self.repo_root / ".agents" / "skills" / "prp-plan" / "resources" / "plan-template.md"
        tmpl_tpl = self.repo_root / "template" / ".agents" / "skills" / "prp-plan" / "resources" / "plan-template.md"
        self.assertEqual(
            proj_tpl.read_text(encoding="utf-8"),
            tmpl_tpl.read_text(encoding="utf-8"),
            "Project and template plan-template.md must be byte-for-byte identical",
        )
        for tpl in [proj_tpl, tmpl_tpl]:
            content = tpl.read_text(encoding="utf-8")
            self.assertIn("- **Branch Name**:", content)
            self.assertIn("- **Auto-Create PR**:", content)
            self.assertIn("- **Base Branch**:", content)

if __name__ == "__main__":
    unittest.main()

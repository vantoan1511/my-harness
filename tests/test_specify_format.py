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
            self.assertIn("Next Step: Run /implement .agents/PRPs/plans/{name}.plan.md to begin test-driven implementation.", content, f"{path} must contain Next Step handoff trigger")

if __name__ == "__main__":
    unittest.main()

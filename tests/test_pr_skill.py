import unittest
from pathlib import Path


class TestPrSkill(unittest.TestCase):
    def setUp(self):
        self.repo_root = Path(__file__).resolve().parent.parent
        self.project_skill = self.repo_root / ".agents" / "skills" / "pr" / "SKILL.md"
        self.template_skill = self.repo_root / "template" / ".agents" / "skills" / "pr" / "SKILL.md"

    def test_pr_skills_exist_and_are_identical(self):
        self.assertTrue(self.project_skill.exists(), "Project pr SKILL.md must exist")
        self.assertTrue(self.template_skill.exists(), "Template pr SKILL.md must exist")
        self.assertEqual(
            self.project_skill.read_text(encoding="utf-8"),
            self.template_skill.read_text(encoding="utf-8"),
            "Project and template pr SKILL.md must be byte-for-byte identical",
        )

    def test_pr_skill_discovers_and_links_issues_across_non_default_base(self):
        for skill_path in [self.project_skill, self.template_skill]:
            content = skill_path.read_text(encoding="utf-8")
            self.assertIn("GitHub Issue", content)
            self.assertIn("closingIssuesReferences", content)
            self.assertIn("defaultBranchRef", content)
            self.assertIn("gh issue comment", content)
            self.assertIn("gh issue close", content)


if __name__ == "__main__":
    unittest.main()

import importlib.util
import unittest
from pathlib import Path


class TestCodeReviewSkill(unittest.TestCase):
    def setUp(self):
        self.repo_root = Path(__file__).resolve().parent.parent
        self.project_skill_dir = self.repo_root / ".agents" / "skills" / "code-review"
        self.template_skill_dir = self.repo_root / "template" / ".agents" / "skills" / "code-review"

    def test_code_review_skills_exist(self):
        self.assertTrue((self.project_skill_dir / "SKILL.md").exists(), "Project code-review SKILL.md must exist")
        self.assertTrue((self.template_skill_dir / "SKILL.md").exists(), "Template code-review SKILL.md must exist")

    def test_code_review_files_are_identical(self):
        rel_files = [
            Path("SKILL.md"),
            Path("evals") / "eval_specs.json",
            Path("evals") / "run_evals.py",
        ]
        for rel in rel_files:
            proj_text = (self.project_skill_dir / rel).read_text(encoding="utf-8")
            tmpl_text = (self.template_skill_dir / rel).read_text(encoding="utf-8")
            self.assertEqual(proj_text, tmpl_text, f"Project and template {rel} must be byte-for-byte identical")

    def test_code_review_evals_pass(self):
        eval_runner = self.project_skill_dir / "evals" / "run_evals.py"
        spec = importlib.util.spec_from_file_location("run_evals", str(eval_runner))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        for skill_dir in (self.project_skill_dir, self.template_skill_dir):
            spec_path = skill_dir / "evals" / "eval_specs.json"
            self.assertTrue(
                mod.run_evals(spec_path),
                f"Skill evaluation suite failed for {spec_path}",
            )


if __name__ == "__main__":
    unittest.main()

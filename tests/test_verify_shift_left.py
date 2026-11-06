import unittest
import tempfile
import shutil
from pathlib import Path
import sys

# Add .agents/scripts to sys.path so we can import verify_shift_left directly
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / ".agents" / "scripts"))

import verify_shift_left

class TestVerifyShiftLeftStructuralComplexity(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.addCleanup(lambda: shutil.rmtree(self.temp_dir, ignore_errors=True))
        self.temp_path = Path(self.temp_dir)

    def test_python_function_under_limits_passes(self):
        code = (
            "def small_func(x):\n"
            "    if x > 0:\n"
            "        return x * 2\n"
            "    return 0\n"
        )
        file_path = self.temp_path / "mod.py"
        file_path.write_text(code, encoding="utf-8")
        violations = verify_shift_left.check_structural_complexity(file_path, code, {"enabled": True})
        self.assertEqual(len(violations), 0)

    def test_python_function_over_50_lines_fails(self):
        # 55 lines
        lines = ["def long_func():"]
        for i in range(54):
            lines.append(f"    a_{i} = {i}")
        code = "\n".join(lines) + "\n"
        file_path = self.temp_path / "long.py"
        file_path.write_text(code, encoding="utf-8")
        violations = verify_shift_left.check_structural_complexity(file_path, code, {"enabled": True})
        self.assertEqual(len(violations), 1)
        self.assertIn("long_func", violations[0].rule)
        self.assertIn("55 lines", violations[0].rule)
        self.assertIn("exceeds limit 50", violations[0].rule)

    def test_python_nesting_over_4_levels_fails(self):
        # 5 levels of control flow inside function
        code = (
            "def deeply_nested(x):\n"
            "    if x > 0:\n"                 # 1
            "        for i in range(x):\n"        # 2
            "            while i > 0:\n"          # 3
            "                try:\n"              # 4
            "                    if i == 1:\n"    # 5 (violates max 4)
            "                        pass\n"
            "                except Exception:\n"
            "                    pass\n"
        )
        file_path = self.temp_path / "nested.py"
        file_path.write_text(code, encoding="utf-8")
        violations = verify_shift_left.check_structural_complexity(file_path, code, {"enabled": True})
        self.assertEqual(len(violations), 1)
        self.assertIn("deeply_nested", violations[0].rule)
        self.assertIn("nesting depth 5", violations[0].rule)
        self.assertIn("exceeds limit 4", violations[0].rule)

    def test_structural_check_respects_shift_left_ignore(self):
        lines = ["def ignored_func():  # shift-left-ignore"]
        for i in range(54):
            lines.append(f"    a_{i} = {i}")
        code = "\n".join(lines) + "\n"
        file_path = self.temp_path / "ignored.py"
        file_path.write_text(code, encoding="utf-8")
        violations = verify_shift_left.check_structural_complexity(file_path, code, {"enabled": True})
        self.assertEqual(len(violations), 0)

    def test_structural_check_respects_disabled_and_exclude(self):
        lines = ["def long_func():"]
        for i in range(54):
            lines.append(f"    a_{i} = {i}")
        code = "\n".join(lines) + "\n"

        file_path = self.temp_path / "tests" / "test_mod.py"
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(code, encoding="utf-8")

        # Excluded by default path_exclude ("tests/", "test_")
        violations = verify_shift_left.check_structural_complexity(file_path, code, {"enabled": True})
        self.assertEqual(len(violations), 0)

        # Disabled explicitly
        other_path = self.temp_path / "src" / "mod.py"
        other_path.parent.mkdir(parents=True, exist_ok=True)
        other_path.write_text(code, encoding="utf-8")
        violations_disabled = verify_shift_left.check_structural_complexity(
            other_path, code, {"enabled": False}
        )
        self.assertEqual(len(violations_disabled), 0)

    def test_brace_language_structural_complexity(self):
        # TypeScript / Rust brace nesting
        code = (
            "function testTs(a) {\n"
            "  if (a > 0) {\n"            # 1
            "    for (let i = 0; i < a; i++) {\n" # 2
            "      while (i > 1) {\n"     # 3
            "        try {\n"             # 4
            "          if (i === 2) {\n"  # 5
            "            console.log(i);\n"
            "          }\n"
            "        } catch (e) {}\n"
            "      }\n"
            "    }\n"
            "  }\n"
            "}\n"
        )
        file_path = self.temp_path / "service.ts"
        file_path.write_text(code, encoding="utf-8")
        violations = verify_shift_left.check_structural_complexity(file_path, code, {"enabled": True})
        self.assertEqual(len(violations), 1)
        self.assertIn("nesting depth", violations[0].rule)

    def test_template_parity_verify_shift_left(self):
        root_script = REPO_ROOT / ".agents" / "scripts" / "verify_shift_left.py"
        tmpl_script = REPO_ROOT / "template" / ".agents" / "scripts" / "verify_shift_left.py"
        self.assertEqual(
            root_script.read_text(encoding="utf-8"),
            tmpl_script.read_text(encoding="utf-8"),
            "verify_shift_left.py must be byte-for-byte identical with template"
        )

if __name__ == "__main__":
    unittest.main()

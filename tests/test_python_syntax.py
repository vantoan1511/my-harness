import ast
import unittest
from pathlib import Path

IGNORE_DIRS = {
    ".git",
    ".venv",
    "venv",
    "env",
    "build",
    "dist",
    "__pycache__",
    ".pytest_cache",
    ".eggs",
    "install_sandbox",
    "simulated_external_project",
}


class TestPythonSyntax(unittest.TestCase):
    def setUp(self):
        self.repo_root = Path(__file__).resolve().parent.parent

    def _get_python_files(self):
        files = []
        for p in self.repo_root.rglob("*.py"):
            parts = set(p.relative_to(self.repo_root).parts)
            if parts.intersection(IGNORE_DIRS):
                continue
            if any(part.endswith(".egg-info") for part in parts):
                continue
            files.append(p)
        return files

    def test_python_compatibility_syntax(self):
        errors = []
        for file_path in self._get_python_files():
            try:
                content = file_path.read_text(encoding="utf-8")
            except Exception as e:
                errors.append(f"{file_path}: Failed to read file: {e}")
                continue

            # 1. Parse AST to detect any syntax errors (e.g. if run on Python 3.10/3.11)
            try:
                tree = ast.parse(content, filename=str(file_path))
            except SyntaxError as e:
                errors.append(f"{file_path}:{e.lineno}:{e.offset} SyntaxError: {e.msg}")
                continue

            # 2. Inspect f-string expressions for PEP 701 incompatibility
            # Python < 3.12 raised SyntaxError: f-string expression part cannot include a backslash
            for node in ast.walk(tree):
                if isinstance(node, ast.FormattedValue):
                    seg = ast.get_source_segment(content, node.value)
                    if seg is None:
                        seg = ast.get_source_segment(content, node)
                    if seg and "\\" in seg:
                        lineno = getattr(node.value, "lineno", getattr(node, "lineno", 0))
                        col = getattr(node.value, "col_offset", getattr(node, "col_offset", 0))
                        rel_path = file_path.relative_to(self.repo_root)
                        errors.append(
                            f"{rel_path}:{lineno}:{col} "
                            f"f-string expression contains backslash (PEP 701 incompatible with Python < 3.12): {seg!r}"
                        )

        if errors:
            self.fail(
                f"Found {len(errors)} syntax / compatibility issue(s):\n"
                + "\n".join(f"  - {err}" for err in errors)
            )


if __name__ == "__main__":
    unittest.main()

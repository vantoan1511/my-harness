import unittest
from pathlib import Path

class TestPackagingConfiguration(unittest.TestCase):
    def setUp(self):
        self.repo_root = Path(__file__).resolve().parent.parent
        self.pyproject = self.repo_root / "pyproject.toml"
        self.setup_py = self.repo_root / "setup.py"
        self.manifest = self.repo_root / "MANIFEST.in"

    def test_manifest_in_exists_and_includes_assets(self):
        self.assertTrue(self.manifest.exists(), "MANIFEST.in must exist to bundle assets in sdist")
        content = self.manifest.read_text(encoding="utf-8")
        self.assertIn("recursive-include template", content)
        self.assertIn("recursive-include packs", content)
        self.assertIn("recursive-include scripts", content)
        self.assertIn("recursive-include assets", content)

    def test_pyproject_includes_package_data(self):
        content = self.pyproject.read_text(encoding="utf-8")
        self.assertIn("package-data", content)

    def test_setup_py_includes_package_data(self):
        content = self.setup_py.read_text(encoding="utf-8")
        self.assertIn("include_package_data=True", content)

if __name__ == "__main__":
    unittest.main()

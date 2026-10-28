import unittest
import importlib.util
from pathlib import Path

def load_tests(loader, standard_tests, pattern):
    test_file = (
        Path(__file__).resolve().parent.parent
        / "template"
        / ".agents"
        / "skills"
        / "pr-changelog"
        / "scripts"
        / "tests"
        / "test_generate_changelog.py"
    )
    if test_file.exists():
        spec = importlib.util.spec_from_file_location("test_generate_changelog", str(test_file))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        for attr in dir(mod):
            val = getattr(mod, attr)
            if isinstance(val, type) and issubclass(val, unittest.TestCase):
                standard_tests.addTests(loader.loadTestsFromTestCase(val))
    return standard_tests

if __name__ == "__main__":
    unittest.main()

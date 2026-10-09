import unittest
import tempfile
import shutil
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

import harness

class TestHarnessInitScope(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.addCleanup(lambda: shutil.rmtree(self.temp_dir, ignore_errors=True))

    def test_parse_args_default_scope(self):
        with patch.object(sys, "argv", ["harness.py", "init"]):
            parser = harness.build_parser() if hasattr(harness, "build_parser") else None
            if parser is None:
                # If main() builds parser internally, test via parser created like in harness.py
                import argparse
                # We expect harness to expose build_parser or parser
                # Let's check harness.build_parser
                self.fail("harness.py should provide build_parser() for testability")
            args = parser.parse_args(["init"])
            self.assertEqual(args.scope, "project")

    def test_parse_args_explicit_scopes(self):
        if not hasattr(harness, "build_parser"):
            self.fail("harness.py should provide build_parser()")
        parser = harness.build_parser()
        args_proj = parser.parse_args(["init", "--scope", "project"])
        self.assertEqual(args_proj.scope, "project")

        args_global = parser.parse_args(["init", "--scope", "global"])
        self.assertEqual(args_global.scope, "global")

    def test_cmd_init_project_scope(self):
        target = Path(self.temp_dir) / "my_project"
        target.mkdir()

        args = MagicMock()
        args.target = str(target)
        args.scope = "project"
        args.preset = "universal"
        args.pack = None

        harness.cmd_init(args)

        self.assertTrue((target / ".agents").exists())
        self.assertTrue((target / ".agents" / "harness.config.json").exists())

    def test_cmd_init_global_scope(self):
        mock_home = Path(self.temp_dir) / "mock_home"
        mock_home.mkdir()

        args = MagicMock()
        args.target = "."
        args.scope = "global"
        args.preset = "universal"
        args.pack = None

        with patch("pathlib.Path.home", return_value=mock_home), \
             patch("subprocess.run") as mock_subproc:
            mock_subproc.return_value = MagicMock(returncode=0)
            harness.cmd_init(args)

            self.assertTrue((mock_home / ".agents").exists())
            self.assertTrue((mock_home / ".agents" / "harness.config.json").exists())
            # Should have called pip install -e
            pip_calls = [
                call for call in mock_subproc.call_args_list
                if any("pip" in str(arg) for arg in call[0][0])
            ]
            self.assertTrue(len(pip_calls) > 0, "pip install -e should be invoked in global scope")

if __name__ == "__main__":
    unittest.main()

import unittest
import tempfile
import shutil
import subprocess
import os
import sys
from pathlib import Path

class TestInstallerE2E(unittest.TestCase):
    """End-to-end tests for installing harness in project and global scopes."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.addCleanup(lambda: shutil.rmtree(self.temp_dir, ignore_errors=True))
        self.repo_root = Path(__file__).resolve().parent.parent

    def test_e2e_project_install(self):
        target = Path(self.temp_dir) / "sample_app"
        target.mkdir()
        (target / "package.json").write_text('{"name": "test-app", "scripts": {"test": "echo ok"}}', encoding="utf-8")

        # Run harness init in project scope
        cmd = [sys.executable, str(self.repo_root / "harness.py"), "init", str(target), "--scope", "project"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, f"STDOUT: {result.stdout}\nSTDERR: {result.stderr}")

        # Verify .agents directory structure
        agents_dir = target / ".agents"
        self.assertTrue(agents_dir.exists())
        self.assertTrue((agents_dir / "harness.config.json").exists())
        self.assertTrue((agents_dir / "hooks.json").exists())
        self.assertTrue((target / "AGENTS.md").exists())

        # Verify doctor passes on target
        doc_cmd = [sys.executable, str(self.repo_root / "harness.py"), "doctor", str(target)]
        doc_res = subprocess.run(doc_cmd, capture_output=True, text=True)
        self.assertEqual(doc_res.returncode, 0)
        self.assertIn("Doctor check completed", doc_res.stdout)

    def test_e2e_global_install_isolated(self):
        # Isolate home directory to a temporary folder
        fake_home = Path(self.temp_dir) / "fake_home"
        fake_home.mkdir()
        fake_gemini = fake_home / ".gemini" / "config"
        fake_gemini.mkdir(parents=True)

        env = {
            **os.environ,
            "GEMINI_CONFIG_DIR": str(fake_gemini),
            "AGENTS_GLOBAL_DIR": str(fake_home / ".agents"),
            "NO_PIP_INSTALL": "1"
        }

        # Run harness init with target pointing to fake_home in global scope
        cmd = [sys.executable, str(self.repo_root / "harness.py"), "init", str(fake_home), "--scope", "global"]
        result = subprocess.run(cmd, capture_output=True, text=True, env=env)
        self.assertEqual(result.returncode, 0, f"STDOUT: {result.stdout}\nSTDERR: {result.stderr}")

        # Verify .agents created in fake_home
        agents_dir = fake_home / ".agents"
        self.assertTrue(agents_dir.exists())
        self.assertTrue((agents_dir / "harness.config.json").exists())

        # Verify doctor passes on global directory
        doc_cmd = [sys.executable, str(self.repo_root / "harness.py"), "doctor", str(fake_home)]
        doc_res = subprocess.run(doc_cmd, capture_output=True, text=True, env=env)
        self.assertEqual(doc_res.returncode, 0)
        self.assertIn("Doctor check completed", doc_res.stdout)

    def test_installer_update_subcommand(self):
        # Run harness.py update with --check-only via subprocess
        cmd = [sys.executable, str(self.repo_root / "harness.py"), "update", "--check-only"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, f"STDOUT: {result.stdout}\nSTDERR: {result.stderr}")
        self.assertIn("Checking for my-harness updates", result.stdout)

if __name__ == "__main__":
    unittest.main()

import unittest
import shutil
import subprocess
from pathlib import Path

class TestInstallerSyntax(unittest.TestCase):
    def setUp(self):
        self.repo_root = Path(__file__).resolve().parent.parent
        self.install_sh = self.repo_root / "install.sh"
        self.install_ps1 = self.repo_root / "install.ps1"

    def test_install_sh_exists(self):
        self.assertTrue(self.install_sh.exists(), "install.sh must exist")

    def test_install_ps1_exists(self):
        self.assertTrue(self.install_ps1.exists(), "install.ps1 must exist")

    def test_install_sh_balanced_blocks(self):
        content = self.install_sh.read_text(encoding="utf-8")
        clean_lines = [l for l in content.splitlines() if not l.strip().startswith("#")]
        tokens = " ".join(clean_lines).split()
        if_count = tokens.count("if")
        fi_count = tokens.count("fi")
        self.assertEqual(if_count, fi_count, f"install.sh has mismatched if ({if_count}) and fi ({fi_count})")

    def test_install_sh_bash_dry_run(self):
        # Locate Git bash or real bash if available
        bash_bin = None
        for cand in [
            r"D:\Program Files\Git\bin\bash.exe",
            r"C:\Program Files\Git\bin\bash.exe",
            r"D:\Program Files\Git\usr\bin\bash.exe",
            r"C:\Program Files\Git\usr\bin\bash.exe"
        ]:
            if Path(cand).exists():
                bash_bin = cand
                break

        if not bash_bin:
            which_bash = shutil.which("bash")
            # Ignore Windows System32 stub if it fails WSL
            if which_bash and "System32" not in which_bash:
                bash_bin = which_bash

        if bash_bin:
            res = subprocess.run([bash_bin, "-n", str(self.install_sh)], capture_output=True, text=True)
            self.assertEqual(res.returncode, 0, f"bash -n install.sh failed:\n{res.stderr}")

if __name__ == "__main__":
    unittest.main()

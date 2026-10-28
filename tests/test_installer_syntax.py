import unittest
import shutil
import subprocess
from pathlib import Path

class TestInstallerSyntax(unittest.TestCase):
    def setUp(self):
        self.repo_root = Path(__file__).resolve().parent.parent
        self.install_sh = self.repo_root / "install.sh"
        self.install_ps1 = self.repo_root / "install.ps1"
        self.ci_yml = self.repo_root / ".github" / "workflows" / "ci.yml"

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

    def test_ci_powershell_step_declares_ref_variables(self):
        self.assertTrue(self.ci_yml.exists(), "ci.yml must exist")
        content = self.ci_yml.read_text(encoding="utf-8")
        if "[ref]$errors" in content:
            ref_pos = content.find("[ref]$errors")
            assign_pos = content.find("$errors =")
            self.assertTrue(
                assign_pos != -1 and assign_pos < ref_pos,
                "$errors must be assigned prior to [ref]$errors in ci.yml",
            )
        if "[ref]$tokens" in content:
            ref_pos = content.find("[ref]$tokens")
            assign_pos = content.find("$tokens =")
            self.assertTrue(
                assign_pos != -1 and assign_pos < ref_pos,
                "$tokens must be assigned prior to [ref]$tokens in ci.yml",
            )

    def test_install_ps1_parses_without_errors(self):
        ps_bin = shutil.which("powershell") or shutil.which("pwsh")
        if not ps_bin:
            self.skipTest("PowerShell interpreter not found")

        script = (
            "$tokens = $null; $errors = $null; "
            f"$null = [System.Management.Automation.Language.Parser]::ParseFile('{self.install_ps1}', [ref]$tokens, [ref]$errors); "
            "if ($errors.Count -gt 0) { $errors | ForEach-Object { Write-Host $_.Message }; exit 1 } else { exit 0 }"
        )
        res = subprocess.run(
            [ps_bin, "-NoProfile", "-NonInteractive", "-Command", script],
            capture_output=True,
            text=True,
        )
        self.assertEqual(
            res.returncode,
            0,
            f"install.ps1 parse failed:\nSTDOUT:\n{res.stdout}\nSTDERR:\n{res.stderr}",
        )

if __name__ == "__main__":
    unittest.main()

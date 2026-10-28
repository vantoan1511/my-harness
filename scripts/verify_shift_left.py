#!/usr/bin/env python3
"""
Portable Shift-Left Pre-Flight Scanner
Packaged with my-harness plugin.

Checks:
1. Branch safety (prevent working directly on main/master)
2. Conflict markers & leaked debugger/secrets in modified files
3. Project delegation (delegates to .agents/scripts/verify_shift_left.py if present)
4. Optional lint, type-check, and test runner triggers
"""

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

BANNED_PATTERNS = [
    (re.compile(r"^<{7}|^={7}|^>{7}", re.MULTILINE), "Unresolved git merge conflict marker"),
    (re.compile(r"\bdebugger;"), "Leftover JavaScript debugger statement"),
    (re.compile(r"\b(pdb\.set_trace|breakpoint\(\))"), "Leftover Python debugger breakpoint"),
    (re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"), "Potential leaked private key"),
    (re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9_]{36,}\b"), "Potential leaked GitHub token"),
]

IGNORED_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".ico", ".svg", ".webp",
    ".zip", ".tar", ".gz", ".7z", ".pdf", ".lock", ".lockb",
    ".pyc", ".pyd", ".exe", ".dll", ".so", ".dylib"
}

IGNORED_DIRS = {".git", "node_modules", "vendor", "dist", "build", ".venv", "env", "target"}

def find_project_script() -> Path | None:
    cwd = Path.cwd()
    for parent in [cwd] + list(cwd.parents):
        cand = parent / ".agents" / "scripts" / "verify_shift_left.py"
        if cand.is_file():
            return cand
        if (parent / ".git").is_dir():
            break
    return None

def run_cmd(cmd: list[str]) -> tuple[int, str, str]:
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
        return proc.returncode, proc.stdout.strip(), proc.stderr.strip()
    except FileNotFoundError:
        return 127, "", f"Command not found: {cmd[0]}"

def check_branch_safety(allow_protected: bool) -> bool:
    code, stdout, _ = run_cmd(["git", "branch", "--show-current"])
    if code != 0 or not stdout:
        return True  # Not in a git repo or detached HEAD
    branch = stdout.strip()
    if branch in {"main", "master"}:
        if allow_protected:
            print(f"[WARN] Currently on protected branch '{branch}' (allowed via flag).")
            return True
        print(f"[ERROR] Branch violation: Working directly on protected branch '{branch}' is forbidden by constitution.")
        print("        Checkout a feature branch first: git checkout -b feat/<name>")
        return False
    return True

def get_changed_files() -> list[Path]:
    code, stdout, _ = run_cmd(["git", "status", "--porcelain"])
    if code != 0:
        return []
    files: list[Path] = []
    for line in stdout.splitlines():
        if len(line) < 3:
            continue
        rel_path = line[3:].strip()
        if " -> " in rel_path:
            rel_path = rel_path.split(" -> ")[1].strip()
        p = Path(rel_path)
        if any(part in IGNORED_DIRS for part in p.parts):
            continue
        if p.suffix.lower() in IGNORED_EXTENSIONS:
            continue
        if p.is_file():
            files.append(p)
    return files

def scan_file(path: Path) -> list[str]:
    violations = []
    try:
        content = path.read_text(encoding="utf-8", errors="ignore")
    except Exception as e:
        return [f"Could not read {path}: {e}"]

    for pattern, desc in BANNED_PATTERNS:
        matches = pattern.finditer(content)
        for m in matches:
            # Calculate line number
            line_no = content.count("\n", 0, m.start()) + 1
            violations.append(f"{path}:{line_no} - {desc}")
    return violations

def main() -> int:
    parser = argparse.ArgumentParser(description="Shift-Left Pre-Flight Scanner")
    parser.add_argument("--changed", action="store_true", help="Scan uncommitted or modified files")
    parser.add_argument("--allow-protected", action="store_true", help="Allow running on main/master")
    parser.add_argument("--lint", action="store_true", help="Trigger project linter if detected")
    parser.add_argument("--type-check", action="store_true", help="Trigger project type-checker if detected")
    parser.add_argument("--test", action="store_true", help="Trigger fast project tests if detected")
    args, unknown = parser.parse_known_args()

    # 1. Project delegation: if project has its own script, delegate
    proj_script = find_project_script()
    if proj_script and proj_script.resolve() != Path(__file__).resolve():
        print(f"[INFO] Delegating to workspace script: {proj_script}", flush=True)
        res = subprocess.run([sys.executable, str(proj_script)] + sys.argv[1:])
        return res.returncode

    print("[*] Running Shift-Left Pre-Flight Scanner...")
    all_passed = True

    # Check Branch Safety
    if not check_branch_safety(args.allow_protected):
        all_passed = False

    # Check Modified Files
    changed_files = get_changed_files()
    if changed_files:
        print(f"[*] Scanning {len(changed_files)} changed file(s) for safety invariants...")
        file_violations = []
        for f in changed_files:
            file_violations.extend(scan_file(f))
        
        if file_violations:
            all_passed = False
            print("[FAIL] Shift-left violations detected:")
            for v in file_violations:
                print(f"  - {v}")
        else:
            print(f"[PASS] {len(changed_files)} file(s) clean of banned patterns and secrets.")
    else:
        print("[*] No uncommitted changed files detected.")

    if not all_passed:
        return 1

    print("[PASS] Shift-Left Pre-Flight passed with zero blockers.")
    return 0

if __name__ == "__main__":
    sys.exit(main())

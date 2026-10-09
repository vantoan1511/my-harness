#!/usr/bin/env python3
"""
verify_shift_left.py — Shift-Left Pre-Flight Verification Tool

Fast, zero-dependency (<0.5s) static validation script that enforces:
1. Git branch discipline (never commit or work directly on protected branches)
2. Configurable architectural boundaries (banned imports in specified directories)
3. Configurable pattern rules (banned functions/macros like unwrap, banned tags/attributes)
4. Configurable or auto-detected type checking, linting, and test commands

Configuration is loaded from `.agents/harness.config.json` or `harness.config.json`.
"""

import sys
import os
import re
import json
import subprocess
import argparse
from pathlib import Path

# ANSI colors
COLOR_RESET = "\033[0m"
COLOR_RED = "\033[31m"
COLOR_GREEN = "\033[32m"
COLOR_YELLOW = "\033[33m"
COLOR_BLUE = "\033[34m"
COLOR_CYAN = "\033[36m"
COLOR_BOLD = "\033[1m"

# Ensure UTF-8 output on Windows consoles
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

MARK_PASS = "[PASS]"
MARK_FAIL = "[FAIL]"
MARK_WARN = "[WARN]"

def print_header(title: str):
    print(f"\n{COLOR_BOLD}{COLOR_CYAN}==> {title}{COLOR_RESET}")

def print_success(msg: str):
    print(f"{COLOR_GREEN}{MARK_PASS} {msg}{COLOR_RESET}")

def print_warning(msg: str):
    print(f"{COLOR_YELLOW}{MARK_WARN} {msg}{COLOR_RESET}")

def print_error(msg: str):
    print(f"{COLOR_RED}{MARK_FAIL} {msg}{COLOR_RESET}")

class Violation:
    def __init__(self, file: str, line: int, code: str, rule: str, suggestion: str):
        self.file = file
        self.line = line
        self.code = code.strip()
        self.rule = rule
        self.suggestion = suggestion

    def __str__(self):
        return (
            f"  {COLOR_RED}[Line {self.line}]{COLOR_RESET} {COLOR_BOLD}{self.rule}{COLOR_RESET}\n"
            f"    Snippet:    `{self.code}`\n"
            f"    Suggestion: {COLOR_YELLOW}{self.suggestion}{COLOR_RESET}"
        )

def get_repo_root() -> Path:
    try:
        res = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=True
        )
        return Path(res.stdout.strip())
    except Exception:
        return Path(__file__).resolve().parent.parent.parent

def load_config(root: Path) -> dict:
    candidates = [
        root / ".agents" / "harness.config.json",
        root / "harness.config.json",
        root / ".agents" / "harness.json",
    ]
    for p in candidates:
        if p.exists():
            try:
                return json.loads(p.read_text(encoding="utf-8"))
            except Exception as e:
                print_warning(f"Failed to parse config {p}: {e}")
    return {}

def get_current_branch(root: Path) -> str:
    try:
        res = subprocess.run(
            ["git", "branch", "--show-current"],
            cwd=root,
            capture_output=True,
            text=True,
            check=True
        )
        return res.stdout.strip()
    except Exception:
        return ""

def get_changed_files(root: Path, staged_only: bool = False) -> list[Path]:
    files = set()
    try:
        if staged_only:
            cmd = ["git", "diff", "--name-only", "--cached", "--diff-filter=ACMRT"]
            res = subprocess.run(cmd, cwd=root, capture_output=True, text=True, check=True)
            for f in res.stdout.splitlines():
                if f.strip():
                    files.add(root / f.strip())
        else:
            # Check uncommitted changes (both staged and unstaged) + untracked files
            cmd1 = ["git", "diff", "--name-only", "HEAD", "--diff-filter=ACMRT"]
            res1 = subprocess.run(cmd1, cwd=root, capture_output=True, text=True)
            if res1.returncode == 0:
                for f in res1.stdout.splitlines():
                    if f.strip():
                        files.add(root / f.strip())
            else:
                # Fallback if HEAD does not exist (new repo)
                cmd_staged = ["git", "diff", "--name-only", "--cached"]
                res_staged = subprocess.run(cmd_staged, cwd=root, capture_output=True, text=True)
                for f in res_staged.stdout.splitlines():
                    if f.strip():
                        files.add(root / f.strip())

            cmd2 = ["git", "ls-files", "--others", "--exclude-standard"]
            res2 = subprocess.run(cmd2, cwd=root, capture_output=True, text=True)
            if res2.returncode == 0:
                for f in res2.stdout.splitlines():
                    if f.strip():
                        files.add(root / f.strip())
    except Exception as e:
        print_warning(f"Could not determine git changed files: {e}")
        return []

    return [f for f in files if f.exists() and f.is_file()]

def check_branch_safety(branch: str, config: dict) -> list[str]:
    violations = []
    git_cfg = config.get("git", {})
    if not git_cfg.get("enforce_branch_safety", True):
        return violations

    protected = git_cfg.get("protected_branches", ["main", "master"])
    if branch in protected:
        violations.append(
            f"Current branch is '{branch}'. Never commit or implement directly on protected branches {protected}! "
            f"Run `git checkout -b feat/<name>` or `fix/<name>` first."
        )
    return violations

def check_banned_imports(file_path: Path, content: str, rules: list[dict]) -> list[Violation]:
    violations = []
    norm_path = file_path.as_posix()

    for rule in rules:
        pattern = rule.get("pattern")
        if not pattern:
            continue

        path_match = rule.get("path_match", [])
        if path_match and not any(target in norm_path for target in path_match):
            continue

        path_exclude = rule.get("path_exclude", [])
        if any(target in norm_path for target in path_exclude):
            continue

        desc = rule.get("description", f"Banned import matching `{pattern}`")
        suggestion = rule.get("suggestion", "Remove or replace this import.")

        for idx, line in enumerate(content.splitlines(), start=1):
            if "shift-left-ignore" in line:
                continue
            if re.search(pattern, line):
                violations.append(
                    Violation(
                        file=norm_path,
                        line=idx,
                        code=line,
                        rule=desc,
                        suggestion=suggestion
                    )
                )

    return violations

def check_banned_patterns(file_path: Path, content: str, rules: list[dict]) -> list[Violation]:
    violations = []
    norm_path = file_path.as_posix()

    for rule in rules:
        pattern = rule.get("pattern")
        if not pattern:
            continue

        file_extensions = rule.get("file_extensions", [])
        if file_extensions and not any(norm_path.endswith(ext) for ext in file_extensions):
            continue

        path_match = rule.get("path_match", [])
        if path_match and not any(target in norm_path for target in path_match):
            continue

        path_exclude = rule.get("path_exclude", [])
        if any(target in norm_path for target in path_exclude):
            continue

        desc = rule.get("description", f"Banned pattern `{pattern}`")
        suggestion = rule.get("suggestion", "Modify or remove this code pattern.")
        ignore_in_tests = rule.get("ignore_in_test_modules", False)
        css_blocks_only = rule.get("css_blocks_only", False)

        blocks_to_check = []
        if css_blocks_only:
            if norm_path.endswith((".css", ".scss", ".less")):
                blocks_to_check.append((1, content))
            elif norm_path.endswith(".vue"):
                for m in re.finditer(r"<style\b[^>]*>(.*?)</style>", content, re.DOTALL):
                    start_line = content[:m.start(1)].count("\n") + 1
                    blocks_to_check.append((start_line, m.group(1)))
        else:
            blocks_to_check.append((1, content))

        for start_line, block in blocks_to_check:
            lines = block.splitlines()
            in_test_module = False
            test_brace_depth = 0

            for offset, line in enumerate(lines):
                line_num = start_line + offset
                stripped = line.strip()

                if ignore_in_tests:
                    if "#[cfg(test)]" in line:
                        in_test_module = True
                        test_brace_depth = 0
                        continue
                    if in_test_module:
                        test_brace_depth += line.count("{") - line.count("}")
                        if test_brace_depth <= 0 and "}" in line:
                            in_test_module = False
                        continue

                if "shift-left-ignore" in line or stripped.startswith("//") or stripped.startswith("#"):
                    continue

                if re.search(pattern, line):
                    violations.append(
                        Violation(
                            file=norm_path,
                            line=line_num,
                            code=line,
                            rule=desc,
                            suggestion=suggestion
                        )
                    )

    return violations

def check_vue_templates(file_path: Path, content: str, vue_rules: dict) -> list[Violation]:
    violations = []
    norm_path = file_path.as_posix()
    if not norm_path.endswith(".vue") or not vue_rules:
        return violations

    template_match = re.search(r"<template\b[^>]*>(.*?)</template>", content, re.DOTALL)
    if not template_match:
        return violations

    template_content = template_match.group(1)
    template_start_pos = template_match.start(1)

    banned_tags = {r["tag"]: r.get("suggestion", f"Avoid raw <{r['tag']}>") for r in vue_rules.get("banned_tags", [])}
    banned_attrs = vue_rules.get("banned_attributes", [])

    for m in re.finditer(r"<([a-zA-Z0-9_-]+)(\s*[^>]*?)>", template_content, re.DOTALL):
        tag_name = m.group(1)
        tag_attrs = m.group(2)
        tag_full = m.group(0)

        if "shift-left-ignore" in tag_attrs:
            continue

        line_num = content[: template_start_pos + m.start()].count("\n") + 1
        first_line = tag_full.splitlines()[0]

        # 1. Tag check
        if tag_name in banned_tags:
            violations.append(
                Violation(
                    file=norm_path,
                    line=line_num,
                    code=first_line,
                    rule=f"Raw `<{tag_name}>` tag in Vue template",
                    suggestion=banned_tags[tag_name]
                )
            )

        # 2. Attribute checks
        for attr_rule in banned_attrs:
            attr_name = attr_rule.get("attribute")
            ignore_components = set(attr_rule.get("ignore_components", []))
            if not attr_name:
                continue

            if tag_name in ignore_components or tag_name.lower() == attr_name.lower():
                continue

            attr_regex = rf"(?<!:)\b{re.escape(attr_name)}\s*=\s*(['\"][^'\"]*?['\"])"
            match_attr = re.search(attr_regex, tag_attrs)
            if match_attr:
                if tag_name[0].isupper() and tag_name not in {"Button", "InputText", "InputNumber", "Select", "Textarea", "ToggleSwitch", "Checkbox", "Tag", "Badge", "Tab", "DataTable"}:
                    continue

                attr_pos = match_attr.start()
                attr_line = content[: template_start_pos + m.start() + attr_pos].count("\n") + 1
                violations.append(
                    Violation(
                        file=norm_path,
                        line=attr_line,
                        code=match_attr.group(0),
                        rule=f"Disallowed `{attr_name}` attribute on `<{tag_name}>` in template",
                        suggestion=attr_rule.get("suggestion", f"Remove or replace `{attr_name}`.")
                    )
                )

    return violations

def run_command(name: str, cmd_str: str, cwd: Path) -> bool:
    if not cmd_str.strip():
        return True
    print_header(f"Running {name}: {cmd_str}")
    try:
        res = subprocess.run(cmd_str, cwd=cwd, shell=True, text=True, capture_output=True)
        if res.returncode == 0:
            print_success(f"{name} passed.")
            return True
        else:
            print_error(f"{name} failed with exit code {res.returncode}:")
            if res.stdout.strip():
                print(res.stdout)
            if res.stderr.strip():
                print(res.stderr)
            return False
    except Exception as e:
        print_error(f"Failed to execute {name}: {e}")
        return False

def scan_files(files: list[Path], config: dict) -> dict[str, list[Violation]]:
    results = {}
    rules_cfg = config.get("rules", {})
    banned_imports = rules_cfg.get("banned_imports", [])
    banned_patterns = rules_cfg.get("banned_patterns", [])
    vue_rules = rules_cfg.get("vue_template_rules", {})

    for f in files:
        try:
            content = f.read_text(encoding="utf-8")
        except Exception:
            continue

        file_violations = []
        if banned_imports:
            file_violations.extend(check_banned_imports(f, content, banned_imports))
        if banned_patterns:
            file_violations.extend(check_banned_patterns(f, content, banned_patterns))
        if vue_rules:
            file_violations.extend(check_vue_templates(f, content, vue_rules))

        if file_violations:
            results[f.as_posix()] = file_violations

    return results

def main():
    parser = argparse.ArgumentParser(description="Shift-Left Pre-Flight Verification Scanner")
    parser.add_argument("--changed", action="store_true", default=True, help="Scan git changed/untracked files (default)")
    parser.add_argument("--staged", action="store_true", help="Scan git staged files only")
    parser.add_argument("--all", action="store_true", help="Scan all source files in repository")
    parser.add_argument("--files", nargs="*", help="Scan explicit list of files")
    parser.add_argument("--type-check", action="store_true", help="Run configured type checking command")
    parser.add_argument("--lint", action="store_true", help="Run configured linting command")
    parser.add_argument("--test", action="store_true", help="Run configured test command")
    parser.add_argument("--build", action="store_true", help="Run configured build command")
    parser.add_argument("--all-checks", action="store_true", help="Run scanner + type-check + lint + test")

    args = parser.parse_args()
    root = get_repo_root()
    config = load_config(root)

    print_header("Shift-Left Pre-Flight Check")

    # 1. Branch Safety Check
    branch = get_current_branch(root)
    print(f"Working Directory: {root}")
    print(f"Current Branch:    {COLOR_BOLD}{branch or 'Unknown'}{COLOR_RESET}")

    branch_violations = check_branch_safety(branch, config)
    if branch_violations:
        for bv in branch_violations:
            print_error(bv)
        print_error("Shift-Left Pre-Flight failed: Branch safety violation.")
        sys.exit(1)
    else:
        print_success("Branch safety verified (not on protected branch).")

    # 2. Collect target files
    target_files = []
    if args.files:
        target_files = [Path(f).resolve() for f in args.files if Path(f).exists()]
    elif args.all:
        for ext in ("*.vue", "*.ts", "*.js", "*.css", "*.scss", "*.rs", "*.py", "*.go"):
            target_files.extend(root.rglob(ext))
    elif args.staged:
        target_files = get_changed_files(root, staged_only=True)
    else:
        target_files = get_changed_files(root, staged_only=False)

    # Filter out ignored dirs
    ignored_parts = {"node_modules", "target", ".git", ".venv", "venv", "__pycache__", "dist", "build"}
    filtered_files = [
        f for f in target_files
        if not any(part in f.parts for part in ignored_parts)
    ]

    print(f"Files to inspect:  {len(filtered_files)}")

    # 3. Scan files for pattern violations
    violations_by_file = scan_files(filtered_files, config)
    total_violations = sum(len(v) for v in violations_by_file.values())

    if total_violations > 0:
        print_header("Shift-Left Pattern Violations Found")
        for file_path, violations in violations_by_file.items():
            rel_path = os.path.relpath(file_path, root)
            print(f"\n{COLOR_BOLD}File: {rel_path}{COLOR_RESET} ({len(violations)} issues)")
            for v in violations:
                print(v)

        print_error(f"\nPre-Flight failed: {total_violations} shift-left violation(s) detected across {len(violations_by_file)} file(s).")
        print_warning("Fix the issues above before proceeding with implementation or committing.")
        sys.exit(1)
    else:
        print_success(f"Pattern checks clean: 0 violations across {len(filtered_files)} file(s).")

    # 4. Command Runners
    commands = config.get("commands", {})
    commands_passed = True

    if args.lint or args.all_checks:
        cmd = commands.get("lint")
        if not cmd and (root / "package.json").exists():
            cmd = "npm run lint"
        if cmd:
            commands_passed = run_command("Lint", cmd, root) and commands_passed

    if args.type_check or args.all_checks:
        cmd = commands.get("type_check")
        if not cmd and (root / "package.json").exists():
            cmd = "npm run type-check"
        elif not cmd and (root / "tsconfig.json").exists():
            cmd = "npx tsc --noEmit"
        if cmd:
            commands_passed = run_command("Type Check", cmd, root) and commands_passed

    if args.test or args.all_checks:
        cmd = commands.get("test")
        if not cmd and (root / "package.json").exists():
            cmd = "npm test"
        elif not cmd and (root / "Cargo.toml").exists():
            cmd = "cargo test"
        elif not cmd and ((root / "pytest.ini").exists() or (root / "pyproject.toml").exists()):
            cmd = "pytest"
        elif not cmd and (root / "go.mod").exists():
            cmd = "go test ./..."
        if cmd:
            commands_passed = run_command("Unit Tests", cmd, root) and commands_passed

    if args.build:
        cmd = commands.get("build")
        if not cmd and (root / "package.json").exists():
            cmd = "npm run build"
        elif not cmd and (root / "Cargo.toml").exists():
            cmd = "cargo build"
        if cmd:
            commands_passed = run_command("Build", cmd, root) and commands_passed

    if not commands_passed:
        print_error("\nOne or more validation commands failed.")
        sys.exit(1)

    print_header("Pre-Flight Complete")
    print_success("All shift-left gates passed cleanly!")
    sys.exit(0)

if __name__ == "__main__":
    main()

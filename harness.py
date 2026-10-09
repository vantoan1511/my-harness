#!/usr/bin/env python3
"""
my-harness — Reusable Agent Engineering Harness CLI

A modular, shift-left engineering harness for autonomous AI coding agents.
Scaffolds, manages, and verifies .agents setups across software projects.
"""

import sys
import os
import shutil
import json
import argparse
import subprocess
from pathlib import Path

VERSION = "0.1.0"

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

def get_harness_root() -> Path:
    return Path(__file__).resolve().parent

def print_banner():
    banner = rf"""
{COLOR_BOLD}{COLOR_CYAN}  __  ____   __       _    _                                
 |  \/  \ \ / /      | |  | |                               
 | \  / |\ V / ______| |__| | __ _ _ __ _ __   ___  ___ ___ 
 | |\/| | > < |______|  __  |/ _` | '__| '_ \ / _ \/ __/ __|
 | |  | |/ . \       | |  | | (_| | |  | | | |  __/\__ \__ \
 |_|  |_/_/ \_\      |_|  |_|\__,_|_|  |_| |_|\___||___/___/
{COLOR_RESET}                     {COLOR_YELLOW}v{VERSION}{COLOR_RESET} — Autonomous Agent Harness
"""
    print(banner)

def detect_project_stack(target_dir: Path) -> dict:
    stack = {
        "languages": [],
        "commands": {
            "type_check": "",
            "lint": "",
            "test": "",
            "build": ""
        }
    }

    # Node / TypeScript
    if (target_dir / "package.json").exists():
        stack["languages"].append("Node/TypeScript")
        try:
            pkg = json.loads((target_dir / "package.json").read_text(encoding="utf-8"))
            scripts = pkg.get("scripts", {})
            if "type-check" in scripts:
                stack["commands"]["type_check"] = "npm run type-check"
            elif "typecheck" in scripts:
                stack["commands"]["type_check"] = "npm run typecheck"

            if "lint" in scripts:
                stack["commands"]["lint"] = "npm run lint"

            if "test" in scripts:
                stack["commands"]["test"] = "npm test"

            if "build" in scripts:
                stack["commands"]["build"] = "npm run build"
        except Exception:
            stack["commands"]["test"] = "npm test"

    # Rust
    if (target_dir / "Cargo.toml").exists():
        stack["languages"].append("Rust")
        if not stack["commands"]["test"]:
            stack["commands"]["test"] = "cargo test"
        if not stack["commands"]["lint"]:
            stack["commands"]["lint"] = "cargo clippy -- -D warnings"
        if not stack["commands"]["build"]:
            stack["commands"]["build"] = "cargo build"

    # Python
    if any((target_dir / f).exists() for f in ("pyproject.toml", "requirements.txt", "setup.py", "pytest.ini")):
        stack["languages"].append("Python")
        if not stack["commands"]["test"]:
            stack["commands"]["test"] = "pytest"
        if not stack["commands"]["lint"]:
            stack["commands"]["lint"] = "ruff check ."

    # Go
    if (target_dir / "go.mod").exists():
        stack["languages"].append("Go")
        if not stack["commands"]["test"]:
            stack["commands"]["test"] = "go test ./..."
        if not stack["commands"]["lint"]:
            stack["commands"]["lint"] = "go vet ./..."

    if not stack["languages"]:
        stack["languages"].append("Universal")

    return stack

def copy_tree_merge(src: Path, dst: Path):
    """Recursively copies src to dst, merging without overwriting non-empty existing dirs."""
    dst.mkdir(parents=True, exist_ok=True)
    for item in src.iterdir():
        target = dst / item.name
        if item.is_dir():
            copy_tree_merge(item, target)
        else:
            if not target.exists() or item.suffix in ('.py', '.json', '.md'):
                shutil.copy2(item, target)

def cmd_init(args):
    harness_root = get_harness_root()
    is_global = getattr(args, "scope", "project") == "global"

    if is_global:
        target_dir = Path.home() if args.target == "." else Path(args.target).resolve()
        target_agents = target_dir / ".agents"
        print(f"{COLOR_CYAN}==> Initializing my-harness globally in: {target_dir} ({target_agents}){COLOR_RESET}")
    else:
        target_dir = Path(args.target).resolve()
        target_agents = target_dir / ".agents"
        print(f"{COLOR_CYAN}==> Initializing my-harness in: {target_dir}{COLOR_RESET}")

    template_agents = harness_root / "template" / ".agents"

    if not template_agents.exists():
        print(f"{COLOR_RED}Error: Template directory not found at {template_agents}{COLOR_RESET}")
        sys.exit(1)

    # 1. Copy template .agents/ into target
    copy_tree_merge(template_agents, target_agents)
    print(f"{COLOR_GREEN}[PASS] Scaffolding .agents/ directories and core skills{COLOR_RESET}")

    # 2. Detect stack and customize harness.config.json
    stack = detect_project_stack(target_dir)
    config_file = target_agents / "harness.config.json"
    config = {}
    if config_file.exists():
        try:
            config = json.loads(config_file.read_text(encoding="utf-8"))
        except Exception:
            config = {}

    project_name = "global-harness" if (is_global and target_dir == Path.home()) else (target_dir.name or "project")
    config["project_name"] = project_name
    config["preset"] = args.preset or "universal"

    # Merge commands
    if "commands" not in config:
        config["commands"] = {}
    for cmd_key, cmd_val in stack["commands"].items():
        if not config["commands"].get(cmd_key) and cmd_val:
            config["commands"][cmd_key] = cmd_val

    config_file.write_text(json.dumps(config, indent=2), encoding="utf-8")
    print(f"{COLOR_GREEN}[PASS] Configured harness.config.json for {', '.join(stack['languages'])}{COLOR_RESET}")

    # 3. Create starter AGENTS.md / GEMINI.md if none exists (project scope only)
    if not is_global:
        rules_file = target_dir / "AGENTS.md"
        gemini_file = target_dir / "GEMINI.md"
        if not rules_file.exists() and not gemini_file.exists():
            template_rule = harness_root / "template" / "AGENTS.md.template"
            if template_rule.exists():
                content = template_rule.read_text(encoding="utf-8")
                content = content.replace("{{PROJECT_NAME}}", project_name)
                content = content.replace("{{TECH_STACK}}", ", ".join(stack["languages"]))
                rules_file.write_text(content, encoding="utf-8")
                print(f"{COLOR_GREEN}[PASS] Created starter AGENTS.md rules file{COLOR_RESET}")

    # 4. Optional pack installation
    if args.pack:
        install_pack(args.pack, target_dir)

    # 5. Global CLI installation via pip if global scope
    if is_global:
        print(f"\n{COLOR_CYAN}==> Registering 'harness' CLI globally via pip...{COLOR_RESET}")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "-e", str(harness_root)], check=True)
            print(f"{COLOR_GREEN}[PASS] Successfully registered 'harness' CLI globally{COLOR_RESET}")
        except Exception as e:
            print(f"{COLOR_YELLOW}Warning: Failed to pip install harness globally: {e}{COLOR_RESET}")
            print(f"{COLOR_YELLOW}Tip: You can manually run: pip install -e {harness_root}{COLOR_RESET}")

    print(f"\n{COLOR_BOLD}{COLOR_GREEN}✓ my-harness initialization ({'global' if is_global else 'project'}) complete!{COLOR_RESET}")
    if is_global:
        print(f"Global .agents configuration installed in: {target_agents}")
        print(f"You can now run 'harness <subcommand>' anywhere in your terminal.")
    else:
        print(f"\nAvailable workflows in {target_dir}:")
        print(f"  - /specify <intent>       (Contract-first specification & plan handoff)")
        print(f"  - /prp-plan <feature>     (Comprehensive plan with TDD tasks & plan handoff)")
        print(f"  - /implement <plan.md>    (Atomic shift-left execution, auto-commit & PR)")
        print(f"  - /tdd-workflow           (Red-Green-Refactor testing gate)")
        print(f"  - /code-review            (Pre-flight quality & security checks)")
        print(f"  - /commit                 (Conventional commit with smart staging)")
        print(f"  - /pr                     (Automated GitHub PR creation)")
        print(f"  - /pr-changelog           (Generate concise PR changelog)")
        print(f"  - python .agents/scripts/verify_shift_left.py --changed (Fast pre-flight check)")

def install_pack(pack_name: str, target_dir: Path):
    harness_root = get_harness_root()
    pack_dir = harness_root / "packs" / pack_name

    if not pack_dir.exists():
        print(f"{COLOR_RED}Error: Pack '{pack_name}' not found in {harness_root / 'packs'}{COLOR_RESET}")
        return False

    print(f"{COLOR_CYAN}==> Installing pack: {pack_name}{COLOR_RESET}")
    target_agents = target_dir / ".agents"
    target_agents.mkdir(parents=True, exist_ok=True)

    # 1. Copy rules
    if (pack_dir / "rules").exists():
        copy_tree_merge(pack_dir / "rules", target_agents / "rules")
        print(f"  - Installed pack rules into .agents/rules/")

    # 2. Copy skills
    if (pack_dir / "skills").exists():
        copy_tree_merge(pack_dir / "skills", target_agents / "skills")
        print(f"  - Installed pack skills into .agents/skills/")

    # 3. Copy references
    if (pack_dir / "references").exists():
        copy_tree_merge(pack_dir / "references", target_agents / "references")
        print(f"  - Installed pack references into .agents/references/")

    # 4. Merge config if present
    pack_config_file = pack_dir / "harness.config.json"
    target_config_file = target_agents / "harness.config.json"
    if pack_config_file.exists() and target_config_file.exists():
        try:
            p_cfg = json.loads(pack_config_file.read_text(encoding="utf-8"))
            t_cfg = json.loads(target_config_file.read_text(encoding="utf-8"))

            # Merge rules
            if "rules" in p_cfg:
                if "rules" not in t_cfg:
                    t_cfg["rules"] = {}
                for k, v in p_cfg["rules"].items():
                    if isinstance(v, list):
                        existing = t_cfg["rules"].get(k, [])
                        existing_ids = {item.get("id") for item in existing if isinstance(item, dict) and "id" in item}
                        for item in v:
                            if isinstance(item, dict) and item.get("id") in existing_ids:
                                continue
                            existing.append(item)
                        t_cfg["rules"][k] = existing
                    elif isinstance(v, dict):
                        t_cfg["rules"][k] = {**t_cfg["rules"].get(k, {}), **v}

            # Merge guardrails
            if "guardrails" in p_cfg and "reminders" in p_cfg["guardrails"]:
                t_cfg.setdefault("guardrails", {})["reminders"] = p_cfg["guardrails"]["reminders"]

            # Merge commands
            if "commands" in p_cfg:
                for ck, cv in p_cfg["commands"].items():
                    if cv:
                        t_cfg.setdefault("commands", {})[ck] = cv

            target_config_file.write_text(json.dumps(t_cfg, indent=2), encoding="utf-8")
            print(f"  - Merged pack configuration rules and reminders")
        except Exception as e:
            print(f"{COLOR_YELLOW}Warning: Failed to merge pack config: {e}{COLOR_RESET}")

    print(f"{COLOR_GREEN}[PASS] Pack '{pack_name}' successfully installed!{COLOR_RESET}")
    return True

def cmd_add_pack(args):
    target_dir = Path(args.target).resolve()
    install_pack(args.pack, target_dir)

def cmd_list_packs(args):
    harness_root = get_harness_root()
    packs_dir = harness_root / "packs"

    print(f"\n{COLOR_BOLD}{COLOR_CYAN}Available Extension Packs:{COLOR_RESET}\n")
    if not packs_dir.exists():
        print("No packs directory found.")
        return

    for p in sorted(packs_dir.iterdir()):
        if p.is_dir():
            readme = p / "README.md"
            desc = "No description"
            if readme.exists():
                for line in readme.read_text(encoding="utf-8").splitlines():
                    if line.strip() and not line.startswith("#"):
                        desc = line.strip()
                        break
            print(f"  - {COLOR_BOLD}{p.name}{COLOR_RESET}")
            print(f"    {COLOR_YELLOW}{desc}{COLOR_RESET}\n")

def cmd_doctor(args):
    target_dir = Path(args.target).resolve()
    target_agents = target_dir / ".agents"

    print(f"{COLOR_CYAN}==> Running my-harness Doctor on: {target_dir}{COLOR_RESET}\n")

    if not target_agents.exists():
        print(f"{COLOR_RED}[FAIL] .agents/ directory does not exist! Run `harness init` first.{COLOR_RESET}")
        sys.exit(1)

    # 1. Structure checks
    expected_dirs = [
        "rules", "scripts", "skills", "references", "PRPs",
        "PRPs/plans", "PRPs/plans/completed", "PRPs/prds", "PRPs/reports",
        "reviews", "handoffs", "logs"
    ]
    all_dirs_ok = True
    for d in expected_dirs:
        dir_path = target_agents / d
        if dir_path.exists():
            print(f"{COLOR_GREEN}[PASS]{COLOR_RESET} Directory: .agents/{d}")
        else:
            print(f"{COLOR_RED}[FAIL]{COLOR_RESET} Missing directory: .agents/{d}")
            all_dirs_ok = False

    # 2. JSON files check
    for json_file in ("hooks.json", "harness.config.json"):
        jp = target_agents / json_file
        if jp.exists():
            try:
                json.loads(jp.read_text(encoding="utf-8"))
                print(f"{COLOR_GREEN}[PASS]{COLOR_RESET} Valid JSON: .agents/{json_file}")
            except Exception as e:
                print(f"{COLOR_RED}[FAIL]{COLOR_RESET} Invalid JSON in .agents/{json_file}: {e}")
        else:
            print(f"{COLOR_YELLOW}[WARN]{COLOR_RESET} Missing file: .agents/{json_file}")

    # 3. Scripts check
    for s in ("verify_shift_left.py", "shift_left_hook.py", "memory_logger.py", "curate_knowledge.py"):
        sp = target_agents / "scripts" / s
        if sp.exists():
            print(f"{COLOR_GREEN}[PASS]{COLOR_RESET} Script present: .agents/scripts/{s}")
        else:
            print(f"{COLOR_RED}[FAIL]{COLOR_RESET} Missing script: .agents/scripts/{s}")

    # 4. Branch check
    try:
        res = subprocess.run(["git", "branch", "--show-current"], cwd=target_dir, capture_output=True, text=True)
        branch = res.stdout.strip()
        print(f"{COLOR_GREEN}[PASS]{COLOR_RESET} Git branch: {branch or 'Detached / No Branch'}")
    except Exception:
        print(f"{COLOR_YELLOW}[WARN]{COLOR_RESET} Git repository not initialized or git not in PATH")

    print(f"\n{COLOR_BOLD}Doctor check completed.{COLOR_RESET}")

def cmd_verify(args):
    target_dir = Path(args.target).resolve()
    script = target_dir / ".agents" / "scripts" / "verify_shift_left.py"

    if not script.exists():
        # Fallback to harness's own script
        script = get_harness_root() / "template" / ".agents" / "scripts" / "verify_shift_left.py"

    cmd = [sys.executable, str(script)]
    if args.staged:
        cmd.append("--staged")
    elif args.all:
        cmd.append("--all")
    elif args.all_checks:
        cmd.append("--all-checks")
    else:
        cmd.append("--changed")

    res = subprocess.run(cmd, cwd=target_dir)
    sys.exit(res.returncode)

def cmd_sync(args):
    harness_root = get_harness_root()
    target_dir = Path(args.target).resolve()
    target_agents = target_dir / ".agents"
    template_agents = harness_root / "template" / ".agents"

    if not target_agents.exists():
        print(f"{COLOR_RED}Error: .agents/ does not exist in {target_dir}. Use `harness init` instead.{COLOR_RESET}")
        sys.exit(1)

    print(f"{COLOR_CYAN}==> Syncing core harness scripts and universal skills to {target_dir}{COLOR_RESET}")

    # Sync scripts
    copy_tree_merge(template_agents / "scripts", target_agents / "scripts")
    # Sync core rules
    copy_tree_merge(template_agents / "rules", target_agents / "rules")
    # Sync skills
    copy_tree_merge(template_agents / "skills", target_agents / "skills")

    print(f"{COLOR_GREEN}[PASS] Core scripts, rules, and universal skills updated!{COLOR_RESET}")

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="my-harness — Reusable Agent Engineering Harness")
    subparsers = parser.add_subparsers(dest="subcommand", help="Harness command to run")

    # init
    p_init = subparsers.add_parser("init", help="Initialize .agents harness in a target project or globally")
    p_init.add_argument("target", nargs="?", default=".", help="Target project directory (default: current directory)")
    p_init.add_argument("--scope", choices=["project", "global"], default="project", help="Installation scope: project (target directory) or global (user home ~/.agents and CLI)")
    p_init.add_argument("--preset", default="universal", help="Configuration preset name")
    p_init.add_argument("--pack", help="Optional pack to install during init (e.g. orbit-desktop, vue-primevue)")

    # add-pack
    p_pack = subparsers.add_parser("add-pack", help="Install an extension pack into target project")
    p_pack.add_argument("pack", help="Name of pack (e.g. orbit-desktop, vue-primevue)")
    p_pack.add_argument("target", nargs="?", default=".", help="Target project directory")

    # list-packs
    subparsers.add_parser("list-packs", help="List available extension packs")

    # doctor
    p_doc = subparsers.add_parser("doctor", help="Check the health of .agents setup")
    p_doc.add_argument("target", nargs="?", default=".", help="Target project directory")

    # verify
    p_verify = subparsers.add_parser("verify", help="Run shift-left pre-flight verification")
    p_verify.add_argument("target", nargs="?", default=".", help="Target project directory")
    p_verify.add_argument("--changed", action="store_true", help="Scan changed files (default)")
    p_verify.add_argument("--staged", action="store_true", help="Scan staged files")
    p_verify.add_argument("--all", action="store_true", help="Scan all source files")
    p_verify.add_argument("--all-checks", action="store_true", help="Run pre-flight scanner + static analysis + tests")

    # sync
    p_sync = subparsers.add_parser("sync", help="Update core harness scripts and skills in target project")
    p_sync.add_argument("target", nargs="?", default=".", help="Target project directory")

    return parser

def main():
    parser = build_parser()
    args = parser.parse_args()

    if not args.subcommand:
        print_banner()
        parser.print_help()
        sys.exit(0)

    if args.subcommand == "init":
        cmd_init(args)
    elif args.subcommand == "add-pack":
        cmd_add_pack(args)
    elif args.subcommand == "list-packs":
        cmd_list_packs(args)
    elif args.subcommand == "doctor":
        cmd_doctor(args)
    elif args.subcommand == "verify":
        cmd_verify(args)
    elif args.subcommand == "sync":
        cmd_sync(args)

if __name__ == "__main__":
    main()

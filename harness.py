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
import time
from pathlib import Path
from dataclasses import dataclass, field
from typing import Set, Optional

VERSION = "0.1.0"

@dataclass
class UpdateCheckResult:
    is_git_repo: bool
    current_commit: str
    remote_commit: str
    has_update: bool
    behind_count: int
    error: Optional[str] = None

@dataclass
class PluginDeploymentResult:
    plugin_dir: Path
    manifest_updated: bool
    skills_copied: int
    rules_consolidated: bool
    assets_copied: bool
    pip_updated: bool = False
    errors: list = field(default_factory=list)

@dataclass
class GlobalInstallationInfo:
    is_installed: bool
    plugin_dir: Optional[Path] = None
    global_agents_dir: Optional[Path] = None
    global_skills: Set[str] = field(default_factory=set)
    global_rules: Set[str] = field(default_factory=set)

def get_gemini_config_dir() -> Path:
    env_dir = os.environ.get("GEMINI_CONFIG_DIR")
    if env_dir:
        return Path(env_dir)
    return Path.home() / ".gemini" / "config"

def get_global_plugin_dir() -> Path:
    return get_gemini_config_dir() / "plugins" / "my-harness"

def get_global_agents_dir() -> Path:
    env_dir = os.environ.get("AGENTS_GLOBAL_DIR")
    if env_dir:
        return Path(env_dir)
    return Path.home() / ".agents"

def detect_global_installation() -> GlobalInstallationInfo:
    plugin_dir = get_global_plugin_dir()
    global_agents = get_global_agents_dir()

    has_plugin = plugin_dir.exists()
    has_global_agents = global_agents.exists()

    is_installed = has_plugin or has_global_agents
    skills: Set[str] = set()
    rules: Set[str] = set()

    # Collect from plugin
    if has_plugin:
        plugin_skills_dir = plugin_dir / "skills"
        if plugin_skills_dir.exists():
            for s in plugin_skills_dir.iterdir():
                if s.is_dir() and (s / "SKILL.md").exists():
                    skills.add(s.name)
        plugin_rules_dir = plugin_dir / "rules"
        if plugin_rules_dir.exists():
            for r in plugin_rules_dir.glob("*.md"):
                rules.add(r.name)
            if (plugin_rules_dir / "AGENTS.md").exists():
                rules.update({"shift-left-quality.md", "review-rules.md", "natural-human-writing.md"})

    # Collect from global .agents
    if has_global_agents:
        g_skills_dir = global_agents / "skills"
        if g_skills_dir.exists():
            for s in g_skills_dir.iterdir():
                if s.is_dir() and (s / "SKILL.md").exists():
                    skills.add(s.name)
        g_rules_dir = global_agents / "rules"
        if g_rules_dir.exists():
            for r in g_rules_dir.glob("*.md"):
                rules.add(r.name)

    return GlobalInstallationInfo(
        is_installed=is_installed,
        plugin_dir=plugin_dir if has_plugin else None,
        global_agents_dir=global_agents if has_global_agents else None,
        global_skills=skills,
        global_rules=rules
    )

def deduplicate_project_scope(target_agents: Path, global_info: GlobalInstallationInfo, dry_run: bool = False) -> dict:
    summary = {
        "removed_skills": [],
        "preserved_skills": [],
        "removed_rules": [],
        "preserved_rules": []
    }

    if not global_info.is_installed:
        return summary

    skills_dir = target_agents / "skills"
    if skills_dir.exists():
        for s in list(skills_dir.iterdir()):
            if s.is_dir():
                if s.name in global_info.global_skills:
                    summary["removed_skills"].append(s.name)
                    if not dry_run:
                        shutil.rmtree(s)
                else:
                    summary["preserved_skills"].append(s.name)

    rules_dir = target_agents / "rules"
    if rules_dir.exists():
        for r in list(rules_dir.glob("*.md")):
            if r.name in global_info.global_rules:
                summary["removed_rules"].append(r.name)
                if not dry_run:
                    r.unlink()
            else:
                summary["preserved_rules"].append(r.name)

    if not dry_run:
        skills_dir.mkdir(parents=True, exist_ok=True)
        rules_dir.mkdir(parents=True, exist_ok=True)

    return summary

def repair_project_structure(target_agents: Path, dry_run: bool = False) -> dict:
    expected_dirs = [
        "rules", "scripts", "skills", "references", "PRPs",
        "PRPs/plans", "PRPs/plans/completed", "PRPs/prds", "PRPs/reports",
        "reviews", "handoffs", "logs"
    ]
    summary = {"created_dirs": [], "existing_dirs": []}
    for d in expected_dirs:
        dir_path = target_agents / d
        if not dir_path.exists():
            summary["created_dirs"].append(d)
            if not dry_run:
                dir_path.mkdir(parents=True, exist_ok=True)
                if d in ["PRPs/plans/completed", "PRPs/prds", "PRPs/reports", "reviews", "handoffs", "logs"]:
                    (dir_path / ".gitkeep").touch(exist_ok=True)
        else:
            summary["existing_dirs"].append(d)
    return summary

def repair_project_scripts(target_agents: Path, template_agents: Path, dry_run: bool = False) -> dict:
    core_scripts = ["verify_shift_left.py", "shift_left_hook.py", "memory_logger.py", "curate_knowledge.py"]
    summary = {"restored_scripts": [], "existing_scripts": []}
    scripts_dir = target_agents / "scripts"
    if not dry_run:
        scripts_dir.mkdir(parents=True, exist_ok=True)

    template_scripts_dir = template_agents / "scripts"
    for s in core_scripts:
        target_script = scripts_dir / s
        if not target_script.exists():
            summary["restored_scripts"].append(s)
            if not dry_run and (template_scripts_dir / s).exists():
                shutil.copy2(template_scripts_dir / s, target_script)
        else:
            summary["existing_scripts"].append(s)
    return summary

def repair_project_configs(target_dir: Path, target_agents: Path, template_agents: Path, dry_run: bool = False) -> dict:
    summary = {"repaired_configs": []}
    config_file = target_agents / "harness.config.json"
    hooks_file = target_agents / "hooks.json"

    need_config_repair = False
    config = {}
    if not config_file.exists():
        need_config_repair = True
    else:
        try:
            config = json.loads(config_file.read_text(encoding="utf-8"))
        except Exception:
            need_config_repair = True
            config = {}

    if need_config_repair or "project_name" not in config or "commands" not in config:
        summary["repaired_configs"].append("harness.config.json")
        if not dry_run:
            stack = detect_project_stack(target_dir)
            project_name = target_dir.name or "project"
            config.setdefault("project_name", project_name)
            config.setdefault("preset", "universal")
            if "commands" not in config:
                config["commands"] = {}
            for k, v in stack["commands"].items():
                if not config["commands"].get(k) and v:
                    config["commands"][k] = v
            config_file.write_text(json.dumps(config, indent=2), encoding="utf-8")

    need_hooks_repair = False
    if not hooks_file.exists():
        need_hooks_repair = True
    else:
        try:
            json.loads(hooks_file.read_text(encoding="utf-8"))
        except Exception:
            need_hooks_repair = True

    if need_hooks_repair:
        summary["repaired_configs"].append("hooks.json")
        if not dry_run:
            template_hooks = template_agents / "hooks.json"
            if template_hooks.exists():
                shutil.copy2(template_hooks, hooks_file)

    return summary

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

def copy_tree_merge(
    src: Path,
    dst: Path,
    overwrite_configs: bool = False,
    exclude_dirs: Optional[Set[str]] = None,
    exclude_files: Optional[Set[str]] = None,
    exclude_suffixes: Optional[Set[str]] = None,
):
    """Recursively copies src to dst, merging without overwriting non-empty existing dirs."""
    if exclude_dirs is None:
        exclude_dirs = {"__pycache__", ".pytest_cache"}
    if exclude_files is None:
        exclude_files = set()
    if exclude_suffixes is None:
        exclude_suffixes = {".pyc", ".pyo"}

    dst.mkdir(parents=True, exist_ok=True)
    for item in src.iterdir():
        if item.is_dir() and item.name in exclude_dirs:
            continue
        if item.is_file() and (item.name in exclude_files or item.suffix in exclude_suffixes):
            continue
        target = dst / item.name
        if item.is_dir():
            copy_tree_merge(
                item,
                target,
                overwrite_configs=overwrite_configs,
                exclude_dirs=exclude_dirs,
                exclude_files=exclude_files,
                exclude_suffixes=exclude_suffixes,
            )
        else:
            if not target.exists():
                shutil.copy2(item, target)
            elif item.name in ("harness.config.json", "hooks.json") and not overwrite_configs:
                # Preserve existing project configuration files
                continue
            elif item.suffix in ('.py', '.json', '.md'):
                shutil.copy2(item, target)

def deploy_antigravity_plugin(harness_root: Path, target_plugin_dir: Path, pack: Optional[str] = None) -> PluginDeploymentResult:
    """Packages and deploys my-harness as an Antigravity plugin into target_plugin_dir."""
    errors = []
    template_agents = harness_root / "template" / ".agents"
    target_plugin_dir.mkdir(parents=True, exist_ok=True)

    # 1. Manifest
    manifest_updated = False
    try:
        plugin_manifest = {
            "name": "my-harness",
            "displayName": "Agent Engineering DevKit",
            "version": VERSION,
            "description": "Shift-left SDLC workflows: spec-first design, TDD loops, code review, and automated PR delivery.",
            "logo": "assets/logo.svg",
            "suggestedPrompts": [
                "/specify design contract and implementation plan for a new feature",
                "/tdd-workflow implement failing tests first then pass them",
                "/code-review inspect uncommitted changes against quality constitution"
            ]
        }
        (target_plugin_dir / "plugin.json").write_text(json.dumps(plugin_manifest, indent=2), encoding="utf-8")
        manifest_updated = True
    except Exception as e:
        errors.append(f"Failed to write plugin.json: {e}")

    # 2. Assets
    assets_copied = False
    try:
        assets_dir = target_plugin_dir / "assets"
        assets_dir.mkdir(parents=True, exist_ok=True)
        logo_src = harness_root / "assets" / "logo.svg"
        if not logo_src.exists():
            logo_src = harness_root / "template" / "assets" / "logo.svg"
        if logo_src.exists():
            shutil.copy2(logo_src, assets_dir / "logo.svg")
            assets_copied = True
    except Exception as e:
        errors.append(f"Failed to copy assets: {e}")

    # 3. README
    try:
        plugin_readme_src = harness_root / "template" / "PLUGIN_README.md"
        if plugin_readme_src.exists():
            shutil.copy2(plugin_readme_src, target_plugin_dir / "README.md")
        elif (harness_root / "README.md").exists():
            shutil.copy2(harness_root / "README.md", target_plugin_dir / "README.md")
    except Exception as e:
        errors.append(f"Failed to copy README.md: {e}")

    # 4. Skills
    skills_copied = 0
    plugin_exclude_dirs = {"__pycache__", ".pytest_cache", "tests", "evals", "agents"}
    plugin_exclude_files = {"openai.yaml", ".update_check.json"}
    plugin_exclude_suffixes = {".pyc", ".pyo"}
    try:
        plugin_skills_dir = target_plugin_dir / "skills"
        if plugin_skills_dir.exists():
            # Clean any stale excluded directories/files from prior installations
            for p in list(plugin_skills_dir.rglob("*")):
                if p.exists():
                    if p.is_dir() and p.name in plugin_exclude_dirs:
                        shutil.rmtree(p, ignore_errors=True)
                    elif p.is_file() and (p.name in plugin_exclude_files or p.suffix in plugin_exclude_suffixes):
                        p.unlink(missing_ok=True)
        copy_tree_merge(
            template_agents / "skills",
            plugin_skills_dir,
            exclude_dirs=plugin_exclude_dirs,
            exclude_files=plugin_exclude_files,
            exclude_suffixes=plugin_exclude_suffixes,
        )
        skills_copied = len([s for s in plugin_skills_dir.iterdir() if s.is_dir()])
    except Exception as e:
        errors.append(f"Failed to copy skills: {e}")

    # 5. Consolidate rules into rules/AGENTS.md
    rules_consolidated = False
    try:
        rules_target_dir = target_plugin_dir / "rules"
        rules_target_dir.mkdir(parents=True, exist_ok=True)
        for old_rule in rules_target_dir.glob("*.md"):
            if old_rule.name != "AGENTS.md":
                old_rule.unlink()

        rule_parts = []
        for r_name in ["shift-left-quality.md", "review-rules.md", "natural-human-writing.md"]:
            r_path = template_agents / "rules" / r_name
            if r_path.exists():
                rule_parts.append(r_path.read_text(encoding="utf-8").strip())

        # Copy pack skills & rules if pack was specified
        if pack:
            pack_dir = harness_root / "packs" / pack
            if (pack_dir / "skills").exists():
                copy_tree_merge(
                    pack_dir / "skills",
                    target_plugin_dir / "skills",
                    exclude_dirs=plugin_exclude_dirs,
                    exclude_files=plugin_exclude_files,
                    exclude_suffixes=plugin_exclude_suffixes,
                )
            if (pack_dir / "rules").exists():
                for pr_path in (pack_dir / "rules").glob("*.md"):
                    rule_parts.append(pr_path.read_text(encoding="utf-8").strip())

        (rules_target_dir / "AGENTS.md").write_text("\n\n---\n\n".join(rule_parts), encoding="utf-8")
        rules_consolidated = True
    except Exception as e:
        errors.append(f"Failed to consolidate rules: {e}")

    # 6. Portable Scripts
    try:
        scripts_target_dir = target_plugin_dir / "scripts"
        scripts_target_dir.mkdir(parents=True, exist_ok=True)
        scripts_src = harness_root / "scripts"
        if scripts_src.exists():
            for s_file in scripts_src.glob("*.py"):
                shutil.copy2(s_file, scripts_target_dir / s_file.name)
        for helper_script in ("shift_left_hook.py", "memory_logger.py"):
            helper_src = template_agents / "scripts" / helper_script
            if helper_src.exists():
                shutil.copy2(helper_src, scripts_target_dir / helper_script)
    except Exception as e:
        errors.append(f"Failed to copy portable scripts: {e}")

    # Remove workspace-dependent hooks or stale cache files if present in plugin root
    for stale_file in ("hooks.json", ".update_check.json"):
        if (target_plugin_dir / stale_file).exists():
            (target_plugin_dir / stale_file).unlink()

    return PluginDeploymentResult(
        plugin_dir=target_plugin_dir,
        manifest_updated=manifest_updated,
        skills_copied=skills_copied,
        rules_consolidated=rules_consolidated,
        assets_copied=assets_copied,
        pip_updated=False,
        errors=errors
    )

def check_for_updates(harness_root: Path, branch: str = "main") -> UpdateCheckResult:
    """Checks upstream git repository for commits ahead of local HEAD."""
    git_dir = harness_root / ".git"
    if not git_dir.exists():
        return UpdateCheckResult(
            is_git_repo=False,
            current_commit="",
            remote_commit="",
            has_update=False,
            behind_count=0,
            error="Not a git repository"
        )

    try:
        # Check current commit
        res_head = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=harness_root,
            capture_output=True,
            text=True,
            check=True
        )
        current_commit = res_head.stdout.strip()

        # Fetch remote safely
        subprocess.run(
            ["git", "fetch", "origin", branch],
            cwd=harness_root,
            capture_output=True,
            text=True,
            timeout=10
        )

        # Check remote commit
        res_remote = subprocess.run(
            ["git", "rev-parse", f"origin/{branch}"],
            cwd=harness_root,
            capture_output=True,
            text=True,
            check=True
        )
        remote_commit = res_remote.stdout.strip()

        # Count commits behind
        res_revlist = subprocess.run(
            ["git", "rev-list", f"HEAD..origin/{branch}"],
            cwd=harness_root,
            capture_output=True,
            text=True,
            check=True
        )
        behind_lines = [line.strip() for line in res_revlist.stdout.splitlines() if line.strip()]
        behind_count = len(behind_lines)

        return UpdateCheckResult(
            is_git_repo=True,
            current_commit=current_commit,
            remote_commit=remote_commit,
            has_update=(behind_count > 0),
            behind_count=behind_count,
            error=None
        )
    except Exception as e:
        return UpdateCheckResult(
            is_git_repo=True,
            current_commit="",
            remote_commit="",
            has_update=False,
            behind_count=0,
            error=str(e)
        )

def should_check_for_updates(cache_file: Path, interval_hours: int = 24) -> bool:
    """Returns True if the update cache is missing or older than interval_hours."""
    if not cache_file.exists():
        return True
    try:
        data = json.loads(cache_file.read_text(encoding="utf-8"))
        last_check = float(data.get("last_check_timestamp", 0))
        elapsed = time.time() - last_check
        return elapsed >= (interval_hours * 3600)
    except Exception:
        return True

def save_update_check_state(cache_file: Path, state: dict):
    """Saves update check state to disk if parent exists."""
    try:
        if cache_file.parent.exists():
            state["last_check_timestamp"] = state.get("last_check_timestamp", time.time())
            cache_file.write_text(json.dumps(state, indent=2), encoding="utf-8")
    except Exception:
        pass

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
    if not is_global:
        global_info = detect_global_installation()
        if global_info.is_installed:
            deduplicate_project_scope(target_agents, global_info, dry_run=False)
            print(f"{COLOR_CYAN}[INFO] Global installation detected: deduplicated project skills and rules to prevent conflicts{COLOR_RESET}")
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
        if not os.environ.get("NO_PIP_INSTALL"):
            print(f"\n{COLOR_CYAN}==> Registering 'harness' CLI globally via pip...{COLOR_RESET}")
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", "-e", str(harness_root)], check=True)
                print(f"{COLOR_GREEN}[PASS] Successfully registered 'harness' CLI globally{COLOR_RESET}")
            except Exception as e:
                print(f"{COLOR_YELLOW}Warning: Failed to pip install harness globally: {e}{COLOR_RESET}")
                print(f"{COLOR_YELLOW}Tip: You can manually run: pip install -e {harness_root}{COLOR_RESET}")

        # 6. Antigravity plugin installation: package into ~/.gemini/config/plugins/my-harness
        gemini_plugins_dir = get_gemini_config_dir() / "plugins"
        if gemini_plugins_dir.parent.exists() or os.environ.get("GEMINI_CONFIG_DIR"):
            harness_plugin_dir = get_global_plugin_dir()
            deploy_res = deploy_antigravity_plugin(harness_root, harness_plugin_dir, pack=args.pack)
            if deploy_res.errors:
                print(f"{COLOR_YELLOW}Warning during plugin deployment: {', '.join(deploy_res.errors)}{COLOR_RESET}")
            else:
                print(f"{COLOR_GREEN}[PASS] Installed Antigravity global plugin with all skills and rules ({harness_plugin_dir}){COLOR_RESET}")

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
        print(f"  - harness fix             (Repair structure & deduplicate global conflicts)")
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

def get_git_hooks_dir(repo_root: Path) -> Optional[Path]:
    """Finds the git hooks directory for a repo root."""
    git_dir = repo_root / ".git"
    if not git_dir.exists():
        return None
    if git_dir.is_file():
        # Submodule or gitdir file
        try:
            content = git_dir.read_text(encoding="utf-8").strip()
            if content.startswith("gitdir:"):
                actual_git_dir = (repo_root / content[len("gitdir:"):].strip()).resolve()
                return actual_git_dir / "hooks"
        except Exception:
            return None
    return git_dir / "hooks"

def is_git_hook_installed(repo_root: Path) -> bool:
    """Checks whether the post-merge auto-update hook is installed in repo_root."""
    hooks_dir = get_git_hooks_dir(repo_root)
    if not hooks_dir or not hooks_dir.exists():
        return False
    hook_file = hooks_dir / "post-merge"
    if not hook_file.exists():
        return False
    try:
        content = hook_file.read_text(encoding="utf-8")
        return "harness.py" in content and "update --force" in content
    except Exception:
        return False

def install_git_hooks(repo_root: Path) -> bool:
    """Installs post-merge auto-update hook into .git/hooks/post-merge."""
    hooks_dir = get_git_hooks_dir(repo_root)
    if not hooks_dir:
        return False
    hooks_dir.mkdir(parents=True, exist_ok=True)
    hook_file = hooks_dir / "post-merge"

    hook_content = (
        "#!/bin/sh\n"
        "# my-harness git post-merge auto-update hook\n"
        "# Automatically synchronizes global Antigravity plugin after pull or merge\n"
        "if command -v python3 >/dev/null 2>&1; then\n"
        '    PYTHON_BIN="python3"\n'
        "elif command -v python >/dev/null 2>&1; then\n"
        '    PYTHON_BIN="python"\n'
        "else\n"
        "    exit 0\n"
        "fi\n\n"
        'REPO_DIR="$(cd "$(dirname "$0")/../.." && pwd)"\n'
        'if [ -f "$REPO_DIR/harness.py" ]; then\n'
        '    "$PYTHON_BIN" "$REPO_DIR/harness.py" update --force >/dev/null 2>&1 &\n'
        "fi\n"
    )

    try:
        hook_file.write_text(hook_content, encoding="utf-8")
        # Ensure executable permission on POSIX systems
        try:
            mode = hook_file.stat().st_mode
            hook_file.chmod(mode | 0o755)
        except Exception:
            pass
        return True
    except Exception:
        return False

def cmd_install_hooks(args) -> int:
    target_dir = Path(getattr(args, "target", ".") or ".").resolve()
    print(f"{COLOR_CYAN}==> Installing git hooks in: {target_dir}...{COLOR_RESET}")
    success = install_git_hooks(target_dir)
    if success:
        print(f"{COLOR_GREEN}[PASS] Installed git post-merge auto-update hook (.git/hooks/post-merge){COLOR_RESET}")
        return 0
    else:
        print(f"{COLOR_RED}[FAIL] Could not install git hooks (is {target_dir} a git repository?){COLOR_RESET}")
        return 1

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

    # 4. Branch & Git Hooks check
    try:
        res = subprocess.run(["git", "branch", "--show-current"], cwd=target_dir, capture_output=True, text=True)
        branch = res.stdout.strip()
        print(f"{COLOR_GREEN}[PASS]{COLOR_RESET} Git branch: {branch or 'Detached / No Branch'}")

        if is_git_hook_installed(target_dir):
            print(f"{COLOR_GREEN}[PASS]{COLOR_RESET} Git post-merge auto-update hook active")
        else:
            print(f"{COLOR_YELLOW}[INFO]{COLOR_RESET} Git post-merge auto-update hook not installed. Run 'harness install-hooks' to auto-sync on pull/merge.")
    except Exception:
        print(f"{COLOR_YELLOW}[WARN]{COLOR_RESET} Git repository not initialized or git not in PATH")

    # 5. Global duplicate check
    global_info = detect_global_installation()
    if global_info.is_installed:
        dup_skills = []
        skills_dir = target_agents / "skills"
        if skills_dir.exists():
            for s in skills_dir.iterdir():
                if s.is_dir() and s.name in global_info.global_skills:
                    dup_skills.append(s.name)

        dup_rules = []
        rules_dir = target_agents / "rules"
        if rules_dir.exists():
            for r in rules_dir.glob("*.md"):
                if r.name in global_info.global_rules:
                    dup_rules.append(r.name)

        if dup_skills or dup_rules:
            msg_parts = []
            if dup_skills:
                msg_parts.append(f"{len(dup_skills)} duplicate skill(s) ({', '.join(dup_skills)})")
            if dup_rules:
                msg_parts.append(f"{len(dup_rules)} duplicate rule(s) ({', '.join(dup_rules)})")
            print(f"{COLOR_YELLOW}[WARN]{COLOR_RESET} Global installation detected with {' and '.join(msg_parts)} in project scope. Run 'harness fix' to resolve conflicts.")
        else:
            print(f"{COLOR_GREEN}[PASS]{COLOR_RESET} No duplicate skills/rules with global installation")

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

def cmd_update(args) -> int:
    harness_root = get_harness_root()
    branch = getattr(args, "branch", "main") or "main"
    check_only = getattr(args, "check_only", False)
    force = getattr(args, "force", False)
    sync_project = getattr(args, "sync_project", False)
    target_dir = Path(getattr(args, "target", ".") or ".").resolve()

    print(f"{COLOR_CYAN}==> Checking for my-harness updates (branch: {branch})...{COLOR_RESET}")

    check_res = check_for_updates(harness_root, branch=branch)
    cache_file = get_global_agents_dir() / ".update_check.json"
    save_update_check_state(cache_file, {
        "last_check_timestamp": time.time(),
        "has_update": check_res.has_update,
        "current_commit": check_res.current_commit,
        "remote_commit": check_res.remote_commit,
        "behind_count": check_res.behind_count
    })

    if check_res.error:
        print(f"{COLOR_YELLOW}[WARN] Update check warning: {check_res.error}{COLOR_RESET}")
    elif check_res.has_update:
        print(f"{COLOR_YELLOW}[UPDATE AVAILABLE] Upstream has {check_res.behind_count} new commit(s)!{COLOR_RESET}")
    else:
        print(f"{COLOR_GREEN}[PASS] Repository is up to date with origin/{branch}.{COLOR_RESET}")

    if check_only:
        return 0

    # If git repo and has updates, pull unless local working tree is dirty
    if check_res.is_git_repo and check_res.has_update and not force:
        try:
            status_res = subprocess.run(["git", "status", "--porcelain"], cwd=harness_root, capture_output=True, text=True)
            if status_res.stdout.strip():
                print(f"{COLOR_YELLOW}[WARN] Working directory has uncommitted changes. Skipping 'git pull'. Run with --force to deploy current working tree.{COLOR_RESET}")
            else:
                print(f"{COLOR_CYAN}==> Pulling latest changes from origin/{branch}...{COLOR_RESET}")
                pull_res = subprocess.run(["git", "pull", "--ff-only", "origin", branch], cwd=harness_root, capture_output=True, text=True)
                if pull_res.returncode == 0:
                    print(f"{COLOR_GREEN}[PASS] Successfully pulled latest commits.{COLOR_RESET}")
                else:
                    print(f"{COLOR_YELLOW}[WARN] git pull failed ({pull_res.stderr.strip()}). Proceeding with current files.{COLOR_RESET}")
        except Exception as e:
            print(f"{COLOR_YELLOW}[WARN] Could not pull from git: {e}{COLOR_RESET}")

    # 1. Update global Antigravity plugin
    harness_plugin_dir = get_global_plugin_dir()
    print(f"\n{COLOR_CYAN}==> Updating global Antigravity plugin ({harness_plugin_dir})...{COLOR_RESET}")
    deploy_res = deploy_antigravity_plugin(harness_root, harness_plugin_dir)

    if deploy_res.errors:
        print(f"{COLOR_RED}[FAIL] Plugin deployment encountered errors: {', '.join(deploy_res.errors)}{COLOR_RESET}")
    else:
        print(f"{COLOR_GREEN}[PASS] Updated manifest, skills ({deploy_res.skills_copied}), and consolidated rules.{COLOR_RESET}")

    # 2. Re-register global CLI via pip if in global environment
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-e", str(harness_root)], check=True, capture_output=True)
        print(f"{COLOR_GREEN}[PASS] Refreshed global 'harness' CLI registration.{COLOR_RESET}")
    except Exception as e:
        print(f"{COLOR_YELLOW}[WARN] Could not refresh global pip install: {e}{COLOR_RESET}")

    # 3. Optional: Sync current project .agents/
    if sync_project:
        target_agents = target_dir / ".agents"
        if target_agents.exists():
            print(f"{COLOR_CYAN}==> Syncing project .agents at {target_dir}...{COLOR_RESET}")
            template_agents = harness_root / "template" / ".agents"
            copy_tree_merge(template_agents / "scripts", target_agents / "scripts")
            copy_tree_merge(template_agents / "rules", target_agents / "rules")
            copy_tree_merge(template_agents / "skills", target_agents / "skills")
            print(f"{COLOR_GREEN}[PASS] Project .agents successfully synchronized.{COLOR_RESET}")
        else:
            print(f"{COLOR_YELLOW}[WARN] No .agents directory found in {target_dir}. Skipping project sync.{COLOR_RESET}")

    print(f"\n{COLOR_BOLD}{COLOR_GREEN}✓ my-harness plugin update complete!{COLOR_RESET}")
    print(f"{COLOR_CYAN}Tip: If new skills or slash commands were added, restart Antigravity to reload them.{COLOR_RESET}\n")
    return 0

def cmd_fix(args) -> int:
    target_dir = Path(args.target).resolve()
    target_agents = target_dir / ".agents"
    harness_root = get_harness_root()
    template_agents = harness_root / "template" / ".agents"
    dry_run = getattr(args, "dry_run", False)

    print(f"{COLOR_CYAN}==> Running my-harness Fix on: {target_dir} {'(DRY RUN)' if dry_run else ''}{COLOR_RESET}\n")

    if not target_agents.exists():
        if not dry_run:
            target_agents.mkdir(parents=True, exist_ok=True)
            print(f"{COLOR_YELLOW}[CREATE] Created missing .agents/ directory{COLOR_RESET}")
        else:
            print(f"{COLOR_YELLOW}[DRY RUN] Would create missing .agents/ directory{COLOR_RESET}")

    # 1. Structure repairs
    struct_res = repair_project_structure(target_agents, dry_run=dry_run)
    for cd in struct_res["created_dirs"]:
        prefix = "[DRY RUN] Would create" if dry_run else "[REPAIRED] Created"
        print(f"{COLOR_GREEN}{prefix} missing directory: .agents/{cd}{COLOR_RESET}")

    # 2. Core scripts repairs
    scripts_res = repair_project_scripts(target_agents, template_agents, dry_run=dry_run)
    for rs in scripts_res["restored_scripts"]:
        prefix = "[DRY RUN] Would restore" if dry_run else "[REPAIRED] Restored"
        print(f"{COLOR_GREEN}{prefix} missing script: .agents/scripts/{rs}{COLOR_RESET}")

    # 3. Config repairs
    cfg_res = repair_project_configs(target_dir, target_agents, template_agents, dry_run=dry_run)
    for rc in cfg_res["repaired_configs"]:
        prefix = "[DRY RUN] Would repair" if dry_run else "[REPAIRED] Repaired"
        print(f"{COLOR_GREEN}{prefix} configuration: .agents/{rc}{COLOR_RESET}")

    # 4. Global deduplication
    global_info = detect_global_installation()
    if global_info.is_installed:
        dedup_res = deduplicate_project_scope(target_agents, global_info, dry_run=dry_run)
        for sk in dedup_res["removed_skills"]:
            prefix = "[DRY RUN] Would remove duplicate skill" if dry_run else "[REMOVED] Duplicate skill"
            print(f"{COLOR_YELLOW}{prefix}: .agents/skills/{sk} (provided globally){COLOR_RESET}")
        for rk in dedup_res["removed_rules"]:
            prefix = "[DRY RUN] Would remove duplicate rule" if dry_run else "[REMOVED] Duplicate rule"
            print(f"{COLOR_YELLOW}{prefix}: .agents/rules/{rk} (provided globally){COLOR_RESET}")

        if dedup_res["preserved_skills"]:
            print(f"{COLOR_CYAN}[INFO] Preserved custom project skill(s): {', '.join(dedup_res['preserved_skills'])}{COLOR_RESET}")
        if dedup_res["preserved_rules"]:
            print(f"{COLOR_CYAN}[INFO] Preserved custom project rule(s): {', '.join(dedup_res['preserved_rules'])}{COLOR_RESET}")
    else:
        print(f"{COLOR_CYAN}[INFO] No global installation detected; skipping deduplication.{COLOR_RESET}")

    print(f"\n{COLOR_BOLD}{COLOR_GREEN}✓ Project repair & deduplication complete!{COLOR_RESET}")
    return 0

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="my-harness — Reusable Agent Engineering Harness")
    subparsers = parser.add_subparsers(dest="subcommand", help="Harness command to run")

    # init
    p_init = subparsers.add_parser("init", help="Initialize .agents harness in a target project or globally")
    p_init.add_argument("target", nargs="?", default=".", help="Target project directory (default: current directory)")
    p_init.add_argument("--scope", choices=["project", "global"], default="project", help="Installation scope: project (target directory) or global (user home ~/.agents and CLI)")
    p_init.add_argument("--preset", default="universal", help="Configuration preset name")
    p_init.add_argument("--pack", help="Optional pack to install during init (e.g. orbit-desktop, vue-primevue)")

    # fix
    p_fix = subparsers.add_parser("fix", help="Repair project-scope .agents setup and remove duplicates if globally installed")
    p_fix.add_argument("target", nargs="?", default=".", help="Target project directory (default: current directory)")
    p_fix.add_argument("--dry-run", action="store_true", help="Preview repairs and deduplications without making changes")

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

    # install-hooks
    p_hooks = subparsers.add_parser("install-hooks", help="Install git post-merge auto-update hook in target repository")
    p_hooks.add_argument("target", nargs="?", default=".", help="Target git repository directory (default: current directory)")

    # update
    p_update = subparsers.add_parser("update", help="Update my-harness plugin and global CLI from git upstream")
    p_update.add_argument("target", nargs="?", default=".", help="Target project directory if syncing project")
    p_update.add_argument("--check-only", action="store_true", help="Only check for available updates without modifying files")
    p_update.add_argument("--force", action="store_true", help="Force re-packaging and re-deploying plugin even if clean or dirty")
    p_update.add_argument("--sync-project", action="store_true", help="Also sync current project .agents/ directory")
    p_update.add_argument("--branch", default="main", help="Git branch to check/pull from (default: main)")

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
    elif args.subcommand == "fix":
        sys.exit(cmd_fix(args))
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
    elif args.subcommand == "install-hooks":
        sys.exit(cmd_install_hooks(args))
    elif args.subcommand == "update":
        sys.exit(cmd_update(args))

if __name__ == "__main__":
    main()

"""
eval_skill.py - Automated Contract & Regression Evaluator for Agent Skills.
Runs static evaluation assertions against SKILL.md to ensure safety,
cross-platform compatibility, and anti-exhaustion best practices.
"""

import sys
import json
import re
from pathlib import Path

# Force utf-8 for stdout if possible
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

def run_evals(spec_file: Path) -> bool:
    if not spec_file.exists():
        print(f"[ERROR] Spec file not found: {spec_file}")
        return False

    with open(spec_file, "r", encoding="utf-8") as f:
        cases = json.load(f)

    skill_dir = spec_file.parent.parent
    passed = 0
    failed = 0

    print(f"\n[EVALS] Running Evals for Skill: {skill_dir.name}")
    print(f"Loaded {len(cases)} evaluation criteria from {spec_file.name}\n" + "-" * 60)

    for case in cases:
        case_id = case.get("id")
        desc = case.get("description")
        target_name = case.get("target_file", "SKILL.md")
        target_path = skill_dir / target_name

        if not target_path.exists():
            print(f"[FAIL] [{case_id}]: Target file {target_name} does not exist.")
            failed += 1
            continue

        content = target_path.read_text(encoding="utf-8")
        errors = []

        # Check required patterns
        for pattern in case.get("required_patterns", []):
            if not re.search(pattern, content, re.IGNORECASE):
                errors.append(f"Missing required pattern: '{pattern}'")

        # Check prohibited patterns
        for pattern in case.get("prohibited_patterns", []):
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                errors.append(f"Found prohibited pattern: '{pattern}' ({len(matches)} occurrences)")

        if errors:
            print(f"[FAIL] [{case_id}] - {desc}")
            for err in errors:
                print(f"   -> {err}")
            if "explanation" in case:
                print(f"   [INFO] Rationale: {case['explanation']}")
            failed += 1
        else:
            print(f"[PASS] [{case_id}] - {desc}")
            passed += 1

    print("-" * 60)
    print(f"Summary: {passed} passed, {failed} failed out of {len(cases)} checks.\n")
    return failed == 0

if __name__ == "__main__":
    current_dir = Path(__file__).parent
    spec_path = current_dir / "eval_specs.json"
    success = run_evals(spec_path)
    sys.exit(0 if success else 1)

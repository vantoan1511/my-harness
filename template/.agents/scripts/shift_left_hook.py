#!/usr/bin/env python3
"""
shift_left_hook.py — PreInvocation Lifecycle Hook for Shift-Left Quality

Inspects the user's latest request in transcript.jsonl. If the user is requesting
implementation, planning, bug fixing, or refactoring, injects an ephemeral
system reminder to guide the agent toward shift-left practices (TDD, contract-first,
pre-flight scanning). Reminders are dynamically loaded from harness.config.json.
"""

import sys
import os
import json
import re
import subprocess
from pathlib import Path

# Ensure UTF-8 output on Windows consoles
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

SHIFT_LEFT_KEYWORDS = [
    r"/implement\b",
    r"/plan\b",
    r"/prp-plan\b",
    r"/specify\b",
    r"\bimplement\b",
    r"\brefactor\b",
    r"\bfix\b",
    r"\badd\s+feature\b",
    r"\bcreate\b",
    r"\bbuild\b",
    r"\bupdate\b"
]

DEFAULT_REMINDERS = [
    "1. Contract-First: Define interfaces, schemas & types before implementing logic.",
    "2. TDD: Write failing tests before writing production code.",
    "3. Micro-Validation: Run `python .agents/scripts/verify_shift_left.py --changed` after every file edit.",
    "4. Branch Safety: Never commit directly to main/master."
]

def get_repo_root(payload: dict = None) -> Path:
    if payload:
        ws_paths = payload.get("workspacePaths")
        if isinstance(ws_paths, list) and ws_paths:
            cand = Path(ws_paths[0])
            if cand.exists():
                return cand
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
            except Exception:
                pass
    return {}

def main():
    try:
        if not sys.stdin.isatty():
            payload = json.load(sys.stdin)
        else:
            payload = {}

        transcript_path = payload.get("transcriptPath")
        if not transcript_path or not os.path.exists(transcript_path):
            print(json.dumps({}))
            return

        latest_user_request = ""
        with open(transcript_path, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    step = json.loads(line)
                    if step.get("type") == "USER_INPUT":
                        content = step.get("content", "")
                        match = re.search(r"<USER_REQUEST>\n?(.*?)\n?</USER_REQUEST>", content, re.DOTALL)
                        if match:
                            latest_user_request = match.group(1).strip()
                        else:
                            latest_user_request = content.strip()
                except Exception:
                    pass

        # Check if request matches dev/planning keywords
        is_dev_request = any(re.search(pat, latest_user_request, re.IGNORECASE) for pat in SHIFT_LEFT_KEYWORDS)

        if is_dev_request:
            root = get_repo_root(payload)
            config = load_config(root)
            reminders = config.get("guardrails", {}).get("reminders", DEFAULT_REMINDERS)
            reminder_text = "[Shift-Left Quality Guardrail]\n" + "\n".join(reminders)

            print(json.dumps({
                "injectSteps": [
                    {
                        "ephemeralMessage": reminder_text
                    }
                ]
            }))
        else:
            print(json.dumps({}))

    except Exception:
        # Never crash the agent loop
        print(json.dumps({}))

if __name__ == "__main__":
    main()

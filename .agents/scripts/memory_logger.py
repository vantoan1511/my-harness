#!/usr/bin/env python3
"""
memory_logger.py — Agent Memory and Correction Logger

Logs user corrections, explicit instructions, and rules into markdown logs (.agents/logs/YYYY-MM-DD.md).
Can run as a PreInvocation lifecycle hook or as a standalone CLI tool.
"""

import os
import sys
import re
import json
import subprocess
from datetime import datetime
from pathlib import Path

# Ensure UTF-8 output on Windows consoles
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

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
        # Fallback to parent of .agents
        return Path(__file__).resolve().parent.parent.parent

def is_memory_or_correction(text: str) -> bool:
    """
    Checks if the user input is asking to remember something or correcting a mistake.
    """
    text_lower = text.lower()

    # Keywords for remembering/memorizing
    memory_keywords = [
        r"remember",
        r"memorize",
        r"keep this in mind",
        r"note this",
        r"take note",
        r"always do",
        r"never do",
        r"\brule\b",
        r"\bconvention\b"
    ]

    # Keywords for corrections
    correction_keywords = [
        r"did .* wrong",
        r"that is wrong",
        r"that's wrong",
        r"don't do that",
        r"instead of",
        r"change that",
        r"change how",
        r"fix that",
        r"next time",
        r"made a mistake",
        r"incorrect",
        r"you should have",
        r"supposed to"
    ]

    for pattern in memory_keywords + correction_keywords:
        if re.search(pattern, text_lower):
            return True

    return False

def log_interaction(user_input: str, tool_calls: list = None, base_dir: Path = None) -> bool:
    """
    Logs the user input if it contains memory or correction requests.
    """
    if not is_memory_or_correction(user_input):
        return False

    if base_dir is None:
        base_dir = get_repo_root() / ".agents" / "logs"

    os.makedirs(base_dir, exist_ok=True)

    today = datetime.now().strftime("%Y-%m-%d")
    filepath = base_dir / f"{today}.md"
    timestamp = datetime.now().strftime("%H:%M:%S")

    with open(filepath, "a", encoding="utf-8") as f:
        f.write(f"## Time: {timestamp}\n")
        f.write(f"**User Request:** {user_input}\n")
        if tool_calls:
            for tc in tool_calls:
                f.write(f"**System:** {tc}\n")
        f.write("\n")

    return True

def handle_hook(log_dir: Path):
    """
    Hook mode: read JSON from stdin, extract input and tool calls, log if relevant.
    """
    try:
        if sys.stdin.isatty():
            print(json.dumps({}))
            return

        payload = json.load(sys.stdin)
        transcript_path = payload.get("transcriptPath")

        if transcript_path and os.path.exists(transcript_path):
            latest_user_input = None
            latest_step_idx = -1
            session_tool_calls = []

            with open(transcript_path, "r", encoding="utf-8") as f:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        step = json.loads(line)
                        step_type = step.get("type")

                        if step_type == "USER_INPUT":
                            content = step.get("content", "")
                            match = re.search(r"<USER_REQUEST>\n?(.*?)\n?</USER_REQUEST>", content, re.DOTALL)
                            if match:
                                latest_user_input = match.group(1).strip()
                            else:
                                latest_user_input = content.strip()
                            latest_step_idx = step.get("step_index", -1)

                        elif step_type == "PLANNER_RESPONSE":
                            tcs = step.get("tool_calls", [])
                            for tc in tcs:
                                name = tc.get("name", "unknown")
                                args = tc.get("args", {})
                                if not isinstance(args, dict):
                                    args = {}
                                summary = args.get("toolSummary", args.get("toolAction", "do something"))
                                if isinstance(summary, str):
                                    summary = summary.strip('"\'')
                                session_tool_calls.append(f'Use tool "{name}" to {summary}')
                    except json.JSONDecodeError:
                        pass

            conversation_id = payload.get("conversationId", "default")
            tracker_file = log_dir / f".last_logged_step_{conversation_id}"
            last_logged = -1
            if tracker_file.exists():
                try:
                    last_logged = int(tracker_file.read_text(encoding="utf-8").strip() or "-1")
                except Exception:
                    last_logged = -1

            if latest_user_input and latest_step_idx > last_logged:
                logged = log_interaction(latest_user_input, tool_calls=session_tool_calls, base_dir=log_dir)
                if logged:
                    os.makedirs(log_dir, exist_ok=True)
                    tracker_file.write_text(str(latest_step_idx), encoding="utf-8")

        print(json.dumps({}))
    except Exception:
        # Never fail or crash agent hook
        print(json.dumps({}))

def main():
    root = get_repo_root()
    log_dir = root / ".agents" / "logs"

    if len(sys.argv) > 1 and sys.argv[1] == "--hook":
        handle_hook(log_dir)
    elif len(sys.argv) > 1:
        text = " ".join(sys.argv[1:])
        logged = log_interaction(text, base_dir=log_dir)
        if logged:
            print("Interaction logged to memory.")
        else:
            print("Interaction did not match memory or correction criteria.")
    else:
        print("Usage: python memory_logger.py \"your text here\"")
        print("       python memory_logger.py --hook (reads JSON from stdin)")
        print("Interactive mode (type 'exit' to quit):")
        while True:
            try:
                user_input = input("> ")
                if user_input.strip().lower() in ['exit', 'quit']:
                    break
                if not user_input.strip():
                    continue
                logged = log_interaction(user_input, base_dir=log_dir)
                if logged:
                    print("-> Saved to memory log.")
            except (EOFError, KeyboardInterrupt):
                break

if __name__ == "__main__":
    main()

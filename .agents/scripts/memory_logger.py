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

def _is_step_failure(step: dict) -> tuple[bool, str]:
    if step.get("status") == "ERROR":
        content = step.get("content", "")
        return True, content[:100] if content else "Step marked as ERROR"
    content = step.get("content", "")
    if isinstance(content, str):
        if "Command exited with code 1" in content or "exit code" in content.lower():
            return True, content[:100]
    return False, ""

def extract_trajectory_failures(steps: list[dict], min_streak: int = 2) -> list[dict]:
    failures = []
    curr_streak = 0
    streak_summaries = []

    for step in steps:
        if step.get("type") == "USER_INPUT":
            curr_streak = 0
            streak_summaries = []
            continue

        failed, desc = _is_step_failure(step)
        if failed:
            curr_streak += 1
            if desc:
                streak_summaries.append(desc.strip())
            if curr_streak >= min_streak and curr_streak == min_streak:
                summary = "; ".join(streak_summaries[-min_streak:])
                failures.append({
                    "streak_length": curr_streak,
                    "summary": summary or f"Streak of {curr_streak} tool failures"
                })
        else:
            curr_streak = 0
            streak_summaries = []

    return failures

def log_trajectory_failures(failures: list[dict], base_dir: Path = None) -> bool:
    if not failures:
        return False
    if base_dir is None:
        base_dir = get_repo_root() / ".agents" / "logs"
    os.makedirs(base_dir, exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")
    filepath = base_dir / f"{today}.md"
    timestamp = datetime.now().strftime("%H:%M:%S")

    with open(filepath, "a", encoding="utf-8") as f:
        for f_rec in failures:
            f.write(f"## Time: {timestamp}\n")
            f.write(f"**Trajectory Failure:** streak: {f_rec['streak_length']} consecutive failures ({f_rec['summary']})\n\n")
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
        if log_dir is None:
            log_dir = get_repo_root(payload) / ".agents" / "logs"
        transcript_path = payload.get("transcriptPath")

        if transcript_path and os.path.exists(transcript_path):
            latest_user_input = None
            latest_step_idx = -1
            session_tool_calls = []
            raw_steps = []

            with open(transcript_path, "r", encoding="utf-8") as f:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        step = json.loads(line)
                        raw_steps.append(step)
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

            did_log = False
            if latest_user_input and latest_step_idx > last_logged:
                logged = log_interaction(latest_user_input, tool_calls=session_tool_calls, base_dir=log_dir)
                if logged:
                    did_log = True

            # Also check trajectory failure streaks across parsed steps
            if 'raw_steps' in locals() and raw_steps:
                failures = extract_trajectory_failures(raw_steps, min_streak=2)
                if failures and latest_step_idx > last_logged:
                    logged_fail = log_trajectory_failures(failures, base_dir=log_dir)
                    if logged_fail:
                        did_log = True

            if did_log:
                os.makedirs(log_dir, exist_ok=True)
                tracker_file.write_text(str(latest_step_idx), encoding="utf-8")

        print(json.dumps({}))
    except Exception:
        # Never fail or crash agent hook
        print(json.dumps({}))

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--hook":
        handle_hook(None)
    elif len(sys.argv) > 1:
        root = get_repo_root()
        log_dir = root / ".agents" / "logs"
        text = " ".join(sys.argv[1:])
        logged = log_interaction(text, base_dir=log_dir)
        if logged:
            print("Interaction logged to memory.")
        else:
            print("Interaction did not match memory or correction criteria.")
    else:
        root = get_repo_root()
        log_dir = root / ".agents" / "logs"
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

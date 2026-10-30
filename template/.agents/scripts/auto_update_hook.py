#!/usr/bin/env python3
"""
auto_update_hook.py — Non-Blocking SessionStart Auto-Updater (Claude Code style)

Runs on Antigravity `SessionStart`:
1. If a background update completed since the previous session (`just_updated: true`),
   clears the flag and injects a one-line system notification.
2. If the update throttle interval (default: 6 hours) has elapsed, immediately
   spawns a detached background process (`harness.py update --quiet`) so session
   startup never blocks (< 15ms).
"""

import json
import os
import subprocess
import sys
import time
from pathlib import Path

# Ensure UTF-8 output on Windows consoles
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


def get_default_cache_file() -> Path:
    env_dir = os.environ.get("AGENTS_GLOBAL_DIR")
    if env_dir:
        return Path(env_dir) / ".update_check.json"
    return Path.home() / ".agents" / ".update_check.json"


def spawn_detached_update(harness_script: Path):
    """Spawns `python harness.py update` in a fully detached background process."""
    cmd = [sys.executable, str(harness_script), "update"]
    kwargs = {
        "stdin": subprocess.DEVNULL,
        "stdout": subprocess.DEVNULL,
        "stderr": subprocess.DEVNULL,
        "cwd": str(harness_script.parent),
    }
    if os.name == "nt":
        # Detached process flags on Windows
        CREATE_NEW_PROCESS_GROUP = 0x00000200
        DETACHED_PROCESS = 0x00000008
        kwargs["creationflags"] = CREATE_NEW_PROCESS_GROUP | DETACHED_PROCESS
    else:
        kwargs["start_new_session"] = True

    subprocess.Popen(cmd, **kwargs)


def run_session_start_check(cache_file: Path = None, interval_hours: int = 6) -> dict:
    """
    Evaluates update cache state, spawns background updater if due,
    and returns the SessionStart hook response dict.
    """
    if cache_file is None:
        cache_file = get_default_cache_file()

    state = {}
    if cache_file.exists():
        try:
            state = json.loads(cache_file.read_text(encoding="utf-8"))
        except Exception:
            state = {}

    response = {}

    # 1. Check if a background update finished since last session
    if state.get("just_updated"):
        commit_short = str(state.get("updated_to_commit", ""))[:7] or "latest"
        state["just_updated"] = False
        try:
            cache_file.parent.mkdir(parents=True, exist_ok=True)
            cache_file.write_text(json.dumps(state, indent=2), encoding="utf-8")
        except Exception:
            pass

        response = {
            "injectSteps": [
                {
                    "systemMessage": {
                        "systemMessage": (
                            f"[my-harness] Auto-updated plugin in the background to {commit_short}. "
                            "Restart Antigravity if new skills or slash commands were added."
                        )
                    }
                }
            ]
        }

    # 2. Check if throttle interval has elapsed
    last_check = float(state.get("last_check_timestamp", 0))
    now = time.time()
    if (now - last_check) >= (interval_hours * 3600):
        source_repo = state.get("source_repo")
        harness_script = Path(source_repo) / "harness.py" if source_repo else None

        if harness_script and harness_script.exists():
            # Optimistically bump timestamp first so concurrent sessions don't stampede
            state["last_check_timestamp"] = now
            try:
                cache_file.parent.mkdir(parents=True, exist_ok=True)
                cache_file.write_text(json.dumps(state, indent=2), encoding="utf-8")
            except Exception:
                pass

            try:
                spawn_detached_update(harness_script)
            except Exception:
                pass

    return response


def main():
    try:
        # Consume stdin if provided by Antigravity hook runner
        if not sys.stdin.isatty():
            try:
                sys.stdin.read()
            except Exception:
                pass

        res = run_session_start_check()
        print(json.dumps(res))
    except Exception:
        # Never crash or block SessionStart
        print(json.dumps({}))


if __name__ == "__main__":
    main()

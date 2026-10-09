#!/usr/bin/env python3
import os
import glob
import sys

# Ensure UTF-8 output on Windows consoles
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def analyze_logs(log_dir):
    if not os.path.exists(log_dir):
        print(f"Log directory {log_dir} does not exist.")
        return

    log_files = glob.glob(os.path.join(log_dir, "*.md"))
    if not log_files:
        print(f"No markdown log files found in {log_dir}.")
        return

    print(f"Found {len(log_files)} log files. Extracting user requests...\n")

    all_requests = []

    for log_file in log_files:
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except Exception:
            continue

        current_time = None
        for line in lines:
            if line.startswith("## Time:"):
                current_time = line.strip().replace("## Time: ", "")
            elif line.startswith("**User Request:**"):
                request = line.strip().replace("**User Request:** ", "")
                all_requests.append({
                    'file': os.path.basename(log_file),
                    'time': current_time,
                    'request': request
                })

    if not all_requests:
        print("No user requests found in logs.")
        return

    print("--- Extracted User Requests ---")
    for req in all_requests:
        print(f"[{req['file']} {req['time']}] {req['request']}")

    print("\n--- Summary ---")
    print(f"Total extracted requests: {len(all_requests)}")
    print("Agent: Please analyze the above requests to identify repeated patterns, corrections, and tasks.")
    print("If you see repeated corrections, please create or update rules in .agents/rules/ or AGENTS.md.")
    print("If you see repeated tasks/steps without reasoning, please create executable scripts in .agents/scripts/.")

if __name__ == "__main__":
    log_directory = sys.argv[1] if len(sys.argv) > 1 else ".agents/logs"
    analyze_logs(log_directory)

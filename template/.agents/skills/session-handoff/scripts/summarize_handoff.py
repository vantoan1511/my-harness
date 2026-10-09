#!/usr/bin/env python3
import argparse
import datetime
import os
import sys

# Ensure UTF-8 output on Windows consoles
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def create_handoff_summary(goal, outcomes, next_steps, issues, output_file=None):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    markdown_content = f"""# Session Handoff Summary
**Date:** {now}

## Goal
{goal}

## Outcomes
{outcomes}

## Next Steps
{next_steps}

## Open Issues / Notes
{issues}
"""

    if not output_file:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        handoffs_dir = os.path.join(".agents", "handoffs")
        os.makedirs(handoffs_dir, exist_ok=True)
        output_file = os.path.join(handoffs_dir, f"handoff_summary_{timestamp}.md")

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(markdown_content)

    print(f"Handoff summary written to {os.path.abspath(output_file)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a handoff summary markdown file.")
    parser.add_argument("--goal", required=True, help="The main goal of the session")
    parser.add_argument("--outcomes", required=True, help="The outcomes achieved")
    parser.add_argument("--next-steps", required=True, help="Next steps to be taken")
    parser.add_argument("--issues", default="None", help="Any open issues or notes")
    parser.add_argument("--output", help="Output file name (optional)")

    args = parser.parse_args()
    create_handoff_summary(args.goal, args.outcomes, args.next_steps, args.issues, args.output)

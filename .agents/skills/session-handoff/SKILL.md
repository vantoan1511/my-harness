---
name: session-handoff
description: >-
  Use this skill when the user asks to summarize the current session or hand off the current work.
  It helps record the goal, outcomes, next steps, and open issues into a markdown file using a Python script.
---

# Session Handoff

This skill helps summarize the current session to hand off work cleanly to the next developer or agent.

## Steps

1. Analyze the current conversation and recent activities to determine:
   - The main **Goal** of the session.
   - The **Outcomes** (what was achieved, created, or modified).
   - The **Next Steps** (what needs to be done next).
   - Any **Open Issues** or important notes for the next session.
2. If any of the above information is unclear, ask the user for clarification before generating the summary.
3. Run the Python script to generate the handoff summary document (supports both local project and global plugin paths):
   ```bash
   python -c "import os, sys, subprocess; cand = next((p for p in ['.agents/skills/session-handoff/scripts/summarize_handoff.py', os.path.expanduser('~/.gemini/config/plugins/my-harness/skills/session-handoff/scripts/summarize_handoff.py'), os.path.expanduser('~/.agents/skills/session-handoff/scripts/summarize_handoff.py')] if os.path.exists(p)), None); sys.exit(subprocess.run([sys.executable, cand] + sys.argv[1:]).returncode if cand else 1)" \
     --goal "<insert goal>" \
     --outcomes "<insert outcomes>" \
     --next-steps "<insert next steps>" \
     --issues "<insert open issues>"
   ```
4. Review the generated file and present a link to it for the user to review.

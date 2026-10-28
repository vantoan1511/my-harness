---
name: agent-log-analyzer
description: Analyze agent log files under .agents/logs/*. Extract repeated user requests, corrections, and propose workspace rules or scripts.
---

# Agent Log Analyzer

Analyze agent interactions and corrections logged in `.agents/logs/`.

## Steps

1. Run the analysis script (supports both local project and global plugin paths):
   ```bash
   python -c "import os, sys, subprocess; cand = next((p for p in ['.agents/skills/agent-log-analyzer/scripts/analyze.py', os.path.expanduser('~/.gemini/config/plugins/my-harness/skills/agent-log-analyzer/scripts/analyze.py'), os.path.expanduser('~/.agents/skills/agent-log-analyzer/scripts/analyze.py')] if os.path.exists(p)), None); sys.exit(subprocess.run([sys.executable, cand] + sys.argv[1:]).returncode if cand else 1)"
   ```
2. Review extracted user requests and corrections.
3. If repeated corrections or rules are found:
   - Propose or update rules in `.agents/rules/` or project `AGENTS.md`.
4. If repeated deterministic tasks are identified:
   - Propose automation scripts in `.agents/scripts/`.

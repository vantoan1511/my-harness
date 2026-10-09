---
name: agent-log-analyzer
description: Analyze agent log files under .agents/logs/*. Extract repeated user requests, corrections, and propose workspace rules or scripts.
---

# Agent Log Analyzer

Analyze agent interactions and corrections logged in `.agents/logs/`.

## Steps

1. Run the analysis script:
   ```bash
   python .agents/skills/agent-log-analyzer/scripts/analyze.py
   ```
2. Review extracted user requests and corrections.
3. If repeated corrections or rules are found:
   - Propose or update rules in `.agents/rules/` or project `AGENTS.md`.
4. If repeated deterministic tasks are identified:
   - Propose automation scripts in `.agents/scripts/`.

import unittest
import tempfile
import shutil
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / ".agents" / "scripts"))

import curate_knowledge

class TestL5KnowledgeCuration(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.addCleanup(lambda: shutil.rmtree(self.temp_dir, ignore_errors=True))
        self.base_dir = Path(self.temp_dir) / ".agents"
        self.base_dir.mkdir(parents=True)
        (self.base_dir / "PRPs" / "reports").mkdir(parents=True)
        (self.base_dir / "references" / "gotchas").mkdir(parents=True)

    def test_extract_self_review_findings(self):
        report_content = (
            "# Implementation Report: Test\n\n"
            "## Self-Review & Adaptation Log\n\n"
            "| # | Severity | File | Issue | Adaptation Applied | Status |\n"
            "|---|---|---|---|---|---|\n"
            "| 1 | [HIGH/MEDIUM/LOW] | `path/to/file` | [finding] | [fix applied] | [done] |\n"
            "| 2 | HIGH | `src/auth.py` | Missing token verification | Added jwt.verify call | [done] Adapted |\n"
            "| 3 | MEDIUM | `src/utils.py` | Function too long (>50 LOC) | Extracted helper func | [done] Adapted |\n"
            "| 4 | LOW | `src/styles.css` | Extra whitespace | Kept for readability | Logged |\n\n"
            "## Files Changed\n"
        )
        report_file = self.base_dir / "PRPs" / "reports" / "feat-auth-report.md"
        report_file.write_text(report_content, encoding="utf-8")

        findings = curate_knowledge.extract_self_review_findings(self.base_dir)
        self.assertEqual(len(findings), 2)  # HIGH and MEDIUM, ignoring template placeholder and LOW
        self.assertEqual(findings[0]["severity"], "HIGH")
        self.assertEqual(findings[0]["file_target"], "`src/auth.py`")
        self.assertIn("token verification", findings[0]["issue"])
        self.assertEqual(findings[1]["severity"], "MEDIUM")

    def test_persist_curated_gotchas_creates_file_and_is_idempotent(self):
        findings = [
            {
                "report": "feat-auth-report.md",
                "severity": "HIGH",
                "file_target": "`src/auth.py`",
                "issue": "Missing token verification in auth route",
                "adaptation": "Added jwt.verify call before processing payload"
            }
        ]
        issues = [
            {
                "file": "feat-auth-report.md",
                "section": "Deviations",
                "text": "Switched from PyJWT to Authlib due to alg mismatch"
            }
        ]

        # First run creates file
        out_file = curate_knowledge.persist_curated_gotchas(self.base_dir, findings, issues)
        self.assertIsNotNone(out_file)
        self.assertTrue(out_file.exists())
        content_1 = out_file.read_text(encoding="utf-8")
        self.assertIn("Auto-Curated Gotchas & Operational Traps", content_1)
        self.assertIn("Missing token verification in auth route", content_1)
        self.assertIn("Switched from PyJWT to Authlib", content_1)

        # Second run is idempotent (no duplicate entries)
        curate_knowledge.persist_curated_gotchas(self.base_dir, findings, issues)
        content_2 = out_file.read_text(encoding="utf-8")
        self.assertEqual(content_1, content_2)

    def test_template_parity_curate_knowledge(self):
        p1 = REPO_ROOT / ".agents" / "scripts" / "curate_knowledge.py"
        p2 = REPO_ROOT / "template" / ".agents" / "scripts" / "curate_knowledge.py"
        self.assertEqual(
            p1.read_text(encoding="utf-8"),
            p2.read_text(encoding="utf-8"),
            "curate_knowledge.py must be byte-for-byte identical with template"
        )

    def test_template_parity_implement_skill(self):
        p1 = REPO_ROOT / ".agents" / "skills" / "implement" / "SKILL.md"
        p2 = REPO_ROOT / "template" / ".agents" / "skills" / "implement" / "SKILL.md"
        self.assertEqual(
            p1.read_text(encoding="utf-8"),
            p2.read_text(encoding="utf-8"),
            "implement/SKILL.md must be byte-for-byte identical with template"
        )
        self.assertIn("curate_knowledge.py --persist", p1.read_text(encoding="utf-8"))

    def test_extract_trajectory_failures_detected(self):
        import memory_logger
        steps = [
            {"step_index": 1, "type": "USER_INPUT", "content": "run tests"},
            {"step_index": 2, "type": "PLANNER_RESPONSE", "status": "ERROR", "tool_calls": [{"name": "run_command"}]},
            {"step_index": 3, "type": "GENERIC", "status": "ERROR", "content": "Command exited with code 1"},
            {"step_index": 4, "type": "PLANNER_RESPONSE", "status": "DONE"}
        ]
        failures = memory_logger.extract_trajectory_failures(steps, min_streak=2)
        self.assertEqual(len(failures), 1)
        self.assertEqual(failures[0]["streak_length"], 2)
        self.assertIn("Command exited with code 1", failures[0]["summary"])

    def test_extract_trajectory_failures_ignores_single_failure(self):
        import memory_logger
        steps = [
            {"step_index": 1, "type": "USER_INPUT", "content": "run tests"},
            {"step_index": 2, "type": "PLANNER_RESPONSE", "status": "ERROR", "tool_calls": [{"name": "run_command"}]},
            {"step_index": 3, "type": "PLANNER_RESPONSE", "status": "DONE"}
        ]
        failures = memory_logger.extract_trajectory_failures(steps, min_streak=2)
        self.assertEqual(len(failures), 0)

    def test_log_trajectory_failures_writes_to_log(self):
        import memory_logger
        failures = [
            {"streak_length": 2, "summary": "Tool error: Command exited with code 1"}
        ]
        logs_dir = self.base_dir / "logs"
        res = memory_logger.log_trajectory_failures(failures, base_dir=logs_dir)
        self.assertTrue(res)
        log_files = list(logs_dir.glob("*.md"))
        self.assertEqual(len(log_files), 1)
        content = log_files[0].read_text(encoding="utf-8")
        self.assertIn("**Trajectory Failure:**", content)
        self.assertIn("streak: 2 consecutive failures", content)

    def test_analyze_script_extracts_user_requests_and_trajectory_failures(self):
        import subprocess
        logs_dir = self.base_dir / "logs"
        logs_dir.mkdir(parents=True, exist_ok=True)
        log_file = logs_dir / "2026-11-06.md"
        log_file.write_text(
            "## Time: 12:00:00\n"
            "**User Request:** please remember to test\n\n"
            "## Time: 12:05:00\n"
            "**Trajectory Failure:** streak: 2 consecutive failures (Command exited with code 1)\n",
            encoding="utf-8"
        )
        script_path = REPO_ROOT / ".agents" / "skills" / "agent-log-analyzer" / "scripts" / "analyze.py"
        res = subprocess.run([sys.executable, str(script_path), str(logs_dir)], capture_output=True, text=True, check=True)
        self.assertIn("please remember to test", res.stdout)
        self.assertIn("Trajectory Failure", res.stdout)

    def test_template_parity_memory_logger_and_analyzer(self):
        p1 = REPO_ROOT / ".agents" / "scripts" / "memory_logger.py"
        p2 = REPO_ROOT / "template" / ".agents" / "scripts" / "memory_logger.py"
        self.assertEqual(p1.read_text(encoding="utf-8"), p2.read_text(encoding="utf-8"))

        a1 = REPO_ROOT / ".agents" / "skills" / "agent-log-analyzer" / "scripts" / "analyze.py"
        a2 = REPO_ROOT / "template" / ".agents" / "skills" / "agent-log-analyzer" / "scripts" / "analyze.py"
        self.assertEqual(a1.read_text(encoding="utf-8"), a2.read_text(encoding="utf-8"))

if __name__ == "__main__":
    unittest.main()

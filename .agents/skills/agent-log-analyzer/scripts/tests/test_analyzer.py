import unittest
import json
import tempfile
import os
import sys

# Add script directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from analyze import TranscriptAnalyzer

class TestTranscriptAnalyzer(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.test_dir.cleanup()

    def test_detect_duplicate_tool_calls(self):
        sample_transcript = [
            {"step_index": 0, "source": "USER_EXPLICIT", "type": "USER_INPUT", "content": "Check status"},
            {"step_index": 1, "source": "MODEL", "type": "PLANNER_RESPONSE", "tool_calls": [
                {"name": "run_command", "args": {"CommandLine": "git status"}}
            ]},
            {"step_index": 2, "source": "MODEL", "type": "GENERIC", "content": "fatal: not a git repo"},
            {"step_index": 3, "source": "MODEL", "type": "PLANNER_RESPONSE", "tool_calls": [
                {"name": "run_command", "args": {"CommandLine": "git status"}}
            ]},
            {"step_index": 4, "source": "MODEL", "type": "GENERIC", "content": "fatal: not a git repo"}
        ]
        file_path = os.path.join(self.test_dir.name, "transcript.jsonl")
        with open(file_path, "w", encoding="utf-8") as f:
            for line in sample_transcript:
                f.write(json.dumps(line) + "\n")

        analyzer = TranscriptAnalyzer()
        results = analyzer.analyze_transcript(file_path)

        self.assertIn("duplicate_tool_calls", results)
        self.assertEqual(len(results["duplicate_tool_calls"]), 1)
        dup = results["duplicate_tool_calls"][0]
        self.assertEqual(dup["tool_name"], "run_command")
        self.assertEqual(dup["count"], 2)

    def test_detect_consecutive_errors(self):
        sample_transcript = [
            {"step_index": 1, "source": "MODEL", "type": "GENERIC", "content": "Command exited with code 1.\nfatal error"},
            {"step_index": 2, "source": "MODEL", "type": "GENERIC", "content": "Command exited with code 1.\nfatal error"}
        ]
        file_path = os.path.join(self.test_dir.name, "transcript.jsonl")
        with open(file_path, "w", encoding="utf-8") as f:
            for line in sample_transcript:
                f.write(json.dumps(line) + "\n")

        analyzer = TranscriptAnalyzer()
        results = analyzer.analyze_transcript(file_path)
        self.assertGreaterEqual(results["consecutive_error_count"], 2)

if __name__ == '__main__':
    unittest.main()

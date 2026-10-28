import unittest
import tempfile
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from auto_patcher import AutoPatcher

class TestAutoPatcher(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory()
        self.patcher = AutoPatcher(workspace_root=self.test_dir.name)

    def tearDown(self):
        self.test_dir.cleanup()

    def test_propose_rule_from_duplicate_tools(self):
        anomaly_report = {
            "duplicate_tool_calls": [
                {
                    "tool_name": "read_file",
                    "count": 3,
                    "sample_args": {"Path": "config.json"}
                }
            ],
            "max_consecutive_errors": 0
        }
        proposals = self.patcher.generate_proposals(anomaly_report)
        self.assertEqual(len(proposals), 1)
        self.assertIn("Duplicate Tool Calls", proposals[0]["title"])
        self.assertEqual(proposals[0]["target_type"], "rule")

    def test_propose_circuit_breaker_from_consecutive_errors(self):
        anomaly_report = {
            "duplicate_tool_calls": [],
            "max_consecutive_errors": 4
        }
        proposals = self.patcher.generate_proposals(anomaly_report)
        self.assertEqual(len(proposals), 1)
        self.assertIn("Consecutive Failures", proposals[0]["title"])

if __name__ == '__main__':
    unittest.main()

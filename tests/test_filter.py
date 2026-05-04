import json
import unittest
import os
import shutil
import tempfile
from lib.filter import filter_actions

class TestFilter(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.config_data = {
            "actions": [
                {"label": "Google Search", "type": "url", "url": "https://google.com?q={query}"},
                {"label": "GitHub Search", "type": "url", "url": "https://github.com?q={query}"},
                {"label": "Script Action", "type": "script", "script": "echo", "args": ["{query}"]}
            ]
        }
        self.config_path = os.path.join(self.test_dir, "actions.json")
        with open(self.config_path, "w") as f:
            json.dump(self.config_data, f)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_filter_empty_query(self):
        labels = filter_actions("", self.config_path)
        self.assertEqual(len(labels), 3)
        self.assertIn("Google Search", labels)

    def test_filter_exact_match(self):
        labels = filter_actions("Google Search", self.config_path)
        self.assertEqual(labels, ["Google Search"])

    def test_filter_partial_match(self):
        labels = filter_actions("Search", self.config_path)
        self.assertEqual(len(labels), 2)
        self.assertIn("Google Search", labels)
        self.assertIn("GitHub Search", labels)

    def test_filter_case_insensitive(self):
        labels = filter_actions("google", self.config_path)
        self.assertEqual(labels, ["Google Search"])

    def test_filter_no_match_returns_all(self):
        labels = filter_actions("NonExistent", self.config_path)
        self.assertEqual(len(labels), 3)

if __name__ == "__main__":
    unittest.main()

import json
import unittest
import os
import shutil
import tempfile
from lib.actions import ActionRepository, ActionFilter

class TestActions(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.config_data = {
            "actions": [
                {"label": "Google Search", "url": "https://google.com?q={query}"},
                {"label": "Script Action", "script": "echo", "args": ["{query}"]},
                {"label": "Gemini", "url": "https://gemini.com", "show_if_contains": ["。", "、", ",", "？"], "copy_to_clipboard": True}
            ]
        }
        self.config_path = os.path.join(self.test_dir, "actions.json")
        with open(self.config_path, "w") as f:
            json.dump(self.config_data, f)
        
        self.repo = ActionRepository(self.config_path)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_filter_empty_query(self):
        actions = self.repo.list_all()
        # show_if_containsの制約は満たさないため、制約なしのみ返る
        result = ActionFilter.filter(actions, "")
        labels = [a.label for a in result]
        self.assertEqual(len(labels), 2)
        self.assertIn("Google Search", labels)
        self.assertNotIn("Gemini", labels)

    def test_filter_no_label_match_restriction(self):
        # ラベル名「Google Search」にマッチしないクエリでも、除外されないことを確認
        actions = self.repo.list_all()
        result = ActionFilter.filter(actions, "Amazon")
        labels = [a.label for a in result]
        self.assertIn("Google Search", labels)

    def test_show_if_contains_match(self):
        actions = self.repo.list_all()
        result = ActionFilter.filter(actions, "今日の天気は？")
        labels = [a.label for a in result]
        self.assertIn("Gemini", labels)
        self.assertIn("Google Search", labels)

    def test_show_if_contains_no_match(self):
        actions = self.repo.list_all()
        result = ActionFilter.filter(actions, "今日の天気")
        labels = [a.label for a in result]
        self.assertNotIn("Gemini", labels)
        
    def test_filter_multiline_query(self):
        actions = self.repo.list_all()
        result = ActionFilter.filter(actions, "line1\nline2")
        labels = [a.label for a in result]
        self.assertEqual(len(labels), 1)
        self.assertEqual(labels[0], "Gemini")

    def test_action_type_resolution(self):
        actions = self.repo.list_all()
        google = next(a for a in actions if a.label == "Google Search")
        script = next(a for a in actions if a.label == "Script Action")
        self.assertEqual(google.type, "url")
        self.assertEqual(script.type, "script")

if __name__ == "__main__":
    unittest.main()

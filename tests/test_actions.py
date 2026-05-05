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
                {"label": "Gemini", "url": "https://gemini.com", "show_if_contains": ["。", "？"], "copy_to_clipboard": True},
                {"label": "Clipboard Only", "script": "cat", "copy_to_clipboard": True}
            ]
        }
        self.config_path = os.path.join(self.test_dir, "actions.json")
        with open(self.config_path, "w") as f:
            json.dump(self.config_data, f)
        
        self.repo = ActionRepository(self.config_path)
        self.filter_engine = ActionFilter()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_default_layer_visibility(self):
        # 何も制約に合致しない場合、制約なしのアクションのみが表示される
        actions = self.repo.list_all()
        result = self.filter_engine.filter("hello", actions)
        labels = [a.label for a in result]
        self.assertEqual(len(labels), 3) # Google, Script, Clipboard Only (Geminiは制約ありなので除外)
        self.assertIn("Google Search", labels)
        self.assertIn("Script Action", labels)
        self.assertIn("Clipboard Only", labels)
        self.assertNotIn("Gemini", labels)

    def test_constraint_layer_exclusivity(self):
        # 制約文字「？」が含まれる場合、制約に合致するアクションのみが独占表示される
        actions = self.repo.list_all()
        result = self.filter_engine.filter("天気は？", actions)
        labels = [a.label for a in result]
        self.assertEqual(len(labels), 1)
        self.assertEqual(labels[0], "Gemini")
        # デフォルトで表示されるはずのアクションも非表示になる
        self.assertNotIn("Google Search", labels)

    def test_newline_layer_highest_priority(self):
        # 改行が含まれる場合、制約マッチよりも優先され、clipboard_onlyのもののみが表示される
        actions = self.repo.list_all()
        # 「？」が含まれているが、改行もある
        result = self.filter_engine.filter("line1\nline2？", actions)
        labels = [a.label for a in result]
        self.assertEqual(len(labels), 2)
        self.assertIn("Gemini", labels)
        self.assertIn("Clipboard Only", labels)
        self.assertNotIn("Google Search", labels)

    def test_action_type_resolution(self):
        actions = self.repo.list_all()
        google = next(a for a in actions if a.label == "Google Search")
        script = next(a for a in actions if a.label == "Script Action")
        self.assertEqual(google.type, "url")
        self.assertEqual(script.type, "script")

if __name__ == "__main__":
    unittest.main()

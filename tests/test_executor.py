import json
import sys
import os
import shutil
import tempfile
import unittest
from unittest.mock import patch
from lib.executor import execute

class TestExecutor(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.config_data = {
            "actions": [
                {"label": "Google", "type": "url", "url": "https://google.com?q={query}"},
                {"label": "Script", "type": "script", "script": "~/test.sh", "args": ["arg1", "{query}"]}
            ]
        }
        self.config_path = os.path.join(self.test_dir, "actions.json")
        with open(self.config_path, "w") as f:
            json.dump(self.config_data, f)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    @patch("subprocess.Popen")
    def test_execute_url(self, mock_popen):
        with patch("sys.argv", ["executor.py", "Google", "hello world", self.config_path]):
            execute()
            expected_url = "https://google.com?q=hello+world"
            mock_popen.assert_called_once()
            args, _ = mock_popen.call_args
            self.assertEqual(args[0], ["xdg-open", expected_url])

    @patch("subprocess.Popen")
    def test_execute_script(self, mock_popen):
        with patch("sys.argv", ["executor.py", "Script", "my query", self.config_path]):
            execute()
            mock_popen.assert_called_once()
            args, _ = mock_popen.call_args
            expected_script = os.path.expanduser("~/test.sh")
            self.assertEqual(args[0], [expected_script, "arg1", "my query"])

    @patch("subprocess.run")
    def test_execute_not_found(self, mock_run):
        with patch("sys.argv", ["executor.py", "Invalid", "query", self.config_path]):
            with self.assertRaises(SystemExit):
                execute()
            mock_run.assert_called()
            args, _ = mock_run.call_args
            self.assertIn("--error", args[0])

if __name__ == "__main__":
    unittest.main()

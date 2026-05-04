import json
import sys
import os
import shutil
import tempfile
import unittest
from unittest.mock import patch, MagicMock
from lib.executor import execute

class TestExecutor(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.config_data = {
            "actions": [
                {"label": "Google", "type": "url", "url": "https://google.com?q={query}"},
                {"label": "Script", "type": "script", "script": "~/test.sh", "args": ["arg1", "{query}"]},
                {"label": "Gemini", "type": "url", "url": "https://gemini.com", "copy_to_clipboard": True}
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

    @patch("subprocess.Popen")
    @patch("subprocess.run")
    def test_copy_to_clipboard_xclip_success(self, mock_run, mock_popen):
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_run.return_value = mock_result
        
        with patch("sys.argv", ["executor.py", "Gemini", "test query", self.config_path]):
            execute()
            
            mock_run.assert_called_once()
            args, kwargs = mock_run.call_args
            self.assertEqual(args[0], ["xclip", "-selection", "clipboard"])
            self.assertEqual(kwargs.get("input"), b"test query")

    @patch("subprocess.Popen")
    @patch("subprocess.run")
    def test_copy_to_clipboard_xclip_fail_xsel_success(self, mock_run, mock_popen):
        mock_fail = MagicMock()
        mock_fail.returncode = 1
        mock_success = MagicMock()
        mock_success.returncode = 0
        
        mock_run.side_effect = [mock_fail, mock_success]
        
        with patch("sys.argv", ["executor.py", "Gemini", "test query", self.config_path]):
            execute()
            
            self.assertEqual(mock_run.call_count, 2)
            args1, kwargs1 = mock_run.call_args_list[0]
            self.assertEqual(args1[0], ["xclip", "-selection", "clipboard"])
            
            args2, kwargs2 = mock_run.call_args_list[1]
            self.assertEqual(args2[0], ["xsel", "--clipboard", "--input"])

    @patch("subprocess.Popen")
    @patch("subprocess.run")
    def test_copy_to_clipboard_xclip_not_found(self, mock_run, mock_popen):
        mock_success = MagicMock()
        mock_success.returncode = 0
        mock_run.side_effect = [FileNotFoundError, mock_success]
        
        with patch("sys.argv", ["executor.py", "Gemini", "test query", self.config_path]):
            execute()
            
            self.assertEqual(mock_run.call_count, 2)
            args1, kwargs1 = mock_run.call_args_list[0]
            self.assertEqual(args1[0], ["xclip", "-selection", "clipboard"])
            
            args2, kwargs2 = mock_run.call_args_list[1]
            self.assertEqual(args2[0], ["xsel", "--clipboard", "--input"])

    @patch("subprocess.Popen")
    @patch("subprocess.run")
    def test_copy_to_clipboard_false_or_missing(self, mock_run, mock_popen):
        with patch("sys.argv", ["executor.py", "Google", "test query", self.config_path]):
            execute()
            mock_run.assert_not_called()

if __name__ == "__main__":
    unittest.main()

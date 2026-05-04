import unittest
from lib.filter import filter_actions

class TestActions(unittest.TestCase):
    def test_filter_empty_query(self):
        """Empty query should return all labels."""
        # Using actions.json as dummy
        labels = filter_actions("", "config/actions.json")
        self.assertIn("Googleで検索", labels)

    def test_filter_match(self):
        """Query 'Google' should match 'Googleで検索'."""
        labels = filter_actions("Google", "config/actions.json")
        self.assertIn("Googleで検索", labels)

if __name__ == '__main__':
    unittest.main()

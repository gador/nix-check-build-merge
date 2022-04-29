import unittest
from unittest import mock
import nix_cbm.checks as checks


class CheckTestCase(unittest.TestCase):
    def test_exists(self):
        self.assertFalse(checks._exists("non_existing_program"))
        self.assertTrue(checks._exists("python"))

    def test_check_tools(self):
        self.assertEqual(checks.check_tools(["python"]), [])
        self.assertEqual(checks.check_tools(["non_existing_program"]), ['non_existing_program'])

    @mock.patch("os.path.exists")
    def test_check_nixpkgs_dir(self, path):
        self.assertTrue(checks.check_nixpkgs_dir("/"))
        assert 3 == path.call_count

    def test_check_nixpkgs_dir(self):
        self.assertRaises(LookupError)

if __name__ == '__main__':
    unittest.main()

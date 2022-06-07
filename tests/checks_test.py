import os
import tempfile
import unittest
from pathlib import Path
from tempfile import mktemp
from unittest import mock

import nix_cbm.checks as checks


class CheckTestCase(unittest.TestCase):
    def test_exists(self):
        self.assertFalse(checks._exists("non_existing_program"))
        self.assertTrue(checks._exists("python"))

    def test_check_tools(self):
        self.assertEqual(checks.check_tools(["python"]), [])
        self.assertEqual(
            checks.check_tools(["non_existing_program"]), ["non_existing_program"]
        )

    def test_check_nixpkgs_dir(self):
        """create a temporary directory and simulate a nixpkgs"""
        with mock.patch(
            "os.path.expanduser"
        ) as mock_base_path, tempfile.TemporaryDirectory() as path:
            mock_base_path.return_value = path
            nixpkgs_dir = os.path.join(path, "nixpkgs")
            os.makedirs(os.path.join(nixpkgs_dir, ".git"))
            Path(os.path.join(nixpkgs_dir, "default.nix")).touch()
            Path(os.path.join(nixpkgs_dir, ".version")).touch()
            self.assertTrue(checks.check_nixpkgs_dir(nixpkgs_dir))
            mock_base_path.assert_called_once()

    def test_check_nixpkgs_dir_not_found(self):
        self.assertFalse(checks.check_nixpkgs_dir("~"))

    def test_check_nixpkgs_raises(self):
        self.assertRaises(NotADirectoryError, checks.check_nixpkgs_dir, "/")


if __name__ == "__main__":
    unittest.main()

import unittest
from unittest import mock

import nix_cbm

class MyTestCase(unittest.TestCase):

    @mock.patch("nix_cbm.checks.check_tools", return_value=[])
    @mock.patch("nix_cbm.checks.check_nixpkgs_dir")
    @mock.patch("nix_cbm.git.git_checkout")
    def test_preflight(self, check_tools, nixpkgs_dir, git_checkout):
        self.assertTrue(nix_cbm._preflight("/"))
        nixpkgs_dir.assert_called_once()
        check_tools.assert_called_once()
        git_checkout.assert_called_once()


if __name__ == '__main__':
    unittest.main()

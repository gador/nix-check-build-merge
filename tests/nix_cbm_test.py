import unittest
from unittest import mock
import pytest

import nix_cbm
from nix_cbm import NixCbm


class MyTestCase(unittest.TestCase):

    @mock.patch("nix_cbm.checks.check_nixpkgs_dir")
    @mock.patch("nix_cbm.git.git_worktree")
    @mock.patch("nix_cbm.git.git_pull")
    @mock.patch("nix_cbm.checks.check_tools", return_value=[])
    @mock.patch("flask_migrate.upgrade")
    @mock.patch("os.path.isfile", return_value=False)
    def test_preflight(self, mock_config, upgrade, check_tools, git_pull, git_worktree, nixpkgs_dir):
        self.assertTrue(nix_cbm._preflight("/"))
        nixpkgs_dir.assert_called_once()
        check_tools.assert_called_once()
        git_worktree.assert_called_once()
        git_pull.assert_called_once()
        mock_config.assert_called_once()
        upgrade.assert_called_once()


    @mock.patch("nix_cbm.checks.check_nixpkgs_dir")
    @mock.patch("nix_cbm.git.git_checkout")
    @mock.patch("nix_cbm.checks.check_tools", return_value=["missing_program"])
    def test_preflight_missing_programs(self, check_tools, nixpkgs_dir, git_checkout):
        self.assertRaises(LookupError, nix_cbm._preflight, "nixpkgs_path")
        check_tools.assert_called_once()
        with pytest.raises(AssertionError):
            nixpkgs_dir.assert_called_with("nixpkgs_path")
        with pytest.raises(AssertionError):
            git_checkout.assert_called_once()

    @mock.patch("subprocess.run", return_value=True)
    def test_find_maintainer(self, mock_subprocess):
        NixCbm().find_maintained_packages(maintainer="test_maintainer")
        mock_subprocess.assert_called_once()

    @mock.patch("nix_cbm.cli")
    def test_main(self, mock_cli):
        nix_cbm.main()
        mock_cli.assert_called_once()

    # TODO add test for click's CLI


if __name__ == '__main__':
    unittest.main()

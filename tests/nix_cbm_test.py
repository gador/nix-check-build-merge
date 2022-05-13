import unittest
from unittest import mock

import pytest

import nix_cbm
from nix_cbm import NixCbm


class MyTestCase(unittest.TestCase):

    # from hydra-check pgadmin --json
    mock_hydra_output = {
        "pgadmin": [
            {
                "icon": "\u2714",
                "success": True,
                "status": "Succeeded",
                "timestamp": "2020-02-19T11:19:06Z",
                "build_id": "113209147",
                "build_url": "https://hydra.nixos.org/build/113209147",
                "name": "pgadmin3-1.22.2",
                "arch": "x86_64-linux",
                "evals": True,
            },
            {
                "icon": "\u2714",
                "success": True,
                "status": "Succeeded",
                "timestamp": "2020-02-18T18:31:04Z",
                "build_id": "113100220",
                "build_url": "https://hydra.nixos.org/build/113100220",
                "name": "pgadmin3-1.22.2",
                "arch": "x86_64-linux",
                "evals": True,
            },
            {
                "icon": "\u2714",
                "success": True,
                "status": "Succeeded",
                "timestamp": "2020-02-15T17:28:08Z",
                "build_id": "112852002",
                "build_url": "https://hydra.nixos.org/build/112852002",
                "name": "pgadmin3-1.22.2",
                "arch": "x86_64-linux",
                "evals": True,
            },
            {
                "icon": "\u2714",
                "success": True,
                "status": "Succeeded",
                "timestamp": "2020-02-08T20:56:44Z",
                "build_id": "111868520",
                "build_url": "https://hydra.nixos.org/build/111868520",
                "name": "pgadmin3-1.22.2",
                "arch": "x86_64-linux",
                "evals": True,
            },
            {
                "icon": "\u2714",
                "success": True,
                "status": "Succeeded",
                "timestamp": "2020-02-03T14:49:58Z",
                "build_id": "111484001",
                "build_url": "https://hydra.nixos.org/build/111484001",
                "name": "pgadmin3-1.22.2",
                "arch": "x86_64-linux",
                "evals": True,
            },
            {
                "icon": "\u2714",
                "success": True,
                "status": "Succeeded",
                "timestamp": "2020-01-28T16:34:13Z",
                "build_id": "111000992",
                "build_url": "https://hydra.nixos.org/build/111000992",
                "name": "pgadmin3-1.22.2",
                "arch": "x86_64-linux",
                "evals": True,
            },
            {
                "icon": "\u2714",
                "success": True,
                "status": "Succeeded",
                "timestamp": "2020-01-15T03:49:43Z",
                "build_id": "110554839",
                "build_url": "https://hydra.nixos.org/build/110554839",
                "name": "pgadmin3-1.22.2",
                "arch": "x86_64-linux",
                "evals": True,
            },
            {
                "icon": "\u2714",
                "success": True,
                "status": "Succeeded",
                "timestamp": "2020-01-12T01:59:46Z",
                "build_id": "110200980",
                "build_url": "https://hydra.nixos.org/build/110200980",
                "name": "pgadmin3-1.22.2",
                "arch": "x86_64-linux",
                "evals": True,
            },
            {
                "icon": "\u2714",
                "success": True,
                "status": "Succeeded",
                "timestamp": "2020-01-10T01:15:51Z",
                "build_id": "110008903",
                "build_url": "https://hydra.nixos.org/build/110008903",
                "name": "pgadmin3-1.22.2",
                "arch": "x86_64-linux",
                "evals": True,
            },
            {
                "icon": "\u2714",
                "success": True,
                "status": "Succeeded",
                "timestamp": "2020-01-06T13:56:50Z",
                "build_id": "109794862",
                "build_url": "https://hydra.nixos.org/build/109794862",
                "name": "pgadmin3-1.22.2",
                "arch": "x86_64-linux",
                "evals": True,
            },
        ]
    }
    json_success = [
        {
            "icon": "✔",
            "success": True,
            "status": "Succeeded",
            "timestamp": "2020-02-19T09:45:37Z",
            "build_id": "113137688",
            "build_url": "https://hydra.nixos.org/build/113137688",
            "name": "pgadmin3-1.22.2",
            "arch": "x86_64-linux",
            "evals": True,
        }
    ]
    json_failure = [
        {
            "icon": "✔",
            "success": False,
            "status": "Succeeded",
            "timestamp": "2020-02-19T09:45:37Z",
            "build_id": "113137688",
            "build_url": "https://hydra.nixos.org/build/113137688",
            "name": "pgadmin3-1.22.2",
            "arch": "x86_64-linux",
            "evals": True,
        }
    ]

    @mock.patch("nix_cbm.checks.check_nixpkgs_dir")
    @mock.patch("nix_cbm.git.git_worktree")
    @mock.patch("nix_cbm.git.git_pull")
    @mock.patch("nix_cbm.checks.check_tools", return_value=[])
    @mock.patch("flask_migrate.upgrade")
    @mock.patch("os.path.isfile", return_value=False)
    def test_preflight(
        self, mock_config, upgrade, check_tools, git_pull, git_worktree, nixpkgs_dir
    ):
        self.assertTrue(nix_cbm._preflight("/"))
        nixpkgs_dir.assert_called_once()
        check_tools.assert_called_once()
        git_worktree.assert_called_once()
        git_pull.assert_called_once()
        mock_config.assert_called_once()
        upgrade.assert_called_once()

    @mock.patch("nix_cbm.checks.check_tools", return_value=["missing_program"])
    def test_preflight_missing_programs(self, check_tools):
        self.assertRaises(LookupError, nix_cbm._preflight, "nixpkgs_path")
        check_tools.assert_called_once()

    def test_get_build_stats(self):
        self.assertTrue(nix_cbm._get_build_status_from_json(self.json_success))
        self.assertFalse(nix_cbm._get_build_status_from_json(self.json_failure))

    # TODO: refactor insert_or_update function
    # @mock.patch("models.Packages.query.filter_by", return_value=["pgadmin"])
    # def test_insert_or_update_package_exists(self):
    #     package = "test_package"
    #     result = True
    #     self.assertTrue(
    #         nix_cbm._insert_or_update(
    #             package=package, result=result, hydra_output=self.mock_hydra_output
    #         )
    #     )

    @mock.patch("subprocess.run", return_value=True)
    def test_find_maintainer(self, mock_subprocess):
        NixCbm().find_maintained_packages(maintainer="test_maintainer")
        mock_subprocess.assert_called_once()

    @mock.patch("nix_cbm.cli")
    def test_main(self, mock_cli):
        nix_cbm.main()
        mock_cli.assert_called_once()

    # TODO add test for click's CLI


if __name__ == "__main__":
    unittest.main()

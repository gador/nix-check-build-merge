import datetime
import os
import tempfile
import unittest
from unittest import mock

import flask_migrate  # type: ignore
from click.testing import CliRunner
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy  # type: ignore
from hypothesis import given
from hypothesis import strategies as st

import nix_cbm


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
    mock_hydra_output_missing_data = {
        "pgadmin": [
            {
                "icon": "\u2714",
                "success": True,
                "status": "Succeeded",
                "name": "pgadmin3-1.22.2",
                "arch": "x86_64-linux",
                "evals": True,
            }
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
    basedir = os.path.abspath(os.path.dirname(__file__))

    def setup_config(self):
        nix_cbm.Config.MAINTAINER = "test_maintainer"
        nix_cbm.Config.NIXPKGS_WORKDIR = "/"
        nix_cbm.Config.NIXPKGS_ORIGINAL = ""

    def setup_db(self):
        """setup_db sets up the database connection

        This will start an in-memory sqlite database and run
        the migration script on it.
        """
        # setup test environment
        nix_cbm.Config.SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
        nix_cbm.Config.SQLALCHEMY_TRACK_MODIFICATIONS = False

        # override frontend db connection with the above test connection
        nix_cbm.frontend.app.config.from_object(nix_cbm.Config)
        with nix_cbm.frontend.app.app_context():
            flask_migrate.upgrade(
                directory=os.path.join(
                    self.basedir, "../", "src", "nix_cbm", "migrations"
                ),
                revision="head",
            )
            nix_cbm.frontend.db.create_all()

    def tear_down(self):
        """tear_down drops all database content"""
        # self.db.init_app(self.app)
        with nix_cbm.frontend.app.app_context():
            nix_cbm.frontend.db.drop_all()

    @mock.patch("nix_cbm.checks.check_nixpkgs_dir")
    @mock.patch("nix_cbm.git.git_worktree")
    @mock.patch("nix_cbm.git.git_pull")
    @mock.patch("nix_cbm.checks.check_tools", return_value=[])
    @mock.patch("flask_migrate.upgrade")
    @mock.patch("os.path.isfile", return_value=False)
    def test_preflight(
        self, mock_config, upgrade, check_tools, git_pull, git_worktree, nixpkgs_dir
    ):
        """test_preflight

        this will test the preflight call and mock all other function
        calls coming from here.

        Parameters
        ----------
        mock_config : _type_
            checks the existence of the sqlite file
        upgrade : _type_
            upgrade script called, if no database has been found
        check_tools : _type_
            call to check_tools (checks for existence of all needed tools)
        git_pull : _type_
            call to git_pull (pull in remote updates)
        git_worktree : _type_
            initiates the git worktree
        nixpkgs_dir : _type_
            checks for the existence of the nixpkgs path provided
        """
        self.setup_config()
        self.setup_db()
        self.assertTrue(nix_cbm._preflight("/"))
        nixpkgs_dir.assert_called_once()
        check_tools.assert_called_once()
        git_worktree.assert_called_once()
        git_pull.assert_called_once()
        mock_config.assert_called_once()
        # called twice. Once in this setup, once inside _preflight function
        assert upgrade.call_count == 2
        self.tear_down()

    @mock.patch("nix_cbm.checks.check_tools", return_value=["missing_program"])
    def test_preflight_missing_programs(self, check_tools):
        """test_preflight_missing_programs test the LookupError for missing programs"""
        self.assertRaises(LookupError, nix_cbm._preflight, "nixpkgs_path")
        check_tools.assert_called_once()

    def test_get_build_stats(self):
        """test_get_build_stats test the result of the build status from json"""
        self.assertTrue(nix_cbm._get_build_status_from_json(self.json_success))
        self.assertFalse(nix_cbm._get_build_status_from_json(self.json_failure))

    @given(st.characters(blacklist_categories="CS"))
    def test_load_maintainer_from_db(self, cs):
        self.setup_config()
        self.setup_db()

        assert nix_cbm.Config.MAINTAINER == "test_maintainer"
        nix_cbm.load_maintainer_from_db()
        # don't override if no maintainer is present in db
        assert nix_cbm.Config.MAINTAINER == "test_maintainer"

        db_entry = nix_cbm.models.PersistentConfig(
            id=0,
            maintainer=cs,
        )
        nix_cbm.frontend.db.session.add(db_entry)
        nix_cbm.frontend.db.session.commit()

        nix_cbm.load_maintainer_from_db()
        assert nix_cbm.Config.MAINTAINER == cs

        nix_cbm.frontend.db.drop_all()
        self.tear_down()

        # reset config
        self.setup_config()

    @given(st.characters(blacklist_categories="CS"))
    def test_save_maintainer_to_db(self, cs):
        self.setup_config()
        self.setup_db()

        assert nix_cbm.Config.MAINTAINER == "test_maintainer"
        nix_cbm.save_maintainer_to_db(cs)
        result = nix_cbm.models.PersistentConfig.query.filter_by(maintainer=cs).first()
        self.assertEqual(result.maintainer, cs)

        self.tear_down()
        self.setup_config()

    @given(st.characters(blacklist_categories="CS"))
    def test_save_nixpkgs_to_db(self, cs):
        self.setup_config()
        self.setup_db()

        assert nix_cbm.Config.NIXPKGS_ORIGINAL == ""
        nix_cbm.save_nixpkgs_to_db(cs)
        result = nix_cbm.models.PersistentConfig.query.filter_by(nixpkgs_path=cs).first()
        self.assertEqual(result.nixpkgs_path, cs)

        self.tear_down()
        self.setup_config()

    @given(st.characters(blacklist_categories="CS"))
    def test_load_nixpkgs_from_db(self, cs):
        self.setup_config()
        self.setup_db()

        assert nix_cbm.Config.NIXPKGS_ORIGINAL == ""
        nix_cbm.load_nixpkgs_from_db()
        nix_cbm.Config.NIXPKGS_ORIGINAL = "testpath"
        # don't override if no path is set
        assert nix_cbm.Config.NIXPKGS_ORIGINAL == "testpath"

        db_entry = nix_cbm.models.PersistentConfig(
            id=0,
            nixpkgs_path=cs,
        )
        nix_cbm.frontend.db.session.add(db_entry)
        nix_cbm.frontend.db.session.commit()

        # loading from db should override existing values
        nix_cbm.load_nixpkgs_from_db()
        assert nix_cbm.Config.NIXPKGS_ORIGINAL == cs

        nix_cbm.frontend.db.drop_all()
        self.tear_down()

        # reset config
        self.setup_config()

    @given(
        st.characters(blacklist_categories="CS"), st.characters(blacklist_categories="CS")
    )
    def test_insert_or_update_package(self, cs, url):
        """
        Test the database model and connection
        """

        # rename pgadmin to a generic character to test with hypothesis
        mock_hydra_output = self.mock_hydra_output.copy()
        mock_hydra_output["pgadmin"][0]["build_url"] = url
        mock_hydra_output[cs] = mock_hydra_output["pgadmin"]

        insert_or_update = nix_cbm.InsertOrUpdate(
            cs, mock_hydra_output, True, "x86_64-linux"
        )

        self.setup_db()
        # custom timestamp format of hydra-check. So we can't easily test with hypothesis
        timestamp = datetime.datetime.fromisoformat("2020-02-19T11:19:06+00:00")
        buildurl = url

        self.assertEqual(insert_or_update.convert_timestamp(), timestamp)
        self.assertEqual(insert_or_update.convert_build_url(), buildurl)
        self.assertFalse(insert_or_update.check_for_package())
        self.assertTrue(insert_or_update.create_db_entry())

        # returns none, but should insert the package in the database
        self.assertIsNone(insert_or_update.insert_or_update())
        # which is checked here
        self.assertTrue(insert_or_update.check_for_package())
        # now update should be performed
        self.assertIsNone(insert_or_update.insert_or_update())

        self.tear_down()

    @given(st.characters(blacklist_categories="CS"))
    def test_insert_or_update_package_missing_data(self, cs):
        """
        Test the database model and connection with missing data
        """

        # rename pgadmin to a generic character to test with hypothesis
        mock_hydra_output = self.mock_hydra_output_missing_data.copy()
        mock_hydra_output[cs] = mock_hydra_output["pgadmin"]

        insert_or_update = nix_cbm.InsertOrUpdate(
            cs, mock_hydra_output, True, "x86_64-linux"
        )

        self.setup_db()

        self.assertIsNone(insert_or_update.convert_timestamp())
        self.assertIsNone(insert_or_update.convert_build_url())
        self.assertFalse(insert_or_update.check_for_package())
        self.assertTrue(insert_or_update.create_db_entry())

        # returns none, but should insert the package in the database
        self.assertIsNone(insert_or_update.insert_or_update())
        # which is checked here
        self.assertTrue(insert_or_update.check_for_package())

        self.tear_down()

    @mock.patch("nix_cbm.InsertOrUpdate")
    @mock.patch("nix_cbm._get_build_status_from_json", return_value=True)
    @mock.patch("nix_cbm.NixCbm")
    def test_refresh_build_status(self, mock_nixcbm, get_build_status, insertOrUpdate):
        """test_refresh_build_status checks the refresh_build_status function

        Here we needed to overwrite the return values of the class variables.
        It also checks the calls to _get_build_status_from_json and the call
        to the database routine "InsertOrUpdate"


        Parameters
        ----------
        mock_nixcbm : _type_
            the class, which contains all the state information
        get_build_status : _type_
            function to determine build success
        insertOrUpdate : _type_
            database connection class
        """

        mock_nixcbm.return_value.maintained_packages = ["pgadmin"]
        mock_nixcbm.return_value.hydra_build_status = {"pgadmin": self.mock_hydra_output}

        self.assertIsNone(nix_cbm.refresh_build_status(reload_maintainer=False))

        mock_nixcbm.assert_called_once()
        get_build_status.assert_called_once()
        insertOrUpdate.assert_called_once()

        self.assertIsNone(nix_cbm.refresh_build_status(reload_maintainer=True))

    # Unicode surrogate don't work with db
    @given(st.characters(blacklist_categories="CS"))
    def test_load_maintained_package_list_from_database(self, package_name):
        self.setup_db()
        self.setup_config()
        nixcbm = nix_cbm.NixCbm()
        nixcbm.load_maintained_packages_from_database()
        assert nixcbm.maintained_packages == []

        insert_or_update = nix_cbm.InsertOrUpdate(
            package_name, self.mock_hydra_output_missing_data, True, "x86_64-linux"
        )
        self.assertIsNone(insert_or_update.insert_or_update())
        nixcbm.load_maintained_packages_from_database()
        assert nixcbm.maintained_packages == [package_name]

        nixcbm.load_maintained_packages_from_database()
        assert nixcbm.maintained_packages == [package_name]

        self.tear_down()

    @given(st.characters())
    def test_find_maintainer(self, cs):
        with mock.patch("subprocess.run", return_value=True) as mock_subprocess:
            nix_cbm.NixCbm().update_maintained_packages_list(maintainer=cs)
            mock_subprocess.assert_called_once()

    @given(st.characters(blacklist_categories="CS"))
    def test_save_maintained_packages_to_db(self, cs):
        """
        Checks that the maintained list of packages is empty,
        then fills it and rechecks that it has been committed
        to the database.
        """

        self.setup_db()
        self.setup_config()

        # rename pgadmin to a generic character to test with hypothesis
        mock_hydra_output = self.mock_hydra_output_missing_data.copy()
        mock_hydra_output[cs] = mock_hydra_output["pgadmin"]

        nixcbm = nix_cbm.NixCbm()
        insert_or_update = nix_cbm.InsertOrUpdate(
            cs,
            self.mock_hydra_output_missing_data,
            True,
            "x86_64-linux",
        )
        assert nixcbm.maintained_packages == []
        nixcbm.save_maintained_packages_to_db()
        self.assertFalse(insert_or_update.check_for_package())

        nixcbm.maintained_packages = [cs]
        nixcbm.save_maintained_packages_to_db()
        self.assertTrue(insert_or_update.check_for_package())

        # re-checking, since the package is now already present
        nixcbm.save_maintained_packages_to_db()
        self.assertTrue(insert_or_update.check_for_package())

        self.tear_down()

    @given(st.characters(blacklist_categories="CS"))
    def test_cli(self, maintainer):
        """test_cli tests the functionality of the CLI

        Here we test the all the combinations of wrong and right
        arguments and their result codes.
        """
        # reset Config values, so we can test the CLI
        old_nixpkgs = nix_cbm.Config.NIXPKGS_ORIGINAL
        nix_cbm.Config.NIXPKGS_ORIGINAL = ""
        old_maintainer = nix_cbm.Config.MAINTAINER
        nix_cbm.Config.MAINTAINER = ""
        with mock.patch("nix_cbm.frontend.app.run") as frontend, mock.patch(
            "nix_cbm.refresh_build_status"
        ) as build_status, mock.patch("nix_cbm._preflight") as preflight:
            with tempfile.TemporaryDirectory() as tmp:
                runner = CliRunner()

                result = runner.invoke(nix_cbm.cli, ["--nixpkgs", tmp, "update"])
                assert result.exit_code == 1
                assert result.output == ""

                result = runner.invoke(
                    nix_cbm.cli,
                    ["--nixpkgs", tmp, "--maintainer", maintainer, "update"],
                )
                assert result.exit_code == 0
                assert result.output == ""
                preflight.assert_called_once()
                build_status.assert_called_once()
                preflight.reset_mock()
                build_status.reset_mock()

                result = runner.invoke(
                    nix_cbm.cli,
                    ["--nixpkgs", tmp, "--maintainer", maintainer, "frontend"],
                )
                assert result.exit_code == 0
                assert result.output == ""
                preflight.assert_called_once()
                build_status.assert_not_called()
                frontend.assert_called_once()

                result = runner.invoke(
                    nix_cbm.cli, ["--nixpkgs", tmp, "--maintainer", maintainer]
                )
                assert result.exit_code == 2
                assert "Error: Missing argument 'ACTION'." in result.output

            runner = CliRunner()

            nix_cbm.Config.NIXPKGS_ORIGINAL = ""
            result = runner.invoke(nix_cbm.cli, ["--maintainer", maintainer, "update"])
            assert result.exit_code == 1
            assert result.output == ""

            # reset back to not influence other tests
            nix_cbm.Config.NIXPKGS_ORIGINAL = old_nixpkgs
            nix_cbm.Config.MAINTAINER = old_maintainer

    @given(st.characters())
    def test_check_hydra_status(self, cs):
        """test_check_hydra_status

        checks the call to the hydra script
        """
        with mock.patch("json.loads") as mock_json, mock.patch(
            "subprocess.run"
        ) as mock_subprocess:
            mock_subprocess.return_value.stdout = True
            nix_cbm.NixCbm().check_hydra_status(packages=[cs], arch="x86_64-linux")
            cmd = [
                "hydra-check",
                cs,
                "--channel",
                "master",
                "--arch=" + "x86_64-linux",
                "--json",
            ]
            mock_subprocess.assert_called_with(cmd, capture_output=True, check=True)
            mock_json.assert_called_once()

    @mock.patch("nix_cbm.cli")
    def test_main(self, mock_cli):
        nix_cbm.main()
        mock_cli.assert_called_once()


if __name__ == "__main__":
    unittest.main()

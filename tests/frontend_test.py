import os
import unittest
from unittest import mock

import flask_migrate  # type: ignore
from hypothesis import given
from hypothesis import strategies as st

import nix_cbm


class FrontendTestCase(unittest.TestCase):
    basedir = os.path.abspath(os.path.dirname(__file__))

    def setUp(self) -> None:
        nix_cbm.Config.MAINTAINER = "test_maintainer"
        nix_cbm.Config.NIXPKGS_ORIGINAL = "/nixpkgs"
        nix_cbm.Config.NIXPKGS_WORKDIR = "/"
        nix_cbm.Config.TESTING = True
        self.setup_db()
        return super().setUp()

    def tearDown(self) -> None:
        nix_cbm.Config.MAINTAINER = ""
        nix_cbm.Config.NIXPKGS_ORIGINAL = ""
        nix_cbm.Config.NIXPKGS_WORKDIR = ""
        nix_cbm.Config.TESTING = False
        self.close_db()
        return super().tearDown()

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

    def close_db(self):
        """tear_down drops all database content"""
        # self.db.init_app(self.app)
        with nix_cbm.frontend.app.app_context():
            nix_cbm.frontend.db.drop_all()

    def test_init_app(self):
        assert nix_cbm.Config.PREFLIGHT_DONE == False
        self.assertIsNone(nix_cbm.frontend.init_app())
        # should stay false, since we return early, due to TESTING == True
        assert nix_cbm.Config.PREFLIGHT_DONE == False

    def test_config_is_set(self):
        self.assertTrue(nix_cbm.frontend.config_is_set())
        nix_cbm.Config.MAINTAINER = ""
        self.assertFalse(nix_cbm.frontend.config_is_set())

        # test loading from database
        nix_cbm.save_maintainer_to_db("test_maintainer")
        nix_cbm.save_nixpkgs_to_db("/nixpkgs")
        self.assertTrue(nix_cbm.frontend.config_is_set())
        self.assertEqual(nix_cbm.Config.MAINTAINER, "test_maintainer")
        self.assertEqual(nix_cbm.Config.NIXPKGS_ORIGINAL, "/nixpkgs")

    def test_get_packages(self):
        with mock.patch("flask_sqlalchemy._QueryProperty.__get__") as queryMOCK:
            # queryMOCK.return_value.filter_by.return_value.all.return_value = [1,22]
            nix_cbm.frontend.get_packages()
            queryMOCK.assert_called_once()
            nix_cbm.frontend.get_packages(True)
            queryMOCK.assert_called()

    @given(
        st.characters(blacklist_characters=["/", "."]),
        # matches only any word character
        st.from_regex(r"\w*", fullmatch=True),
        # matches at least one any non-word character
        st.from_regex(r"\w*\W+\w*", fullmatch=True),
    )
    def test_input_sanitizer(self, cs, regex, illegal_regex):
        self.assertRaises(ValueError, nix_cbm.frontend.input_sanitizer, cs, "wrong_which")
        self.assertEqual(nix_cbm.frontend.input_sanitizer(cs, "path"), None)
        self.assertEqual(nix_cbm.frontend.input_sanitizer(regex, "maintainer"), regex)
        self.assertIsNone(nix_cbm.frontend.input_sanitizer(illegal_regex, "maintainer"))

    def test_main_page_without_settings(self):
        # Create a test client using the Flask application configured for testing
        nix_cbm.Config.MAINTAINER = ""
        nix_cbm.Config.NIXPKGS_ORIGINAL = ""
        with nix_cbm.frontend.app.test_client() as test_client:
            response = test_client.get("/")
            assert response.status_code == 302

    def test_main_page(self):
        with nix_cbm.frontend.app.test_client() as test_client:
            response = test_client.get("/")
            assert response.status_code == 200
            assert b"Nix Check Build Merge" in response.data
            assert b"Packages maintained by test_maintainer" in response.data
            assert b"Nix Check Build Merge on GitHub" in response.data

    @mock.patch("nix_cbm.refresh_build_status")
    def test_main_page_button1(self, refresh_build):
        with nix_cbm.frontend.app.test_client() as test_client:
            response = test_client.post(
                "/",
                data={
                    "button1": "Update hydra-build",
                },
            )
            assert response.status_code == 200
            refresh_build.assert_called_with(arch="x86_64-linux")
            assert b"Nix Check Build Merge" in response.data
            assert b"Packages maintained by test_maintainer" in response.data
            assert b"Nix Check Build Merge on GitHub" in response.data

    @mock.patch("nix_cbm.refresh_build_status")
    def test_main_page_button2(self, refresh_build):
        with nix_cbm.frontend.app.test_client() as test_client:
            response = test_client.post(
                "/",
                data={
                    "button2": "Update maintained packages",
                },
            )
            assert response.status_code == 200
            refresh_build.assert_called_with(reload_maintainer=True, arch="x86_64-linux")
            assert b"Nix Check Build Merge" in response.data
            assert b"Packages maintained by test_maintainer" in response.data
            assert b"Nix Check Build Merge on GitHub" in response.data

    def test_failed_page(self):
        # Create a test client using the Flask application configured for testing
        with nix_cbm.frontend.app.test_client() as test_client:
            response = test_client.get("/failed")
            assert response.status_code == 200
            assert b"Nix Check Build Merge" in response.data
            assert b"Built failures from packages maintained by" in response.data
            assert b"Nix Check Build Merge on GitHub" in response.data
        with nix_cbm.frontend.app.test_client() as test_client:
            response = test_client.put("/failed")
            assert response.status_code == 405
            assert b"Not Allowed" in response.data

    @mock.patch("nix_cbm.refresh_build_status")
    def test_failed_page_button1(self, refresh_build):
        with nix_cbm.frontend.app.test_client() as test_client:
            response = test_client.post(
                "/failed",
                data={
                    "button1": "Update hydra-build",
                },
            )
            assert response.status_code == 200
            refresh_build.assert_called_with(arch="x86_64-linux")
            assert b"Nix Check Build Merge" in response.data
            assert b"Built failures from packages maintained by" in response.data
            assert b"Nix Check Build Merge on GitHub" in response.data

    @mock.patch("nix_cbm.refresh_build_status")
    def test_failed_page_button2(self, refresh_build):
        with nix_cbm.frontend.app.test_client() as test_client:
            response = test_client.post(
                "/failed",
                data={
                    "button2": "Update maintained packages",
                },
            )
            assert response.status_code == 200
            refresh_build.assert_called_with(reload_maintainer=True, arch="x86_64-linux")
            assert b"Nix Check Build Merge" in response.data
            assert b"Built failures from packages maintained by" in response.data
            assert b"Nix Check Build Merge on GitHub" in response.data

    def test_settings_page(self):
        # Create a test client using the Flask application configured for testing
        with nix_cbm.frontend.app.test_client() as test_client:
            response = test_client.get("/settings")
            assert response.status_code == 200
            assert b"Settings for Nix Check Build Merge" in response.data
            assert b"Nixpkgs path:" in response.data
            assert b"Nix Check Build Merge on GitHub" in response.data
        with nix_cbm.frontend.app.test_client() as test_client:
            response = test_client.post(
                "/settings",
                data={
                    "maintainer_textbox": "new_maintainer",
                    "path_textbox": "/",
                    "button": "Save settings",
                },
            )
            assert response.status_code == 302
            self.assertEqual(nix_cbm.Config.MAINTAINER, "new_maintainer")
            self.assertEqual(nix_cbm.Config.NIXPKGS_ORIGINAL, "/")

    def test_settings_page_partial_info(self):
        with nix_cbm.frontend.app.test_client() as test_client:
            response = test_client.post(
                "/settings",
                data={
                    "maintainer_textbox": "new_maintainer",
                    "path_textbox": "",
                    "button": "Save settings",
                },
            )
            assert response.status_code == 200
            self.assertEqual(nix_cbm.Config.MAINTAINER, "new_maintainer")
            self.assertEqual(nix_cbm.Config.NIXPKGS_ORIGINAL, "/nixpkgs")
            assert b"Settings for Nix Check Build Merge" in response.data


if __name__ == "__main__":
    unittest.main()

import os
import unittest
from unittest import mock

import flask_migrate  # type: ignore
from hypothesis import given
from hypothesis import strategies as st

import nix_cbm


class FrontendTestCase(unittest.TestCase):
    basedir = os.path.abspath(os.path.dirname(__file__))

    def setup_config(self):
        nix_cbm.Config.MAINTAINER = "test_maintainer"
        nix_cbm.Config.NIXPKGS_WORKDIR = "/"
        nix_cbm.Config.TESTING = True

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
        nix_cbm.Config.TESTING = False

    def test_main_age(self):
        # Create a test client using the Flask application configured for testing
        self.setup_config()
        self.setup_db()
        with nix_cbm.frontend.app.test_client() as test_client:
            response = test_client.get("/")
            assert response.status_code == 200
            assert b"Nix Check Build Merge" in response.data
            assert b"Packages maintained by test_maintainer" in response.data
            assert b"Nix Check Build Merge on GitHub" in response.data
        self.tear_down()

    def test_failed_page(self):
        # Create a test client using the Flask application configured for testing
        self.setup_config()
        self.setup_db()
        with nix_cbm.frontend.app.test_client() as test_client:
            response = test_client.get("/failed")
            assert response.status_code == 200
            assert b"Nix Check Build Merge" in response.data
            assert b"Built failures from packages maintained by" in response.data
            assert b"Nix Check Build Merge on GitHub" in response.data
        self.tear_down()


if __name__ == "__main__":
    unittest.main()

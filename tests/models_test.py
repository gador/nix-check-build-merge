import datetime
import subprocess
import unittest
from unittest import mock

from nix_cbm import models


class ModelTestCase(unittest.TestCase):
    def test_repr(self):
        db_entry = models.Packages(
            name="test_package",
            hydra_status={"dict": "test"},
            build_url="test_url",
            timestamp=datetime.datetime.fromisoformat("2020-02-19T11:19:06+00:00"),
            last_checked=datetime.datetime.fromisoformat("2022-02-19T09:45:37+00:00"),
        )
        assert db_entry.name == "test_package"
        assert db_entry.hydra_status == {"dict": "test"}
        assert db_entry.build_url == "test_url"
        assert db_entry.timestamp == datetime.datetime.fromisoformat(
            "2020-02-19T11:19:06+00:00"
        )
        assert db_entry.last_checked == datetime.datetime.fromisoformat(
            "2022-02-19T09:45:37+00:00"
        )

        assert repr(db_entry) == "<Package test_package>"


if __name__ == "__main__":
    unittest.main()

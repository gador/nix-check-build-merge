import datetime
import subprocess
import unittest
from unittest import mock

from hypothesis import given
from hypothesis import strategies as st

from nix_cbm import models


class ModelTestCase(unittest.TestCase):
    @given(
        st.characters(),
        st.characters(),
        st.dictionaries(st.characters(), st.characters()),
        st.datetimes(),
    )
    def test_repr(self, cs, url, di, dates):
        db_entry = models.Packages(
            name=cs,
            hydra_status=di,
            build_url=url,
            timestamp=dates,
            last_checked=dates,
        )
        assert db_entry.name == cs
        assert db_entry.hydra_status == di
        assert db_entry.build_url == url
        assert db_entry.timestamp == dates
        assert db_entry.last_checked == dates

        assert repr(db_entry) == f"<Package {cs}>"


if __name__ == "__main__":
    unittest.main()

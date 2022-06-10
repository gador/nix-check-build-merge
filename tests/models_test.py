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
        st.characters(),
    )
    def test_package_repr(self, cs, url, di, dates, arch):
        db_entry = models.Packages(
            name=cs,
            hydra_status=di,
            build_url=url,
            arch=arch,
            timestamp=dates,
            last_checked=dates,
        )
        assert db_entry.name == cs
        assert db_entry.hydra_status == di
        assert db_entry.build_url == url
        assert db_entry.arch == arch
        assert db_entry.timestamp == dates
        assert db_entry.last_checked == dates

        assert repr(db_entry) == f"<Package {cs}>"

    @given(st.characters(), st.characters(), st.characters())
    def test_config_repr(self, cs, path, arch):
        db_entry = models.PersistentConfig(
            maintainer=cs, nixpkgs_path=path, archs_to_check=arch
        )
        assert db_entry.maintainer == cs
        assert db_entry.nixpkgs_path == path
        assert db_entry.archs_to_check == arch
        assert repr(db_entry) == f"<Maintainer {cs}, Path {path}, Archs {arch}>"


if __name__ == "__main__":
    unittest.main()

import os
from pathlib import Path

basedir = os.path.join(Path.home(), ".config", "nix-check-build-merge")


class Config(object):
    if not os.path.exists(basedir):
        os.makedirs(basedir, exist_ok=True)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL"
    ) or "sqlite:///" + os.path.join(basedir, "nixcbm.db")

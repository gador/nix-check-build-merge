import os
from pathlib import Path

basedir = os.path.join(Path.home(), ".config", "nix-check-build-merge")
nixpkgs_workdir = os.path.join(basedir, "nixpkgs")


class Config(object):
    if not os.path.exists(basedir):
        os.makedirs(basedir, exist_ok=True)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL"
    ) or "sqlite:///" + os.path.join(basedir, "nixcbm.db")
    NIXPKGS_WORKDIR = os.environ.get("NIXPKGS_WORKDIR") or nixpkgs_workdir
    MAINTAINER = os.environ.get("MAINTAINER") or ""
    NIXPKGS_ORIGINAL = os.environ.get("NIXPKGS") or ""

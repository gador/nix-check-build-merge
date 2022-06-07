import os
import re
from typing import Tuple, Union

from flask import Flask, jsonify, redirect, render_template, request, wrappers
from flask_migrate import Migrate  # type: ignore
from flask_sqlalchemy import SQLAlchemy  # type: ignore
from werkzeug import Response

import nix_cbm
from nix_cbm.config import Config

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)


def init_app() -> None:
    """makes sure preflight ran"""
    if not Config.PREFLIGHT_DONE:
        nix_cbm.preflight(Config.NIXPKGS_ORIGINAL)


def config_is_set() -> bool:
    """Check, whether maintainer and nixpkgs path are set"""
    if Config.MAINTAINER and Config.NIXPKGS_ORIGINAL:
        return True
    # not set, so try loading from database
    nix_cbm.check_for_database()
    nix_cbm.restore_or_save_config()
    # now, try again
    if Config.MAINTAINER and Config.NIXPKGS_ORIGINAL:
        return True
    return False


def get_packages(failed: bool = False) -> Tuple:
    """Get packages from db"""
    init_app()
    if failed:
        return nix_cbm.models.Packages.query.filter(
            nix_cbm.models.Packages.hydra_status == False  # noqa: E712
        )
    else:
        return nix_cbm.models.Packages.query


def input_sanitizer(input: str, which: str) -> Union[str, None]:
    """Sanitizes maintainer and path strings"""
    if which == "maintainer":
        # matches any word characters
        match = re.fullmatch(r"^\w*$", input)
        if input == "":
            # special case of empty string. Return it instead of None
            return ""
        if match and match.group(0) != "":
            return match.group(0)
        else:
            return None
        # return match.group(0) if match else None
    elif which == "path":
        return input if os.path.exists(os.path.normpath(input)) else None
    else:
        raise ValueError(f"wrong argument called {which}")


# TODO: add functionality
@app.route("/tasks", methods=["POST"])
def run_task() -> Tuple[wrappers.Response, int]:
    task_type = request.form["type"]
    return jsonify(task_type), 202


@app.route("/settings", methods=["GET", "POST"])
def settings() -> Union[str, Response]:
    """Change settings and save to the database"""
    if request.method == "POST":
        if request.form.get("button") == "Save settings":
            maintainer = input_sanitizer(
                str(request.form.get("maintainer_textbox")), "maintainer"
            )
            path = input_sanitizer(str(request.form.get("path_textbox")), "path")
            if maintainer:
                Config.MAINTAINER = maintainer
                nix_cbm.save_maintainer_to_db(maintainer)
            if path:
                Config.NIXPKGS_ORIGINAL = path
                nix_cbm.save_nixpkgs_to_db(path)
            if maintainer and path:
                return redirect("/", 302)
            return render_template(
                "settings.html",
                maintainer=Config.MAINTAINER,
                path=Config.NIXPKGS_ORIGINAL,
            )
    return render_template(
        "settings.html", maintainer=Config.MAINTAINER, path=Config.NIXPKGS_ORIGINAL
    )


@app.route("/failed", methods=["GET", "POST"])
def failed() -> Union[str, Response]:
    # check for set maintainer and nixpkgs path first
    if not config_is_set():
        return redirect("/settings", code=302)
    packages = get_packages(failed=True)
    if request.method == "POST":
        # TODO: delegate to worker
        if request.form.get("button1") == "Update hydra-build":
            for arch in Config.ARCH_TO_CHECK:
                nix_cbm.refresh_build_status(arch=arch)
            packages = get_packages(failed=True)
            return render_template(
                "failed.html",
                maintainer=Config.MAINTAINER,
                packages=packages,
            )
        if request.form.get("button2") == "Update maintained packages":
            for arch in Config.ARCH_TO_CHECK:
                nix_cbm.refresh_build_status(reload_maintainer=True, arch=arch)
            packages = get_packages(failed=True)
            return render_template(
                "failed.html",
                maintainer=Config.MAINTAINER,
                packages=packages,
            )
    return render_template("failed.html", maintainer=Config.MAINTAINER, packages=packages)


@app.route("/", methods=["GET", "POST"])
def index() -> Union[str, Response]:
    # TODO: this needs to be offloaded to a different worker
    # check for set maintainer and nixpkgs path first
    if not config_is_set():
        return redirect("/settings", code=302)
    packages = get_packages()
    if request.method == "POST":
        # TODO: delegate to worker
        if request.form.get("button1") == "Update hydra-build":
            for arch in Config.ARCH_TO_CHECK:
                nix_cbm.refresh_build_status(arch=arch)
            packages = get_packages()
            return render_template(
                "index.html",
                maintainer=Config.MAINTAINER,
                packages=packages,
            )
        if request.form.get("button2") == "Update maintained packages":
            for arch in Config.ARCH_TO_CHECK:
                nix_cbm.refresh_build_status(reload_maintainer=True, arch=arch)
            packages = get_packages()
            return render_template(
                "index.html",
                maintainer=Config.MAINTAINER,
                packages=packages,
            )
    return render_template("index.html", maintainer=Config.MAINTAINER, packages=packages)

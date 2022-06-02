from typing import Tuple

from flask import Flask, jsonify, render_template, request, wrappers
from flask_migrate import Migrate  # type: ignore
from flask_sqlalchemy import SQLAlchemy  # type: ignore

import nix_cbm
from nix_cbm.config import Config

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# TODO: Write frontend tests


def get_packages(failed: bool = False) -> Tuple:
    """Get packages from db"""
    if failed:
        return nix_cbm.models.Packages.query.filter(
            nix_cbm.models.Packages.hydra_status == False  # noqa: E712
        )
    else:
        return nix_cbm.models.Packages.query


@app.route("/tasks", methods=["POST"])
def run_task() -> Tuple[wrappers.Response, int]:
    task_type = request.form["type"]
    return jsonify(task_type), 202


@app.route("/failed", methods=["GET", "POST"])
def failed() -> str:
    packages = get_packages(failed=True)
    if request.method == "POST":
        # TODO: delegate to worker
        if request.form.get("button1") == "Update hydra-build":
            nix_cbm.refresh_build_status()
            packages = get_packages(failed=True)
            return render_template(
                "failed.html",
                maintainer=Config.MAINTAINER,
                packages=packages,
            )
        if request.form.get("button2") == "Update maintained packages":
            nix_cbm.refresh_build_status(reload_maintainer=True)
            packages = get_packages(failed=True)
            return render_template(
                "failed.html",
                maintainer=Config.MAINTAINER,
                packages=packages,
            )
    elif request.method == "GET":
        return render_template(
            "failed.html", maintainer=Config.MAINTAINER, packages=packages
        )
    return render_template("index.html", maintainer=Config.MAINTAINER, packages=packages)


@app.route("/", methods=["GET", "POST"])
def index() -> str:
    # this needs to be offloaded to a different worker
    # also, for now maintainer is hardcoded
    # TODO: add form to enter maintainer
    # TODO: make DataTable static
    packages = get_packages()
    if request.method == "POST":
        # TODO: delegate to worker
        if request.form.get("button1") == "Update hydra-build":
            nix_cbm.refresh_build_status()
            packages = get_packages()
            return render_template(
                "index.html",
                maintainer=Config.MAINTAINER,
                packages=packages,
            )
        if request.form.get("button2") == "Update maintained packages":
            nix_cbm.refresh_build_status(reload_maintainer=True)
            packages = get_packages()
            return render_template(
                "index.html",
                maintainer=Config.MAINTAINER,
                packages=packages,
            )
    elif request.method == "GET":
        return render_template(
            "index.html", maintainer=Config.MAINTAINER, packages=packages
        )
    return render_template("index.html", maintainer=Config.MAINTAINER, packages=packages)

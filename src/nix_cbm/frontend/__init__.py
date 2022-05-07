import logging
import os

from flask import Flask, render_template, request
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

import nix_cbm
from nix_cbm.config import Config

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)


@app.route("/", methods=["GET", "POST"])
def index():
    # this needs to be offloaded to a different worker
    # also, for now maintainer is hardcoded
    # TODO: add form to enter maintainer
    # TODO: make DataTable static
    nixcbm = nix_cbm.NixCbm()
    packages = nix_cbm.models.Packages.query
    if request.method == "POST":
        # TODO: delegate to worker
        if request.form.get("check") == "Check for Maintainer":
            logging.debug("Checking")
            if request.form.get("nixpkgs_path"):
                logging.debug(f"nixpkgs path: {request.form.get('nixpkgs_path')}")
                if os.path.isdir(request.form.get("nixpkgs_path")):
                    logging.debug("Nixpkgs is a dir")
                    nixcbm.nixpkgs_repo = request.form.get("nixpkgs_path")
            if request.form.get("maintainer"):
                nixcbm.maintainer = request.form.get("maintainer")
                logging.debug(f"Maintainer is {nixcbm.maintainer}")
        if nixcbm.maintainer and nixcbm.nixpkgs_repo:
            logging.debug("Both fields answered")
            nixcbm.find_maintained_packages(nixcbm.maintainer)
            nix_cbm.refresh_build_status(
                nixpkgs=nixcbm.nixpkgs_repo, maintainer=nixcbm.maintainer
            )
            packages = nix_cbm.models.Packages.query
            return render_template(
                "index.html",
                maintainer=nixcbm.maintainer,
                packages=packages,
                nixpkgs_path=nixcbm.nixpkgs_repo,
            )
    elif request.method == "GET":
        return render_template("index.html", maintainer="gador", packages=packages)
    return render_template("index.html", maintainer="gador", packages=packages)

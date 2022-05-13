import datetime
import json
import logging
import os
import subprocess
import tempfile

import click
import flask_migrate  # type: ignore

from nix_cbm import checks, frontend, git, models
from nix_cbm.config import Config

basedir = os.path.abspath(os.path.dirname(__file__))

logging.basicConfig(level=logging.DEBUG)


def _preflight(nixpkgs_path: str) -> bool:
    """
    Check if all running conditions are met.
    This is the only function to interact with the
    local nixpkgs repo. From now on, we'll work
    with the workdir.
    OUTPUT: ok, bool.
    """
    logging.debug("running preflight checklist")
    missing_programs = checks.check_tools()
    if missing_programs:
        raise LookupError(
            f"The following programs are missing: + ${str(missing_programs)}"
        )
    checks.check_nixpkgs_dir(nixpkgs_path)
    git.git_worktree(repo=nixpkgs_path, nixpkgs_dir=Config.NIXPKGS_WORKDIR)
    git.git_pull(repo=Config.NIXPKGS_WORKDIR)
    # check for database
    if not os.path.isfile(Config.SQLALCHEMY_DATABASE_URI.replace("sqlite:///", "")):
        logging.info(f"Creating db at {Config.SQLALCHEMY_DATABASE_URI}")
        with frontend.app.app_context():
            flask_migrate.upgrade(
                directory=os.path.join(basedir, "migrations"), revision="head"
            )
    # git.git_checkout(repo=Config.NIXPKGS_WORKDIR)
    return True


def _get_build_status_from_json(package_json: list[dict]) -> bool:
    # the 0 implies the most recent build
    return package_json[0]["success"]


def _insert_or_update(package: str, result: bool, hydra_output: dict) -> None:
    try:
        timestamp_str = str(hydra_output[package][0]["timestamp"])
        timestamp_str = timestamp_str.replace("Z", "+00:00")
        timestamp = datetime.datetime.fromisoformat(timestamp_str)
    except KeyError:
        timestamp = None

    try:
        build_url = hydra_output[package][0]["build_url"]
    except KeyError:
        build_url = None

    current_package = models.Packages.query.filter_by(name=package).first()
    if not current_package:
        # package doesn't exist yet
        db_entry = models.Packages(
            name=package,
            hydra_status=result,
            build_url=build_url,
            timestamp=timestamp,
            last_checked=datetime.datetime.now(),
        )
        frontend.db.session.add(db_entry)
    else:
        current_package.hydra_status = result
        current_package.build_url = build_url
        current_package.timestamp = timestamp
        current_package.last_checked = datetime.datetime.now()
    frontend.db.session.commit()


def refresh_build_status() -> None:
    nixcbm = NixCbm()
    nixcbm.nixpkgs_repo = Config.NIXPKGS_WORKDIR
    nixcbm.find_maintained_packages(Config.MAINTAINER)
    nixcbm.check_hydra_status(nixcbm.maintained_packages)

    # just a stub/demonstration of the current packages
    # TODO: Add a frontend to display them nicely
    for package, hydra_output in nixcbm.hydra_build_status.items():
        result = _get_build_status_from_json(hydra_output[package])
        _insert_or_update(package=package, result=result, hydra_output=hydra_output)
        if result:
            print(f"{package} built successfully on hydra")
        elif hydra_output[package][0]["evals"]:
            print(
                f"Package {package} failed. See log at {hydra_output[package][0]['build_url']}"
            )
        elif hydra_output[package][0]["status"] == "Cancelled":
            print(f"Package {package} was cancelled")
        else:
            print(f"Package {package} failed due to an eval failure")


def main() -> None:
    # TODO add CLI and API interface
    cli()


@click.command()
@click.option("--nixpkgs", help="path to nixpkgs")
@click.option("--maintainer", help="maintainer to look for")
@click.argument("action")
def cli(nixpkgs: str, maintainer: str, action: str) -> None:
    """
    CLI interface for nix-check-build-merge.\n
    Use "update" for checking the build status for all packages belonging to "maintainer"\n
    Use "frontend" to test the frontend
    """
    if not Config.NIXPKGS_ORIGINAL and not nixpkgs:
        raise LookupError("Please provide a path to nixpkgs")
    if not Config.NIXPKGS_ORIGINAL:
        Config.NIXPKGS_ORIGINAL = nixpkgs
    if not Config.MAINTAINER and not maintainer:
        raise LookupError("Please provide a maintainer")
    if not Config.MAINTAINER:
        Config.MAINTAINER = maintainer
    _preflight(Config.NIXPKGS_ORIGINAL)
    if action == "update":
        refresh_build_status()
    elif action == "frontend":
        logging.info("Loading frontend")
        frontend.app.run(debug=True, use_reloader=False)
    else:
        raise KeyError("Please enter either frontend or update")


class NixCbm:
    """ "
    Main class to save important state information
    """

    def __init__(self) -> None:
        self.nixpkgs_repo = Config.NIXPKGS_WORKDIR
        self.maintainer = Config.MAINTAINER
        self.maintained_packages: list[str] = []
        self.hydra_build_status: dict = {}

    def find_maintained_packages(self, maintainer: str = Config.MAINTAINER) -> None:
        """ "
        find all occurrences of a given maintainer
        INPUT: maintainer, string.
        OUTPUT: package names, List of strings.
        """
        logging.info(f"Will look for {maintainer}")
        current_dir = os.path.dirname(os.path.realpath(__file__))
        cmd = [
            "nix-shell",
            os.path.join(current_dir, "nix", "check-maintainer.nix"),
            "--argstr",
            "maintainer",
            maintainer,
            "-I",
            "nixpkgs=" + self.nixpkgs_repo,
        ]

        with tempfile.NamedTemporaryFile(mode="w") as tmp:
            subprocess.run(cmd, stdout=tmp, check=True)
            tmp.flush()
            with open(tmp.name) as f:
                # remove trailing newline at the end
                stdout = f.read().replace("\n", "")
                self.maintained_packages = stdout.split(",")

    def check_hydra_status(self, packages: list[str]) -> None:
        """
        Check the hydra build status of a set of packages
        Parameters
        ----------
        packages: list[str]
            a list of packages to check
        """
        logging.info("Will now look for hydra build failures")
        arch = "x86_64-linux"
        for package in packages:
            cmd = [
                "hydra-check",
                package,
                "--channel",
                "master",
                "--arch=" + arch,
                "--json",
            ]
            result = subprocess.run(cmd, capture_output=True, check=True)
            # JSON format
            # {'icon': '✔', 'success': True, 'status': 'Succeeded',
            # 'timestamp': '2020-02-19T09:45:37Z', 'build_id': '113137688',
            # 'build_url': 'https://hydra.nixos.org/build/113137688',
            # 'name': 'pgadmin3-1.22.2', 'arch': 'x86_64-linux', 'evals': True}
            self.hydra_build_status[package] = json.loads(result.stdout)


if __name__ == "__main__":
    main()

# functionality to implement
# 2) git fetch current master
# 3) search all packages for a given maintainer

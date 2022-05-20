import datetime
import json
import logging
import os
import subprocess
import tempfile
from typing import Optional

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


class InsertOrUpdate:
    def __init__(self, package: str, hydra_output: dict, result: bool):
        self.package = package
        self.hydra_output = hydra_output
        self.result = result

    def convert_timestamp(self) -> Optional[datetime.datetime]:

        try:
            timestamp_str = str(self.hydra_output[self.package][0]["timestamp"])
            timestamp_str = timestamp_str.replace("Z", "+00:00")
            timestamp = datetime.datetime.fromisoformat(timestamp_str)
        except KeyError:
            timestamp = None
        return timestamp

    def convert_build_url(self) -> Optional[str]:
        try:
            build_url = str(self.hydra_output[self.package][0]["build_url"])
        except KeyError:
            build_url = None
        return build_url

    def check_for_package(self) -> models.Packages:
        return models.Packages.query.filter_by(name=self.package).first()

    def insert_or_update(self) -> None:
        if self.check_for_package():
            logging.debug(f"Updating {self.package}")
            self.update()
        else:
            logging.debug(f"Adding {self.package}")
            frontend.db.session.add(self.create_db_entry())
        frontend.db.session.commit()

    def create_db_entry(self) -> models.Packages:
        db_entry = models.Packages(
            name=self.package,
            hydra_status=self.result,
            build_url=self.convert_build_url(),
            timestamp=self.convert_timestamp(),
            last_checked=datetime.datetime.now(),
        )
        return db_entry

    def update(self) -> None:
        current_package = self.check_for_package()
        current_package.hydra_status = self.result
        current_package.build_url = self.convert_build_url()
        current_package.timestamp = self.convert_timestamp()
        current_package.last_checked = datetime.datetime.now()


def refresh_build_status(reload_maintainer: bool = False) -> None:
    nixcbm = NixCbm()
    nixcbm.nixpkgs_repo = Config.NIXPKGS_WORKDIR
    if reload_maintainer:
        nixcbm.update_maintained_packages_list(Config.MAINTAINER)
        nixcbm.save_maintained_packages_to_db()
    nixcbm.load_maintained_packages_from_database()
    nixcbm.check_hydra_status(nixcbm.maintained_packages)
    # TODO: Add other architectures

    for package, hydra_output in nixcbm.hydra_build_status.items():
        result = _get_build_status_from_json(hydra_output[package])
        insert_or_update = InsertOrUpdate(package, hydra_output, result)
        insert_or_update.insert_or_update()


def main() -> None:
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

    def update_maintained_packages_list(
        self, maintainer: str = Config.MAINTAINER
    ) -> None:
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

    def save_maintained_packages_to_db(self) -> None:
        list_of_packages_in_db = models.Packages.query.all()
        list_of_packages_in_db_list = []
        for package in list_of_packages_in_db:
            list_of_packages_in_db_list.append(package.name)

        for package in self.maintained_packages:
            if package not in list_of_packages_in_db_list:
                logging.debug(f"saving {package} to database")
                insert = InsertOrUpdate(package, {}, False)
                insert.insert_or_update()
            else:
                logging.debug(f"Package {package} already in database. Skipping.")

    def load_maintained_packages_from_database(self) -> None:
        list_of_packages_in_db = models.Packages.query.all()

        for package in list_of_packages_in_db:
            logging.debug(f"found {package} in database")
            if package.name not in self.maintained_packages:
                self.maintained_packages.append(package.name)

    def check_hydra_status(self, packages: list[str], arch: str = "x86_64-linux") -> None:
        """
        Check the hydra build status of a set of packages
        Parameters
        ----------
        arch: str = "x86_64-linux"
            which architecture to check
        packages: list[str]
            a list of packages to check
        """
        logging.info("Will now look for hydra build failures")
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

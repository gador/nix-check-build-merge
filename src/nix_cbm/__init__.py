import json
import logging
import os
import subprocess
import tempfile

import click

from nix_cbm import models  # noqa: F401
from nix_cbm import checks, frontend, git
from nix_cbm.config import Config

logging.basicConfig(level=logging.DEBUG)


def _preflight(nixpkgs_path: str) -> bool:
    """
    Check if all running conditions are met.
    Also, cd to the nixpkgs dir.
    OUTPUT: ok, bool.
    """
    logging.debug("running preflight checklist")
    missing_programs = checks.check_tools()
    if missing_programs:
        raise LookupError(
            f"The following programs are missing: + ${str(missing_programs)}"
        )
    checks.check_nixpkgs_dir(nixpkgs_path)
    git.git_pull(nixpkgs_path)
    git.git_checkout(nixpkgs_path)
    return True


def _get_build_status_from_json(package_json: dict):
    # the 0 implies the most recent build
    return package_json[0]["success"]


def main() -> None:
    # TODO add CLI and API interface
    cli()


@click.command()
@click.option("--nixpkgs", default=".", help="path to nixpkgs")
@click.option("--maintainer", help="maintainer to look for")
@click.argument("action")
def cli(nixpkgs, maintainer, action):
    """
    CLI interface for nix-check-build-merge.\n
    Use "maintainer" for checking the build status for all packages belonging to "maintainer"\n
    Use "frontend" to test the frontend
    """
    if action == "maintainer":
        _preflight(nixpkgs)
        nixcbm = NixCbm()
        nixcbm.nixpkgs_repo = nixpkgs
        nixcbm.find_maintained_packages(maintainer)
        nixcbm.check_hydra_status(nixcbm.maintained_packages)

        # just a stub/demonstration of the current packages
        # TODO: Add a frontend to display them nicely
        for package, hydra_output in nixcbm.hydra_build_status.items():
            result = _get_build_status_from_json(hydra_output[package])
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
    elif action == "frontend":
        _preflight(nixpkgs)
        logging.info("Loading frontend")
        logging.debug(f"sqlite db is at {Config.SQLALCHEMY_DATABASE_URI}")
        frontend.app.run(debug=True)
    else:
        raise KeyError("Please enter either frontend or maintainer")


class NixCbm:
    """ "
    Main class to save important state information
    """

    def __init__(self):
        self.nixpkgs_repo = ""
        self.maintained_packages = []
        self.hydra_build_status = {}

    def find_maintained_packages(self, maintainer: str):
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

    def check_hydra_status(self, packages: list[str]):
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

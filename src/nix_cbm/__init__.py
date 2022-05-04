import logging
import os
import subprocess
import tempfile

import click

from nix_cbm import checks, git

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


def main() -> None:
    # TODO add CLI and API interface
    cli()


@click.command()
@click.option("--nixpkgs", default=".", help="path to nixpkgs")
@click.argument("maintainer")
def cli(nixpkgs, maintainer):
    """
    CLI interface for nix-check-build-merge
    """
    _preflight(nixpkgs)
    nixcbm = NixCbm()
    nixcbm.nixpkgs_repo = nixpkgs
    nixcbm.find_maintained_packages(maintainer)
    logging.info(str(nixcbm.maintained_packages))


class NixCbm:
    """ "
    Main class to save important state information
    """

    def __init__(self):
        self.nixpkgs_repo = ""
        self.maintained_packages = []

    def find_maintained_packages(self, maintainer: str):
        """"
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
                stdout = f.read()
                self.maintained_packages = stdout.split(",")

    def check_hydra_status(self, packages: list):
        logging.info("Will now look for hydra build failures")


if __name__ == "__main__":
    main()

# functionality to implement
# 2) git fetch current master
# 3) search all packages for a given maintainer

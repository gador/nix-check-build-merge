import logging
import os
import subprocess
import sys
import tempfile

import checks
import git

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
        sys.exit("The following programs are missing: " + str(missing_programs))
    checks.check_nixpkgs_dir(nixpkgs_path)
    git.git_checkout("testcommit")
    return True


def main() -> None:
    # TODO add CLI and API interface
    nixpkgs_dir = "/home/wogan/software/git/nixpkgs"
    maintainer = "gador"

    if not _preflight(nixpkgs_dir):
        exit(1)

    nixcbm = NixCbm()
    nixcbm.nixpkgs_repo = nixpkgs_dir
    nixcbm.find_maintainer(maintainer)
    logging.info(str(nixcbm.maintained_packages))


class NixCbm:
    """ "
    Main class to save important state information
    """

    def __init__(self):
        self.nixpkgs_repo = ""
        self.maintained_packages = []

    def find_maintainer(self, maintainer: str):
        """ "
        find all occurances of a given maintainer
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
        # stdout = subprocess.run(cmd, check=True).stdout()
        # self.maintained_packages =
        with tempfile.NamedTemporaryFile(mode="w") as tmp:
            subprocess.run(cmd, stdout=tmp, check=True)
            tmp.flush()
            with open(tmp.name) as f:
                stdout = f.read()
                self.maintained_packages = stdout.split(",")


if __name__ == "__main__":
    main()

# functionality to implement
# 1) check, whether we are in nixpkgs local repo
# 2) git fetch current master
# 3) search all packages for a given maintainer

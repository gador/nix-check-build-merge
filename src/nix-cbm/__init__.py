import logging
import sys

import checks
import git

logging.basicConfig(level=logging.DEBUG)


def _preflight() -> bool:
    """
    Check if all running conditions are met.
    OUTPUT: ok, bool.
    """
    logging.debug("running preflight checklist")
    missing_programs = checks.check_tools()
    if missing_programs:
        sys.exit("The following programs are missing: " + str(missing_programs))
    checks.check_nixpkgs_dir()
    git.git_checkout("testcommit")
    return True


# TODO: add function
def find_maintainer(maintainer: str) -> list[str]:
    """ "
    find all occurances of a given maintainer
    INPUT: maintainer, string.
    OUTPUT: package names, list of strings.
    """
    logging.info(f"Will look for {maintainer}")
    return []


def main() -> None:
    _preflight()
    packages = find_maintainer("gador")
    logging.info(str(packages))


if __name__ == "__main__":
    main()

# functionality to implement
# 1) check, whether we are in nixpkgs local repo
# 2) git fetch current master
# 3) search all packages for a given maintainer

import logging
import sys

import check_tools

logging.basicConfig(level=logging.DEBUG)


def main() -> None:
    _preflight()


def _preflight() -> bool:
    """
    Check if all running conditions are met.
    OUTPUT: ok, bool.
    """
    logging.debug("running preflight checklist")
    missing_programs = check_tools.checkTools()
    if missing_programs:
        sys.exit("The following programs are missing: " + str(missing_programs))
    return True


if __name__ == "__main__":
    main()

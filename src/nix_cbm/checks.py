import logging
import os
from shutil import which


def _exists(name: str) -> bool:
    """
    Check for the existence of a program
    INPUT: Name, string.
    OUTPUT: exists, bool.
    """
    return which(name) is not None


def check_tools(
    programs_to_check: list[str] = ["rg", "git", "nix", "hydra-check"]
) -> list[str]:
    """
    Check for all needed programs.
    INPUT: programs to check, List of str.
    OUTPUT: Missing packages, List of str.
    """
    missing_programs = []
    for program in programs_to_check:
        if not _exists(program):
            missing_programs.append(program)
    return missing_programs


def check_nixpkgs_dir(nixpkgs_path: str) -> bool:
    """
    Checks, whether we are in a nixpkgs repo dir.
    INPUT: nixpkgs path. This needs to be inside the home directory of the user!
    OUTPUT: ok, bool.
    """
    # checks for the following:
    # 1) .git dir present
    # 2) default.nix present
    # 3) .version present

    base_path = os.path.expanduser("~")
    fullpath = os.path.normpath(os.path.join(base_path, nixpkgs_path))
    if not fullpath.startswith(base_path):
        raise NotADirectoryError(
            f"The provided path {str(nixpkgs_path)} evaluates to {str(fullpath)} which tries to escape the home directory path"
        )

    if not os.path.exists(os.path.normpath(os.path.join(fullpath, ".git"))):
        logging.warning(f"Directory {fullpath} doesn't seem to be a nixpkgs repo")
        return False
    if not os.path.exists(os.path.normpath(os.path.join(fullpath, "default.nix"))):
        logging.warning(f"Directory {fullpath} doesn't seem to be a nixpkgs repo")
        return False
    if not os.path.exists(os.path.normpath(os.path.join(fullpath, ".version"))):
        logging.warning(f"Directory {fullpath} doesn't seem to be a nixpkgs repo")
        return False
    return True

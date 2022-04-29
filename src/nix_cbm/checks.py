import logging
import os
from shutil import which


def _exists(name: str) -> str:
    """
    Check for the existence of a program
    INPUT: Name, string.
    OUTPUT: exists, bool.
    """
    return which(name) is not None


def check_tools() -> list[str]:
    """
    Check for all needed programs.
    INPUT: None
    OUTPUT: Missing packages, List of str.
    """
    missing_programs = []
    programs_to_check = ["rg", "git", "nix"]
    for program in programs_to_check:
        if not _exists(program):
            missing_programs.append(program)
    return missing_programs


def check_nixpkgs_dir(nixpkgs_path: str) -> bool:
    """
    Checks, whether we are in a nixpkgs repo dir.
    INPUT: None
    OUTPUT: ok, bool.
    """
    # checks for two things:
    # 1) .git dir present
    # 2) default.nix present
    # 3) .version present
    git_dir = os.path.exists(os.path.join(nixpkgs_path, ".git"))
    default_nix = os.path.exists(os.path.join(nixpkgs_path, "default.nix"))
    version = os.path.exists(os.path.join(nixpkgs_path, ".version"))
    if git_dir and default_nix and version:
        return True
    logging.error(f"Directory {nixpkgs_path} doesn't seem to be a nixpkgs repo")
    exit(1)
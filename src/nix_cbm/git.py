import logging
import subprocess
from pathlib import Path
from typing import Optional, Union


def _sh(
    command: list[str], cwd: Optional[Union[Path, str]] = None, check: bool = True
) -> "subprocess.CompletedProcess[str]":
    """

    Parameters
    ----------
    command: list[str]
        the command to execute
    cwd: str
        the working directory
    check: bool, default: True
        raise an error if non-zero return code

    Returns
    -------
    subprocess.CompletedProcess
        stdout, stderr and return_code of command
    """
    logging.info("$ " + " ".join(command))
    return subprocess.run(command, cwd=cwd, check=check, text=True)


def git_pull(repo: str, commit: str = "master", remote: str = "origin"):
    """
    Pull the current refs from remote
    Parameters
    ----------
    repo: str
        The path to the repository
    commit: str, default: master
        The commit or branch to pull
    remote: str, default: origin
        The remote to pull from

    Returns
    -------
    bool
        True if successful
    """
    logging.info(f"Will now pull {str(commit)} from {str(remote)}")
    cmd = ["git", "pull", remote, commit]
    return_code = _sh(cmd, cwd=repo).returncode
    if return_code == 0:
        return True
    else:
        return False


def git_checkout(repo: str, commit: str = "master") -> bool:
    """
    Checkout the local nixpkgs to the specified commit
    Parameters
    ----------
    repo: str
        The path to the repository
    commit: str, default: master
        The commit or branch to check out
    Returns
    -------
    bool
        True if successful
    """
    logging.info(f"Will now checkout commit {str(commit)}")
    cmd = ["git", "checkout", commit]
    return_code = _sh(cmd, cwd=repo).returncode
    if return_code == 0:
        return True
    else:
        return False

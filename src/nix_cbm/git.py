import logging
import os.path
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
    return not bool(_sh(cmd, cwd=repo).returncode)


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
    return not bool(_sh(cmd, cwd=repo).returncode)  # exit code 0 would otherwise be False


def git_fetch(
    repo: str, remote_repo: str = "https://github.com/NixOS/nixpkgs", base: str = "master"
):
    cmd = [
        "git",
        "-c",
        "fetch.prune=false",
        "fetch",
        "--no-tags",
        "--force",
        remote_repo,
        f"{base}:refs/nixcbm/0",
    ]
    _sh(cmd, cwd=repo)
    shas = []
    out = subprocess.check_output(
        ["git", "rev-parse", "--verify", "refs/nixpkgs-review/0"], text=True
    )
    shas.append(out.strip())
    return shas


def git_worktree(nixpkgs_dir: str, repo: str, commit: str = "master") -> bool:
    """
    create a worktree of the local nixpkgs repo
    Parameters
    ----------
    nixpkgs_dir: str
        Path to the worktree
    repo: str
        Path to the local, original, nixpkgs repo
    commit: str = "master"
        What commit to checkout at the worktree. Defaults to "master"

    Returns
    -------
    bool:
        True if successful

    """
    if not os.path.exists(nixpkgs_dir):
        cmd = ["git", "worktree", "add", "-f", "-B", "nixcbm-master", nixpkgs_dir, commit]
        return not bool(_sh(cmd, cwd=repo, check=False).returncode)
    else:
        return True

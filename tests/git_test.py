import subprocess
import unittest
from unittest import mock

from nix_cbm import git


class GitTestCase(unittest.TestCase):
    @mock.patch("subprocess.run")
    def test_sh(self, process):
        self.assertTrue(git._sh(["pwd"], "/", check=False))
        process.assert_called_with(["pwd"], cwd="/", check=False, text=True)

    @mock.patch(
        "nix_cbm.git._sh", return_value=subprocess.CompletedProcess(args="", returncode=0)
    )
    def test_git_pull(self, mock_sh):
        self.assertTrue(
            git.git_pull(repo="test_repo", commit="test_commit", remote="test_remote")
        )
        mock_sh.return_value = subprocess.CompletedProcess(args="", returncode=1)
        self.assertFalse(
            git.git_pull(repo="test_repo", commit="test_commit", remote="test_remote")
        )

    @mock.patch(
        "nix_cbm.git._sh", return_value=subprocess.CompletedProcess(args="", returncode=0)
    )
    def test_git_checkout(self, mock_sh):
        self.assertTrue(git.git_checkout(repo="test_repo", commit="test_commit"))
        mock_sh.return_value = subprocess.CompletedProcess(args="", returncode=1)
        self.assertFalse(git.git_checkout(repo="test_repo", commit="test_commit"))

    @mock.patch("subprocess.check_output")
    @mock.patch("nix_cbm.git._sh")
    def test_git_fetch(self, sh, subprocess):
        """test_git_fetch mocks the git fetch call

        asserts the correct subprocess call
        """
        subprocess.return_value = "list1"
        self.assertListEqual(git.git_fetch("/", "remote", "main"), ["list1"])
        cmd = [
            "git",
            "-c",
            "fetch.prune=false",
            "fetch",
            "--no-tags",
            "--force",
            "remote",
            "main:refs/nixcbm/0",
        ]
        sh.assert_called_with(cmd, cwd="/")
        subprocess.assert_called_with(
            ["git", "rev-parse", "--verify", "refs/nixpkgs-review/0"], text=True
        )

    @mock.patch("nix_cbm.git._sh")
    @mock.patch("os.path.exists")
    def test_git_worktree(self, path, sh):
        path.return_value = True
        self.assertTrue(git.git_worktree("/", "repo", "main"))

        path.return_value = False
        sh.return_value.returncode = 0
        cmd = ["git", "worktree", "add", "-f", "-B", "nixcbm-master", "/", "main"]
        self.assertTrue(git.git_worktree("/", "repo", "main"))
        sh.assert_called_with(cmd, cwd="repo", check=False)

        sh.return_value.returncode = 128
        self.assertFalse(git.git_worktree("/", "repo", "main"))
        sh.assert_called_with(cmd, cwd="repo", check=False)


if __name__ == "__main__":
    unittest.main()

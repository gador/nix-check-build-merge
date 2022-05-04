import unittest
from nix_cbm import git
from unittest import mock
import subprocess


class GitTestCase(unittest.TestCase):

    @mock.patch("nix_cbm.git._sh", return_value=subprocess.CompletedProcess(args="", returncode=0))
    def test_git_pull(self, mock_sh):
        self.assertTrue(git.git_pull(repo="test_repo",commit="test_commit", remote="test_remote"))
        mock_sh.return_value=subprocess.CompletedProcess(args="", returncode=1)
        self.assertFalse(git.git_pull(repo="test_repo",commit="test_commit", remote="test_remote"))

    @mock.patch("nix_cbm.git._sh", return_value=subprocess.CompletedProcess(args="", returncode=0))
    def test_git_checkout(self, mock_sh):
        self.assertTrue(git.git_checkout(repo="test_repo", commit="test_commit"))
        mock_sh.return_value = subprocess.CompletedProcess(args="", returncode=1)
        self.assertFalse(git.git_checkout(repo="test_repo", commit="test_commit"))


if __name__ == '__main__':
    unittest.main()

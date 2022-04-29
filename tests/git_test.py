import unittest
from nix_cbm import git

# TODO adjust, when function is implemented
class gitTestCase(unittest.TestCase):
    def test_git_checkout(self):
        self.assertTrue(git.git_checkout("abcdefgh"))


if __name__ == '__main__':
    unittest.main()

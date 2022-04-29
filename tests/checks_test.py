import unittest
import nix_cbm.checks as checks


class MyTestCase(unittest.TestCase):
    def test_exists(self):
        self.assertFalse(checks._exists("non_existing_program"))
        self.assertTrue(checks._exists("python")) 


if __name__ == '__main__':
    unittest.main()

import unittest

from calc import ops


class OpsTest(unittest.TestCase):
    def test_add(self):
        self.assertEqual(ops.add(2, 3), 5)

    def test_mul(self):
        self.assertEqual(ops.mul(4, 3), 12)


if __name__ == "__main__":
    unittest.main()

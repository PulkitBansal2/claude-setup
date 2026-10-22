import unittest

from calc import stats


class StatsTest(unittest.TestCase):
    def test_mean(self):
        self.assertEqual(stats.mean([1, 2, 3, 4]), 2.5)

    def test_median_odd(self):
        self.assertEqual(stats.median([3, 1, 2]), 2)

    def test_median_even(self):
        self.assertEqual(stats.median([4, 1, 3, 2]), 2.5)


if __name__ == "__main__":
    unittest.main()

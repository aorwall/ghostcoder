import unittest
from coffee_machine_program import max_coffee_cups

class TestMaxCoffeeCups(unittest.TestCase):
    def test_max_coffee_cups(self):
        # Test case for normal inputs
        self.assertEqual(max_coffee_cups(36, 400), 2)

    def test_not_enough_resources(self):
        # Test case where there's not enough resources for even one cup
        self.assertEqual(max_coffee_cups(10, 100), 0)

    def test_only_enough_coffee_for_one_cup(self):
        # Test case where there's only enough coffee for one cup
        self.assertEqual(max_coffee_cups(18, 400), 1)

    def test_only_enough_water_for_one_cup(self):
        # Test case where there's only enough water for one cup
        self.assertEqual(max_coffee_cups(36, 200), 1)

    def test_zero_resources(self):
        # Test case where there's no resources
        self.assertEqual(max_coffee_cups(0, 0), 0)

if __name__ == '__main__':
    unittest.main()
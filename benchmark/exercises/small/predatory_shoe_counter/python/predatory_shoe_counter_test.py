import unittest
from predatory_shoe_counter import predatory_shoe_counter

class TestPredatoryShoeCounter(unittest.TestCase):
    def test_basic_case(self):
        distance = [10, 20, 30]
        time = [1, 2, 3]
        self.assertEqual(predatory_shoe_counter(distance, time), 3)

    def test_same_attack_time(self):
        distance = [10, 20, 30]
        time = [1, 1, 3]
        self.assertEqual(predatory_shoe_counter(distance, time), 2)

    def test_large_input(self):
        distance = [i for i in range(1, 10**5+1)]
        time = [i % 1000 for i in range(1, 10**5+1)]  # Modulo operation to keep time values within limit
        self.assertEqual(predatory_shoe_counter(distance, time), 1000)  # Expecting 1000 unique time values

    def test_large_input_with_same_values(self):
        distance = [1 for i in range(1, 10**5+1)]
        time = [1 for i in range(1, 10**5+1)]
        self.assertEqual(predatory_shoe_counter(distance, time), 1)

    def test_non_negative_values(self):
        distance = [0, 0, 0]
        time = [0, 0, 0]
        self.assertEqual(predatory_shoe_counter(distance, time), 1)

    def test_negative_values(self):
        distance = [-10, -20, -30]
        time = [-1, -2, -3]
        with self.assertRaises(ValueError):
            predatory_shoe_counter(distance, time)

    def test_time_values_do_not_exceed_limit(self):
        distance = [10, 20, 30]
        time = [1000, 1000, 1000]
        self.assertEqual(predatory_shoe_counter(distance, time), 1)

    def test_time_values_exceed_limit(self):
        distance = [10, 20, 30]
        time = [1001, 1002, 1003]
        with self.assertRaises(ValueError):
            predatory_shoe_counter(distance, time)

if __name__ == '__main__':
    unittest.main()
import unittest
from odd_animal_party import odd_animal_party

class TestOddAnimalParty(unittest.TestCase):
    def test_empty_list(self):
        animals = []
        self.assertEqual(odd_animal_party(animals), (False, ''))

    def test_unique_attributes(self):
        animals = [{'color': 'red', 'legs': 4}, {'color': 'blue', 'legs': 2}, {'color': 'green', 'legs': 3}]
        self.assertEqual(odd_animal_party(animals), (False, ''))

    def test_multiple_common_attributes(self):
        animals = [{'color': 'red', 'legs': 4, 'size': 'big'}, {'color': 'red', 'legs': 4, 'size': 'big'}, {'color': 'red', 'legs': 4, 'size': 'big'}]
        self.assertEqual(odd_animal_party(animals), (True, 'color'))
    def test_valid_party(self):
        animals = [{'color': 'red', 'legs': 4}, {'color': 'red', 'legs': 2}, {'color': 'red', 'legs': 4}]
        self.assertEqual(odd_animal_party(animals), (True, 'color'))

    def test_invalid_party_even_animals(self):
        animals = [{'color': 'red', 'legs': 4}, {'color': 'red', 'legs': 2}]
        self.assertEqual(odd_animal_party(animals), (False, ''))

    def test_invalid_party_no_common_attribute(self):
        animals = [{'color': 'red', 'legs': 4}, {'color': 'blue', 'legs': 2}, {'color': 'green', 'legs': 3}]
        self.assertEqual(odd_animal_party(animals), (False, ''))

    def test_valid_party_common_legs(self):
        animals = [{'color': 'red', 'legs': 4}, {'color': 'blue', 'legs': 4}, {'color': 'green', 'legs': 4}]
        self.assertEqual(odd_animal_party(animals), (True, 'legs'))

    def test_large_input(self):
        animals = [{'color': 'red', 'legs': 4}]*1001
        self.assertEqual(odd_animal_party(animals), (True, 'color'))

if __name__ == '__main__':
    unittest.main()
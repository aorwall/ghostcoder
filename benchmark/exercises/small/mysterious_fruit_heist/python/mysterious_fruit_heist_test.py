import unittest
from mysterious_fruit_heist import update_inventory

class TestUpdateInventory(unittest.TestCase):
    def test_update_inventory(self):
        """
        This test case tests the basic functionality of the update_inventory function.
        It checks if the function correctly updates the inventory based on the disappeared fruits.
        """
        inventory = ['apple', 'banana', 'cherry', 'apple']
        disappeared = ['apple', 'cherry']
        expected_output = ['banana', 'apple']
        self.assertEqual(update_inventory(inventory, disappeared), expected_output)

    def test_disappeared_fruit_not_in_inventory(self):
        """
        This test case tests if the function correctly ignores the fruits from the disappeared list that do not exist in the inventory.
        """
        inventory = ['apple', 'banana', 'cherry']
        disappeared = ['apple', 'grape']
        expected_output = ['banana', 'cherry']
        self.assertEqual(update_inventory(inventory, disappeared), expected_output)

    def test_empty_disappeared_list(self):
        """
        This test case tests if the function correctly handles an empty disappeared list.
        """
        inventory = ['apple', 'banana', 'cherry']
        disappeared = []
        expected_output = ['apple', 'banana', 'cherry']
        self.assertEqual(update_inventory(inventory, disappeared), expected_output)

    def test_empty_inventory_list(self):
        """
        This test case tests if the function correctly handles an empty inventory list.
        """
        inventory = []
        disappeared = ['apple', 'banana']
        expected_output = []
        self.assertEqual(update_inventory(inventory, disappeared), expected_output)

    def test_multiple_disappeared_fruits(self):
        """
        This test case tests if the function correctly handles multiple instances of the same fruit in the disappeared list.
        """
        inventory = ['apple', 'banana', 'cherry', 'apple', 'apple']
        disappeared = ['apple', 'apple']
        expected_output = ['banana', 'cherry', 'apple']
        self.assertEqual(update_inventory(inventory, disappeared), expected_output)

if __name__ == '__main__':
    unittest.main()
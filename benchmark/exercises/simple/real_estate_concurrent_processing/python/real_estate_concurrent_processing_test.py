import unittest
from real_estate_concurrent_processing import Property, calculate_price, calculate_prices_concurrently

class TestRealEstateConcurrentProcessing(unittest.TestCase):
    def setUp(self):
        self.properties = [
            Property("Location1", 1000, 2, 1, 10),
            Property("Location2", 2000, 3, 2, 5),
            Property("Location3", 1500, 1, 1, 20)
        ]

    def test_property_initialization(self):
        property = self.properties[0]
        self.assertEqual(property.location, "Location1")
        self.assertEqual(property.square_footage, 1000)
        self.assertEqual(property.bedrooms, 2)
        self.assertEqual(property.bathrooms, 1)
        self.assertEqual(property.age, 10)

    def test_calculate_price(self):
        property = self.properties[0]
        property = calculate_price(property)
        self.assertEqual(property.price, 1000*200 + 2*5000 - 10*1000)

    def test_calculate_prices_concurrently(self):
        properties = calculate_prices_concurrently(self.properties)
        self.assertEqual(properties[0].price, 1000*200 + 2*5000 - 10*1000)
        self.assertEqual(properties[1].price, 2000*200 + 3*5000 - 5*1000)
        self.assertEqual(properties[2].price, 1500*200 + 1*5000 - 20*1000)

    def test_thread_safety(self):
        properties = self.properties * 1000  # Create a large number of properties
        try:
            properties = calculate_prices_concurrently(properties)
            for i in range(0, len(properties), 3):
                self.assertEqual(properties[i].price, 1000*200 + 2*5000 - 10*1000)
                self.assertEqual(properties[i+1].price, 2000*200 + 3*5000 - 5*1000)
                self.assertEqual(properties[i+2].price, 1500*200 + 1*5000 - 20*1000)
        except Exception as e:
            self.fail(f"calculate_prices_concurrently raised an exception with a large number of properties: {e}")

if __name__ == '__main__':
    unittest.main()
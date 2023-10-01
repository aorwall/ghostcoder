import unittest
import time
from sales_queries import CustomerDatabase

class TestCustomerDatabase(unittest.TestCase):
    def setUp(self):
        self.db = CustomerDatabase()

    def test_add_customer(self):
        self.db.add_customer(1, 'John Doe', 1000.0)
        self.assertEqual(self.db.customers[1].name, 'John Doe')
        self.assertEqual(self.db.customers[1].total_purchases, 1000.0)

    def test_add_customer_with_same_id(self):
        self.db.add_customer(1, 'John Doe', 1000.0)
        with self.assertRaises(ValueError):
            self.db.add_customer(1, 'Jane Doe', 2000.0)

    def test_add_customer_with_long_name(self):
        with self.assertRaises(ValueError):
            self.db.add_customer(1, 'a'*101, 1000.0)

    def test_add_customer_with_large_id(self):
        with self.assertRaises(ValueError):
            self.db.add_customer(10001, 'John Doe', 1000.0)

    def test_add_customer_with_invalid_purchase(self):
        with self.assertRaises(ValueError):
            self.db.add_customer(1, 'John Doe', 1000001.0)

    def test_delete_customer(self):
        self.db.add_customer(1, 'John Doe', 1000.0)
        self.db.delete_customer(1)
        self.assertNotIn(1, self.db.customers)

    def test_delete_non_existent_customer(self):
        with self.assertRaises(ValueError):
            self.db.delete_customer(1)

    def test_get_all_customers(self):
        self.db.add_customer(1, 'John Doe', 1000.0)
        self.db.add_customer(2, 'Jane Doe', 2000.0)
        customers = self.db.get_all_customers()
        self.assertEqual(customers[0].id, 2)
        self.assertEqual(customers[1].id, 1)

    def test_update_purchase(self):
        self.db.add_customer(1, 'John Doe', 1000.0)
        self.db.update_purchase(1, 500.0)
        self.assertEqual(self.db.customers[1].total_purchases, 1500.0)

    def test_add_more_than_max_customers(self):
        for i in range(1000):
            self.db.add_customer(i, 'John Doe', 1000.0)
        with self.assertRaises(ValueError):
            self.db.add_customer(1000, 'John Doe', 1000.0)

    def test_many_function_calls(self):
        start_time = time.time()
        for i in range(100):
            self.db.add_customer(i, 'John Doe', 1000.0)
        end_time = time.time()
        self.assertLess(end_time - start_time, 1)

        start_time = time.time()
        for i in range(100):
            self.db.delete_customer(i)
        end_time = time.time()
        self.assertLess(end_time - start_time, 1)

        for i in range(100, 200):
            self.db.add_customer(i, 'John Doe', 1000.0)

        start_time = time.time()
        for i in range(100, 200):
            self.db.update_purchase(i, 500.0)
        end_time = time.time()
        self.assertLess(end_time - start_time, 1)

    def test_update_purchase_invalid_amount(self):
        self.db.add_customer(1, 'John Doe', 1000.0)
        with self.assertRaises(ValueError):
            self.db.update_purchase(1, 1000001.0)

    def test_many_function_calls(self):
        start_time = time.time()
        for i in range(100):
            self.db.add_customer(i, 'John Doe', 1000.0)
        end_time = time.time()
        self.assertLess(end_time - start_time, 1)

    def test_update_purchase_non_existent_customer(self):
        with self.assertRaises(ValueError):
            self.db.update_purchase(1, 500.0)

if __name__ == '__main__':
    unittest.main()
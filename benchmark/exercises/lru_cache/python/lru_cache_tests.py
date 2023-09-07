import unittest

from lru_cache import LRUCache

class TestLRUCache(unittest.TestCase):

    def test_put_and_get(self):
        lru = LRUCache(2)

        lru.put(1, 10)
        self.assertEqual(lru.get(1), 10)

        lru.put(2, 20)
        self.assertEqual(lru.get(1), 10)
        self.assertEqual(lru.get(2), 20)

    def test_eviction(self):
        lru = LRUCache(2)

        lru.put(1, 10)
        lru.put(2, 20)
        lru.put(3, 30)

        self.assertEqual(lru.get(1), None)
        self.assertEqual(lru.get(2), 20)
        self.assertEqual(lru.get(3), 30)

    def test_update_value(self):
        lru = LRUCache(2)

        lru.put(1, 10)
        lru.put(1, 100)

        self.assertEqual(lru.get(1), 100)

    def test_lru_order(self):
        lru = LRUCache(3)

        lru.put(1, 10)
        lru.put(2, 20)
        lru.put(3, 30)

        # Access key 1, making it most recently used
        lru.get(1)

        # Add another key to trigger eviction
        lru.put(4, 40)

        # Key 2 should have been evicted (least recently used)
        self.assertEqual(lru.get(2), None)


if __name__ == '__main__':
    unittest.main()

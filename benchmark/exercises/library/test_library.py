import unittest
from book_manager import BookManager
from patron_manager import PatronManager


class TestLibrary(unittest.TestCase):

    def setUp(self):
        self.book_mgr = BookManager()
        self.patron_mgr = PatronManager()

    def test_add_and_remove_book(self):
        self.book_mgr.add_book("1984", "George Orwell")
        self.assertIn({"title": "1984", "author": "George Orwell"}, self.book_mgr.get_books())

        self.book_mgr.remove_book("1984")
        self.assertNotIn({"title": "1984", "author": "George Orwell"}, self.book_mgr.get_books())

    def test_add_and_remove_patron(self):
        self.patron_mgr.add_patron("John")
        self.assertIn("John", self.patron_mgr.get_patrons())

        self.patron_mgr.remove_patron("John")
        self.assertNotIn("John", self.patron_mgr.get_patrons())

    def test_input_length_constraint(self):
        long_string = "a" * 101
        self.book_mgr.add_book(long_string, "George Orwell")
        self.assertNotIn({"title": long_string, "author": "George Orwell"}, self.book_mgr.get_books())

        self.patron_mgr.add_patron(long_string)
        self.assertNotIn(long_string, self.patron_mgr.get_patrons())

    def test_unique_constraint(self):
        self.book_mgr.add_book("Unique Title", "Unique Author")
        self.patron_mgr.add_patron("Unique Patron")

        unique_test = len(self.book_mgr.get_books()) + len(self.patron_mgr.get_patrons())
        self.assertEqual(unique_test, 2)


if __name__ == "__main__":
    unittest.main()
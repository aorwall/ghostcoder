# Background
You are tasked with creating a library management system that has two main components: one for managing the list of books, and another for managing patrons who borrow the books.

# Instructions

## 1. Book Manager (book_manager.py)
Create a Python file called book_manager.py and define a class BookManager with the following methods:

* __init__(self): Initialize the book list as an empty list.
* add_book(self, book_title, book_author): Add a book to the library. A book should be a dictionary with a title and an author.
* remove_book(self, book_title): Remove a book from the library by its title.
* get_books(self): Return the list of books in the library.

## 2. Patron Manager (patron_manager.py)
Create another Python file called patron_manager.py and define a class PatronManager with the following methods:

* __init__(self): Initialize the list of patrons as an empty list.
* add_patron(self, name): Add a patron to the library.
* remove_patron(self, name): Remove a patron from the library by their name.
* get_patrons(self): Return the list of patrons.

# Constraints:
* All inputs are strings and can have a maximum length of 100 characters.
* Do not use any third-party libraries.

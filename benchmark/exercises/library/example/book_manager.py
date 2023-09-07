class BookManager:
    def __init__(self):
        self.books = []

    def add_book(self, book_title, book_author):
        if len(book_title) <= 100 and len(book_author) <= 100:
            self.books.append({"title": book_title, "author": book_author})

    def remove_book(self, book_title):
        self.books = [book for book in self.books if book["title"] != book_title]

    def get_books(self):
        return self.books

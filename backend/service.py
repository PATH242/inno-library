"""
This module contains the business logic for the application.
"""

import logging
import sqlite3

from fastapi import HTTPException
from fastapi import status as http_status
from passlib.context import CryptContext

from . import database, models
from .const import SQLITE_DB

context = CryptContext(schemes=["bcrypt"])


class Hasher:
    """
    Class for hashing and verifying passwords.
    """

    @staticmethod
    def password_hash(password):
        """
        Hash a password using bcrypt.
        Returns different hash each time for the same password.
        """
        return context.hash(password)

    @staticmethod
    def password_verification(password, hashed_password):
        """
        Verify a password against a hashed password.
        """

        return context.verify(password, hashed_password)


class User:
    """
    Class for managing users
    """

    @staticmethod
    def create_user(username, password, confirm_password):
        """
        Given user data, creates a user. Checks for the validity of
        password and existing username before proceeding.
        """

        if password != confirm_password:
            raise HTTPException(
                http_status.HTTP_400_BAD_REQUEST,
                "Password and confirmation don't match!",
            )

        password_hash = Hasher.password_hash(password)

        if not User.verify_new_user(username):
            logging.info(f"Service: Creating user: {username}")
            conn = sqlite3.connect(SQLITE_DB)
            database.create_user(username, password_hash, conn)
            conn.close()
        else:
            logging.error(f"Service: Username already exists: {username}")
            raise HTTPException(
                http_status.HTTP_400_BAD_REQUEST, detail="Username already exists!"
            )

    @staticmethod
    def verify_new_user(username):
        """
        Helper function to check if a username exists in the database.
        Return True if user exists, else False
        """

        conn = sqlite3.connect(SQLITE_DB)
        users = database.get_user_by_username(username, conn)
        conn.close()
        return bool(users)

    @staticmethod
    def check_user(username, password):
        """
        Function to verify login.
        Returns the ID of a user if the username and password matches.
        Throws exception, in case of wrong password/
        """
        conn = sqlite3.connect(SQLITE_DB)
        user = database.get_user_by_username(username, conn)
        conn.close()
        if not user:
            logging.error(f"Service: User not found: {username}")
            raise HTTPException(
                http_status.HTTP_404_NOT_FOUND,
                detail="User not found!",
            )
        if not Hasher.password_verification(password, user[2]):
            logging.error(f"Service: Credentials mismatch for {username}")
            raise HTTPException(
                http_status.HTTP_404_NOT_FOUND,
                detail="Credentials mismatch!",
            )
        logging.info(f"Service: User logged in: {username}")
        return user

    @staticmethod
    def get_user(user_id):
        """
        Helper function to return a User instance given a user id
        """
        conn = sqlite3.connect(SQLITE_DB)
        user = database.get_user(user_id, conn)
        conn.close()
        return models.User(id=user[0], username=user[1])


class Book:
    """
    Class related to Book related logic
    """

    @staticmethod
    def from_db(book_id):
        """
        Given a book id, returns a Book class object
        """

        conn = sqlite3.connect(SQLITE_DB)
        book_data = database.get_book(book_id, conn)
        if book_data:
            book = models.Book(
                id=book_data[0],
                title=book_data[1],
                author=book_data[2],
                genre=book_data[3],
                reads=database.get_book_read_count(book_data[0], conn),
            )
            conn.close()
            return book
        raise HTTPException(
            http_status.HTTP_404_NOT_FOUND,
            detail="Book not found!",
        )

    @staticmethod
    def get_books(start: int, n: int):
        """
        Helper function to get a list of books (paginated).
        Converts the database results to Book object.
        Also calculates the previous and next offsets.
        Returns a Books object.
        """

        conn = sqlite3.connect(SQLITE_DB)
        book_data = database.get_books(start, n, conn)
        books = [
            models.Book(
                id=book[0],
                title=book[1],
                author=book[2],
                genre=book[3],
                reads=database.get_book_read_count(book[0], conn),
            )
            for book in book_data
        ]
        count = database.get_book_count(conn)
        conn.close()

        return models.Books(
            books=books,
            previous_n=prev_n if (prev_n := start - n) >= 0 else 0,
            next_n=start_n if (start_n := start + n) < count else None,
        )

    @staticmethod
    def search_book(book_name):
        """
        Search for a book by name.
        """

        conn = sqlite3.connect(SQLITE_DB)
        logging.info(f"Service: Searching for book: {book_name}")
        book_data = database.search_book_by_title(book_name, conn)
        if not book_data:
            logging.error(f"Service: Book not found: {book_name}")
            conn.close()
            return []

        books = [
            models.Book(
                id=book[0],
                title=book[1],
                author=book[2],
                genre=book[3],
                reads=database.get_book_read_count(book[0], conn),
            )
            for book in book_data
        ]
        logging.info(f"Service: {len(books)} books found for: {book_name}")
        conn.close()
        return books

    @staticmethod
    def get_genres():
        """
        Helper function to get the list of genres.
        """
        conn = sqlite3.connect(SQLITE_DB)
        genres = database.get_genres(conn)
        conn.close()
        return genres

    @staticmethod
    def get_books_by_genre(genre):
        """
        Helper function to get the list of books by genre.
        """

        conn = sqlite3.connect(SQLITE_DB)
        book_data = database.get_books_by_genre(genre, conn)
        books = [
            models.Book(
                id=book[0],
                title=book[1],
                author=book[2],
                genre=book[3],
                reads=database.get_book_read_count(book[0], conn),
            )
            for book in book_data
        ]
        books.sort(key=lambda book: book.reads, reverse=True)
        logging.info(f"Service: {len(books)} books found for genre: {genre}")
        conn.close()
        return books[:15]


class ReadingList:
    """
    Class for managing the reading list of a user.
    """

    def __init__(self, user_id):
        """
        Initialize the ReadingList object with the user id.
        """

        self.user_id = user_id
        self.books = []
        self.load()

    def load(self):
        """
        Load's the user's library from the database.
        Converts the database results to MyRead object.
        """

        conn = sqlite3.connect(SQLITE_DB)
        self.books = [
            models.MyRead(
                id=book.id,
                title=book.title,
                author=book.author,
                genre=book.genre,
                reads=book.reads,
                status=entry[3],
                updated_at=entry[5],
            )
            for entry in database.get_reading_lists(self.user_id, conn)
            if (book := Book.from_db(entry[1]))
        ]
        logging.info(
            f"Service: Reading list loaded for user: {self.user_id}."
            f"Total books: {len(self.books)}"
        )
        conn.close()

    def get_genres(self):
        """
        Helper function to get the list of genres user has in the reading list.
        """
        return list(set(book.genre for book in self.books if book))

    def add_book(self, book_id, status=models.StatusEnum.not_started):
        """
        Add a book to the reading list.
        Checks if the book is already in the reading list and throws an error.
        """

        conn = sqlite3.connect(SQLITE_DB)
        if database.get_book_in_reading_list(self.user_id, book_id, conn):
            logging.error(
                f"Service: Book {book_id} already in reading list for user: {self.user_id}"
            )
            conn.close()
            raise HTTPException(
                http_status.HTTP_400_BAD_REQUEST,
                detail="Book already in reading list!",
            )
        database.create_reading_list(self.user_id, book_id, status, conn)
        logging.info(
            f"Service: Book {book_id} added to reading list for user: {self.user_id}"
        )
        conn.close()

    def read_books(self):
        """
        Get the books that have been marked complete by the user.
        """

        conn = sqlite3.connect(SQLITE_DB)
        books = database.get_completed_books(self.user_id, conn)
        conn.close()
        return books

    def remove_book(self, book_id):
        """
        Remove a book from the reading list.
        """

        conn = sqlite3.connect(SQLITE_DB)
        database.remove_from_reading_list(self.user_id, book_id, conn)
        logging.info(
            f"Service: Book {book_id} removed from reading list for user: {self.user_id}"
        )
        conn.close()

    def change_reading_status(self, book_id, status):
        """
        Change the reading status of a book in the reading list.
        """

        conn = sqlite3.connect(SQLITE_DB)
        database.update_reading_status(self.user_id, book_id, status, conn)
        logging.info(
            f"Service: Book {book_id} status updated to {status} for user: {self.user_id}"
        )
        conn.close()

    def get_recommendations(self, n: int = 15):
        """
        Get book recommendations for the user based on the current reading list.
        Returns empty list if the reading list is empty.
        Returns top n books (sorted by number of reads) that are not in the reading list.
        """

        conn = sqlite3.connect(SQLITE_DB)
        # for each genre in the reading list, get the books in that genre
        _books = []
        for genre in self.get_genres():
            _books.extend(database.get_books_by_genre(genre, conn))

        books = list(set(_books))
        books = [Book.from_db(book[0]) for book in books]

        # remove the books that are already in the reading list
        books = [book for book in books if book not in self.books]
        logging.info(
            f"Service: Recommendations generated for user: {self.user_id}. "
            f"Total books: {len(books)}"
        )
        books.sort(key=lambda book: book.reads, reverse=True)
        conn.close()
        return books[:n]

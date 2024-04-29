import sqlite3

from fastapi import HTTPException, status
from passlib.context import CryptContext

from . import database, models
from .const import SQLITE_DB

context = CryptContext(schemes=["bcrypt"])


class Hasher:
    @staticmethod
    def password_hash(password):
        return context.hash(password)

    @staticmethod
    def password_verification(password, hashed_password):
        return context.verify(password, hashed_password)


class User:

    @staticmethod
    def create_user(username, password, confirm_password):
        if password != confirm_password:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                "Password and confirmation don't match!",
            )

        password_hash = Hasher.password_hash(password)

        if not User.verify_new_user(username):
            conn = sqlite3.connect(SQLITE_DB)
            database.create_user(username, password_hash, conn)
            conn.close()
        else:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST, detail="Username already exists!"
            )

    @staticmethod
    def verify_new_user(username):
        conn = sqlite3.connect(SQLITE_DB)
        users = database.get_user_by_username(username, conn)
        conn.close()
        return bool(users)

    @staticmethod
    def check_user(username, password):
        conn = sqlite3.connect(SQLITE_DB)
        user = database.get_user_by_username(username, conn)
        conn.close()
        if not user:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                detail="User not found!",
            )
        if not Hasher.password_verification(password, user[2]):
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                detail="User not found!",
            )
        return user

    @staticmethod
    def get_user(user_id):
        conn = sqlite3.connect(SQLITE_DB)
        user = database.get_user(user_id, conn)
        conn.close()
        return models.User(id=user[0], username=user[1])


class Book:
    @staticmethod
    def from_db(book_id):
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
            status.HTTP_404_NOT_FOUND,
            detail="Book not found!",
        )

    @staticmethod
    def get_books(start: int, n: int):
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
        conn = sqlite3.connect(SQLITE_DB)
        book_data = database.search_book_by_title(book_name, conn)
        if not book_data:
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
        conn.close()
        return books

    @staticmethod
    def get_genres():
        conn = sqlite3.connect(SQLITE_DB)
        genres = database.get_genres(conn)
        conn.close()
        return genres

    @staticmethod
    def get_books_by_genre(genre):
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
        conn.close()
        return books[:15]


class ReadingList:
    def __init__(self, user_id):
        self.user_id = user_id
        self.books = []
        self.load()

    def load(self):
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
        conn.close()

    def get_genres(self):
        return list(set(book.genre for book in self.books if book))

    def add_book(self, book_id, status=models.StatusEnum.not_started):
        conn = sqlite3.connect(SQLITE_DB)
        database.create_reading_list(self.user_id, book_id, status, conn)
        conn.close()

    def read_books(self):
        # get the books that have been read
        conn = sqlite3.connect(SQLITE_DB)
        books = database.get_completed_books(self.user_id, conn)
        conn.close()
        return books

    def remove_book(self, book_id):
        conn = sqlite3.connect(SQLITE_DB)
        database.remove_from_reading_list(self.user_id, book_id, conn)
        conn.close()

    def change_reading_status(self, book_id, status):
        conn = sqlite3.connect(SQLITE_DB)
        database.update_reading_status(self.user_id, book_id, status, conn)
        conn.close()

    def get_recommendations(self, n: int = 15):
        conn = sqlite3.connect(SQLITE_DB)
        # for each genre in the reading list, get the books in that genre
        _books = []
        for genre in self.get_genres():
            _books.extend(database.get_books_by_genre(genre, conn))

        books = list(set(_books))
        books = [Book.from_db(book[0]) for book in books]

        # remove the books that are already in the reading list
        books = [book for book in books if book not in self.books]
        books.sort(key=lambda book: book.reads, reverse=True)
        conn.close()
        return books[:n]

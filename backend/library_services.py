import database
import hashlib
from passlib.context import CryptContext
from fastapi import HTTPException
context = CryptContext(schemes=["bcrypt"])

class Hasher:
    def password_hash(self, password):
        return context.hash(password)

    def password_verification(self, password, password_hash):
        password = self.password_hash(password)
        return context.verify(password, password_hash)

BOOK_LIST = []

def load_book_list():
    global BOOK_LIST
    BOOK_LIST = database.get_books(database.conn)

load_book_list()

class User:
    def __init__(self, username, password, confirmed_password):
        self.username = username
        if password != confirmed_password:
            raise HTTPException(status_code=400, detail="Password and confirmation don't match!")
        hasher = Hasher()
        self.password_hash = hasher.password_hash(password)
        if self.verify_new_user(username):
            raise HTTPException(status_code=400, detail="Username already exists!")
        database.create_user(username, self.password_hash, database.conn)

    @staticmethod
    def verify_new_user(username):
        users = database.get_users(database.conn)
        return any(user[1] == username for user in users)

class Book:
    def __init__(self, id, name, author, genre):
        self.id = id
        self.name = name
        self.author = author
        self.genre = genre

    @staticmethod
    def from_db(book_id):
        book_data = database.get_book(book_id, database.conn)
        if book_data:
            return Book(book_data[0], book_data[1], book_data[2], book_data[3])
        return None
    @staticmethod
    def from_book_list(book_name):
        for book in BOOK_LIST:
            if book[1] == book_name:
                return Book(book[0], book[1], book[2], book[3])
        return None
       

class ReadingList:
    def __init__(self, user_id):
        self.user_id = user_id
        self.books = []
        self.load()

    def load(self):
        self.books = [Book.from_db(entry[1]) for entry in database.get_reading_lists(self.user_id, database.conn)]

    def update(self):
        self.load()

    def get_genres(self):
        return list(set(book.genre for book in self.books if book))

    # todo: change
    def add_book(self, book_id):
        database.add_to_reading_list(self.user_id, book_id, "not_started", database.conn)
        self.update()

    def remove_book(self, book_id):
        database.remove_from_reading_list(self.user_id, book_id, database.conn)
        self.update()

    def change_reading_status(self, book_id, status):
        database.update_reading_status(self.user_id, book_id, status, database.conn)
        self.update()

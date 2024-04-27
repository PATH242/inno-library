from passlib.context import CryptContext
from fastapi import HTTPException, status
from . import models, database
from .const import SQLITE_DB
import sqlite3

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
        if(password != confirm_password):
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Password and confirmation don't match!")
                
        password_hash = Hasher.password_hash(password)

        if not User.verify_new_user(username):
            conn = sqlite3.connect(SQLITE_DB)
            database.create_user(username, password_hash, conn)
            conn.close()
        else:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Username already exists!")

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
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User not found!")
        if not Hasher.password_verification(password, user[2]):
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User not found!")
        return user
    
    @staticmethod
    def get_user(user_id):
        conn = sqlite3.connect(SQLITE_DB)
        user = database.get_user(user_id, conn)
        conn.close()
        return models.User(id = user[0], username = user[1])

class Book:
    @staticmethod
    def from_db(book_id):
        conn = sqlite3.connect(SQLITE_DB)
        book_data = database.get_book(book_id, conn)
        conn.close()
        if book_data:
            return models.Book(id = book_data[0], title = book_data[1], author = book_data[2], genre = book_data[3])
        return None
        
    @staticmethod
    def search_book(book_name):
        conn = sqlite3.connect(SQLITE_DB)
        book_data = database.get_book_by_name(book_name, conn)
        conn.close() 
        if not book_data:
            return []
        books = [models.Book(id = book[0], title = book[1], author = book[2], genre = book[3]) for book in book_data]            
        return books
       

class ReadingList:
    def __init__(self, user_id):
        self.user_id = user_id
        self.books = []
        self.load()

    def load(self):
        conn = sqlite3.connect(SQLITE_DB)
        self.books = [Book.from_db(entry[1]) for entry in database.get_reading_lists(self.user_id, conn)]
        conn.close()

    def get_genres(self):
        return list(set(book.genre for book in self.books if book))

    def add_book(self, book_id, status=models.StatusEnum.not_started):
        conn = sqlite3.connect(SQLITE_DB)
        database.create_reading_list(self.user_id, book_id, status, conn)
        conn.close()

    def read_books(self):
        # get the books that have been read
        return [book for book in self.books if book.status == models.StatusEnum.complete]

    def remove_book(self, book_id):
        conn = sqlite3.connect(SQLITE_DB)
        database.remove_from_reading_list(self.user_id, book_id, conn)
        conn.close()

    def change_reading_status(self, book_id, status):
        conn = sqlite3.connect(SQLITE_DB)
        database.update_reading_status(self.user_id, book_id, status, conn)
        conn.close()
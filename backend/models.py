"""
This module contains the pydantic schemas to represent data
"""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel


# Enum for the status of a book in a user's reading list
class StatusEnum(str, Enum):
    not_started = "not_started"
    started = "started"
    complete = "complete"


# Model to represent a book. Used for book related endpoints
class Book(BaseModel):
    id: int
    title: str
    author: str
    genre: str
    reads: int | None = None


# Model to manage pagination of books
class Books(BaseModel):
    books: list[Book]
    previous_n: int = 0
    next_n: int | None = None


# Model to accept a new user. Used for the /register endpoint
class CreateUser(BaseModel):
    username: str
    password: str
    confirm_password: str


# Model to accept a user login. Used for the /login endpoint
class LoginUser(BaseModel):
    username: str
    password: str


# Model to represent a user. Used for /me and internal user representation
class User(BaseModel):
    id: int
    username: str
    reads: int | None = None
    total_books: int | None = None


# Model to represent a user and JWT token. Used for the /login endpoint
class Token(BaseModel):
    id: int
    username: str
    token: str


# Model for updating a user's library. Used for POST and PUT methods
class EditReadingList(BaseModel):
    book_id: int
    status: StatusEnum | None = None


# Model to represent a book in a user's reading list. Used for /reads endpoint
class MyRead(Book):
    status: StatusEnum
    updated_at: datetime

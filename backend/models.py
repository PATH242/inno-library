from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class StatusEnum(str, Enum):
    not_started = "not_started"
    started = "started"
    complete = "complete"


class Book(BaseModel):
    id: int
    title: str
    author: str
    genre: str
    reads: int | None = None


class Books(BaseModel):
    books: list[Book]
    previous_n: int = 0
    next_n: int | None = None


class CreateUser(BaseModel):
    username: str
    password: str
    confirm_password: str


class LoginUser(BaseModel):
    username: str
    password: str


class User(BaseModel):
    id: int
    username: str
    reads: int | None = None
    total_books: int | None = None


class Token(BaseModel):
    id: int
    username: str
    token: str


class EditReadingList(BaseModel):
    book_id: int
    status: StatusEnum | None = None


class MyRead(BaseModel):
    book_id: int
    title: str
    status: StatusEnum
    updated_at: datetime

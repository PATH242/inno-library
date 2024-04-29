"""
This module contains the FastAPI router that defines the API endpoints.
"""

from fastapi import APIRouter, Depends

from . import models, security, service

router = APIRouter(prefix="/api")


# Auth routes
@router.post("/register", tags=["auth"])
def register(user: models.CreateUser) -> str:
    """
    Register a new user.
    """

    service.User.create_user(
        user.username,
        user.password,
        user.confirm_password,
    )
    return "User created successfully!"


@router.post("/login", tags=["auth"])
def login(user: models.LoginUser) -> models.Token:
    """
    Login a user and return a JWT token.
    """

    login_user = service.User.check_user(user.username, user.password)
    token = security.create_jwt_token({"user_id": login_user[0]})
    return models.Token(id=login_user[0], username=login_user[1], token=token)


@router.get("/me", tags=["auth"])
def me(user_id: int = Depends(security.get_user)) -> models.User:
    """
    For a logged in user, returns thier details, total number of books in the
    library and the number of books read.
    """

    reading_list = service.ReadingList(user_id)
    user = service.User.get_user(user_id)
    user.total_books = len(reading_list.books)
    user.reads = len(reading_list.read_books())
    return user


# Book routes
@router.get("/books", tags=["books"])
def get_all_books(start: int = 0, n: int = 15) -> models.Books:
    """
    Returns the available books in the database (paginated).
    """

    return service.Book.get_books(start, n)


@router.get("/search", tags=["books"])
def search_book(q: str) -> list[models.Book]:
    """
    Search for a book by title (case-insensitive)
    """

    return service.Book.search_book(q)


@router.get("/genre", tags=["books"])
def get_genres() -> list[str]:
    """
    Returns the available genres in the database.
    """

    return service.Book.get_genres()


@router.get("/books/genre", tags=["books"])
def get_books_by_genre(genre: str) -> list[models.Book]:
    """
    Returns the books from a specific genre.
    """

    return service.Book.get_books_by_genre(genre)


# Reading list routes
@router.get("/reads", tags=["library"])
def get_reading_list(
    user_id: int = Depends(security.get_user),
) -> list[models.MyRead]:
    """
    Returns the reading list of the user.
    """

    reading_list = service.ReadingList(user_id)
    return reading_list.books


@router.post("/reads", tags=["library"])
def add_to_reading_list(
    book_id: int, user_id: int = Depends(security.get_user)
) -> models.Book:
    """
    Add a book to the user's reading list.
    Throws an error if the book is already in the reading list.
    """
    reading_list = service.ReadingList(user_id)
    reading_list.add_book(book_id)
    return service.Book.from_db(book_id)


@router.put("/reads", tags=["library"])
def change_reading_status(
    entry: models.EditReadingList, user_id: int = Depends(security.get_user)
) -> models.Book:
    """
    Update the reading status of a book in the user's reading list.
    Change the status to 'not_started', 'started' or 'complete'.
    Does not do anything if the book is not in the reading list.
    Does not do anything if the status is the same as the current status.
    """
    reading_list = service.ReadingList(user_id)
    reading_list.change_reading_status(entry.book_id, entry.status)
    return service.Book.from_db(entry.book_id)


@router.delete("/reads", tags=["library"])
def remove_from_reading_list(
    book_id: int, user_id: int = Depends(security.get_user)
) -> str:
    """
    Remove a book from the user's reading list.
    Does not do anything if the book is not in the reading list.
    """
    reading_list = service.ReadingList(user_id)
    reading_list.remove_book(book_id)
    return "Book removed from reading list!"


@router.get("/recommend", tags=["library"])
def get_recommendations(
    n: int = 15, user_id: int = Depends(security.get_user)
) -> list[models.Book]:
    """
    Get book recommendations for the user based on the current reading list.
    Returns empty list if the reading list is empty.
    """

    reading_list = service.ReadingList(user_id)
    return reading_list.get_recommendations(n)

from fastapi import APIRouter, Depends

from . import models, security, service

router = APIRouter(prefix="/api")


# Auth routes
@router.post("/register", tags=["auth"])
def register(user: models.CreateUser) -> str:
    service.User.create_user(
        user.username,
        user.password,
        user.confirm_password,
    )
    return "User created successfully!"


@router.post("/login", tags=["auth"])
def login(user: models.LoginUser) -> models.Token:
    login_user = service.User.check_user(user.username, user.password)
    token = security.create_jwt_token({"user_id": login_user[0]})
    return models.Token(id=login_user[0], username=login_user[1], token=token)


@router.get("/me", tags=["auth"])
def me(user_id: int = Depends(security.get_user)) -> models.User:
    reading_list = service.ReadingList(user_id)
    user = service.User.get_user(user_id)
    user.total_books = len(reading_list.books)
    user.reads = len(reading_list.read_books())
    return user


# Book routes
@router.get("/books", tags=["books"])
def get_all_books(start: int = 0, n: int = 15) -> models.Books:
    return service.Book.get_books(start, n)


@router.get("/search", tags=["books"])
def search_book(q: str) -> list[models.Book]:
    return service.Book.search_book(q)


@router.get("/genre", tags=["books"])
def get_genres() -> list[str]:
    return service.Book.get_genres()


@router.get("/books/genre", tags=["books"])
def get_books_by_genre(genre: str) -> list[models.Book]:
    return service.Book.get_books_by_genre(genre)


# Reading list routes
@router.get("/reads", tags=["library"])
def get_reading_list(
    user_id: int = Depends(security.get_user),
) -> list[models.Book]:
    reading_list = service.ReadingList(user_id)
    return reading_list.books


@router.post("/reads", tags=["library"])
def add_to_reading_list(
    book_id: int, user_id: int = Depends(security.get_user)
) -> models.Book:
    reading_list = service.ReadingList(user_id)
    reading_list.add_book(book_id)
    return service.Book.from_db(book_id)


@router.put("/reads", tags=["library"])
def change_reading_status(
    entry: models.EditReadingList, user_id: int = Depends(security.get_user)
) -> models.Book:
    reading_list = service.ReadingList(user_id)
    reading_list.change_reading_status(entry.book_id, entry.status)
    return service.Book.from_db(entry.book_id)


@router.delete("/reads", tags=["library"])
def remove_from_reading_list(
    book_id: int, user_id: int = Depends(security.get_user)
) -> str:
    reading_list = service.ReadingList(user_id)
    reading_list.remove_book(book_id)
    return "Book removed from reading list!"


@router.get("/recommend", tags=["library"])
def get_recommendations(
    n: int = 15, user_id: int = Depends(security.get_user)
) -> list[models.Book]:
    reading_list = service.ReadingList(user_id)
    return reading_list.get_recommendations(n)

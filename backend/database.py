"""
This module contains the SQL queries and related functions for the application.
"""

import json
import os
import sqlite3


def create_tables(conn: sqlite3.Connection):
    """
    Crates the tables in the database and populates the books table with
    the data from the books.json file.
    """
    # {
    #     "title": "Book name",
    #     "author": "author",
    #     "genre": "genre",
    # }
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            genre TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    )

    # {
    #     "username": "admin",
    #     "password_hash": "pbkdf2:sha256:150000$1Z6Z6Z6Z$e",
    #     "name": "Name"
    # }

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    )

    conn.commit()

    # {
    #     "book": 123,
    #     "user": 123,
    #     "reading_status": "not_started",
    # }
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS reading_list (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book INTEGER NOT NULL,
            user INTEGER NOT NULL,
            reading_status TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (book) REFERENCES books (id),
            FOREIGN KEY (user) REFERENCES users (id)
        )
    """
    )
    conn.commit()

    # Check if there is any book exists in the database
    # Populates the table only if there are no books in the database
    cursor = conn.execute(
        """
        SELECT * FROM books
    """
    )
    books = cursor.fetchall()
    if not books:
        with open(f"{os.path.dirname(__file__)}/data/books.json", "r") as f:
            books = json.load(f)
            for book in books:
                create_book(book["title"], book["author"], book["genre"], conn)
    conn.commit()


def drop_tables(conn: sqlite3.Connection):
    """
    Drops the tables from the database. Not used in the application.
    """
    conn.execute(
        """
        DROP TABLE IF EXISTS books
    """
    )
    conn.execute(
        """
        DROP TABLE IF EXISTS users
    """
    )
    conn.execute(
        """
        DROP TABLE IF EXISTS reading_list
    """
    )
    conn.commit()


def create_book(title, author, genre, conn: sqlite3.Connection):
    """
    Creates a new book in the database.
    """
    conn.execute(
        """
        INSERT INTO books (title, author, genre)
        VALUES (?, ?, ?)
    """,
        (title, author, genre),
    )
    conn.commit()


def get_books(start, n, conn: sqlite3.Connection):
    """
    Given an offset and a limit, returns a list of books.
    """

    cursor = conn.execute(
        """
        SELECT * FROM books LIMIT ? OFFSET ?
    """,
        (n, start),
    )
    books = cursor.fetchall()
    return books


def get_genres(conn: sqlite3.Connection):
    """
    Returns the list of all genres in the database.
    """

    cursor = conn.execute(
        """
        SELECT DISTINCT genre FROM books
    """
    )
    genres = cursor.fetchall()
    return [genre[0] for genre in genres]


def get_book(book_id, conn: sqlite3.Connection):
    """
    Returns the book with the given ID.
    """

    cursor = conn.execute(
        """
        SELECT * FROM books WHERE id = ?
    """,
        (book_id,),
    )
    book = cursor.fetchone()
    return book


def get_book_count(conn: sqlite3.Connection):
    """
    Returns the total number of books in the database.
    """
    cursor = conn.execute(
        """
        SELECT COUNT(*) FROM books
    """
    )
    count = cursor.fetchone()
    return count[0]


def search_book_by_title(title, conn: sqlite3.Connection):
    """
    Given a title, returns a list of books that contain the title (case insensitive).
    """
    cursor = conn.execute(
        """
        SELECT * FROM books WHERE title LIKE ?
    """,
        (f"%{title}%",),
    )
    books = cursor.fetchall()
    return books


def get_books_by_genre(genre, conn: sqlite3.Connection):
    """
    Given a genre, returns a list of books that belong to the genre.
    """
    cursor = conn.execute(
        """
        SELECT * FROM books WHERE genre = ?
    """,
        (genre,),
    )
    books = cursor.fetchall()
    return books


def update_book(book_id, title, author, genre, conn: sqlite3.Connection):
    """
    Updates the book with the given ID. Not used in the application.
    """

    conn.execute(
        """
        UPDATE books
        SET title = ?, author = ?, genre = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """,
        (title, author, genre, book_id),
    )
    conn.commit()


def delete_book(book_id, conn: sqlite3.Connection):
    """
    Deletes the book with the given ID. Not used in the application.
    """

    conn.execute(
        """
        DELETE FROM books WHERE id = ?
    """,
        (book_id,),
    )
    conn.execute(
        """
        DELETE FROM reading_list WHERE book = ?
    """,
        (book_id,),
    )
    conn.commit()


def create_user(username, password_hash, conn: sqlite3.Connection):
    """
    Creates a new user in the database.
    """

    conn.execute(
        """
        INSERT INTO users (username, password_hash)
        VALUES (?, ?)
    """,
        (username, password_hash),
    )
    conn.commit()


def get_users(conn: sqlite3.Connection):
    """
    Returns the list of all users in the database. Not used in the application.
    """

    cursor = conn.execute(
        """
        SELECT * FROM users
    """
    )
    users = cursor.fetchall()
    return users


def get_user(user_id, conn: sqlite3.Connection):
    """
    Returns the user with the given ID.
    """

    cursor = conn.execute(
        """
        SELECT * FROM users WHERE id = ?
    """,
        (user_id,),
    )
    user = cursor.fetchone()
    return user


def get_user_by_username(username, conn: sqlite3.Connection):
    """
    Returns the user with the given username.
    """

    cursor = conn.execute(
        """
        SELECT * FROM users WHERE username = ?
    """,
        (username,),
    )
    user = cursor.fetchone()
    return user


def update_user(user_id, username, password_hash, conn: sqlite3.Connection):
    """
    Updates the user with the given ID. Not used in the application.
    """

    conn.execute(
        """
        UPDATE users
        SET username = ?, password_hash = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """,
        (username, password_hash, user_id),
    )
    conn.commit()


def delete_user(user_id, conn: sqlite3.Connection):
    """
    Deletes the user with the given ID. Not used in the application.
    """

    conn.execute(
        """
        DELETE FROM users WHERE id = ?
    """,
        (user_id,),
    )
    conn.execute(
        """
        DELETE FROM reading_list WHERE user = ?
    """,
        (user_id,),
    )
    conn.commit()


def create_reading_list(
    user_id,
    book_id,
    reading_status,
    conn: sqlite3.Connection,
):
    """
    Given a user_id and a book_id, adds the book to user's library.
    """

    conn.execute(
        """
        INSERT INTO reading_list (book, user, reading_status)
        VALUES (?, ?, ?)
    """,
        (book_id, user_id, reading_status),
    )
    conn.commit()


def get_reading_lists(user_id, conn: sqlite3.Connection):
    """
    Given a user_id, returns the list of books in the user's library.
    """

    cursor = conn.execute(
        """
        SELECT * FROM reading_list WHERE user = ?
    """,
        (user_id,),
    )
    reading_lists = cursor.fetchall()
    return reading_lists


def get_book_in_reading_list(user_id, book_id, conn: sqlite3.Connection):
    """
    Given a user_id and a book_id, returns the book in user's library.
    """

    cursor = conn.execute(
        """
        SELECT * FROM reading_list WHERE user = ? AND book = ?
    """,
        (user_id, book_id),
    )
    book = cursor.fetchone()
    return book


def get_completed_books(user_id, conn: sqlite3.Connection):
    """
    Given a user_id, returns the list of books that the user has completed.
    """

    cursor = conn.execute(
        """
        SELECT * FROM reading_list WHERE user = ?
        AND reading_status = 'complete'
    """,
        (user_id,),
    )
    completed_books = cursor.fetchall()
    return completed_books


def get_readers(book_id, conn: sqlite3.Connection):
    """
    Given a book_id, returns the list of users who have added the book to their library.
    """

    cursor = conn.execute(
        """
        SELECT * FROM reading_list WHERE book = ?
    """,
        (book_id,),
    )
    readers = cursor.fetchall()
    return readers


def get_book_read_count(book_id, conn: sqlite3.Connection):
    """
    Given a book_id, returns the number of users who have completed the book.
    """

    cursor = conn.execute(
        """
        SELECT COUNT(*) FROM reading_list WHERE book = ?
        AND reading_status = 'complete'
    """,
        (book_id,),
    )
    count = cursor.fetchone()
    return count[0]


def remove_from_reading_list(user_id, book_id, conn: sqlite3.Connection):
    """
    Given a user_id and a book_id, removes the book from user's library.
    """

    conn.execute(
        """
        DELETE FROM reading_list WHERE book = ? AND user = ?
    """,
        (book_id, user_id),
    )
    conn.commit()


def update_reading_status(
    user_id,
    book_id,
    reading_status,
    conn: sqlite3.Connection,
):
    """
    Given a user_id, a book_id, and a reading_status, updates the reading status
    of the book in user's library.
    """

    conn.execute(
        """
        UPDATE reading_list
        SET reading_status = ?, updated_at = CURRENT_TIMESTAMP
        WHERE book = ? AND user = ?
    """,
        (reading_status, book_id, user_id),
    )
    conn.commit()

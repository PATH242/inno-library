"""
This module contains the SQL queries and related functions for the application.
"""

import json
import logging
import os
import sqlite3


def create_tables(conn: sqlite3.Connection):
    """
    Crates the tables in the database and populates the books table with
    the data from the books.json file.
    """

    logging.info("Creating tables")

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
    logging.info("Tables created")


def drop_tables(conn: sqlite3.Connection):
    """
    Drops the tables from the database. Not used in the application.
    """
    logging.info("Dropping tables")
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
    logging.info("Tables dropped")


def create_book(title, author, genre, conn: sqlite3.Connection):
    """
    Creates a new book in the database.
    """
    logging.info(f"Database: Creating book: {title}")

    conn.execute(
        """
        INSERT INTO books (title, author, genre)
        VALUES (?, ?, ?)
    """,
        (title, author, genre),
    )
    conn.commit()
    logging.info(f"Database: Book created: {title}")


def get_books(start, n, conn: sqlite3.Connection):
    """
    Given an offset and a limit, returns a list of books.
    """
    logging.info(f"Database: Getting books: {start} - {n}")

    cursor = conn.execute(
        """
        SELECT * FROM books LIMIT ? OFFSET ?
    """,
        (n, start),
    )
    books = cursor.fetchall()
    logging.info(f"Database: {len(books)} books found")
    return books


def get_genres(conn: sqlite3.Connection):
    """
    Returns the list of all genres in the database.
    """
    logging.info("Getting genres")

    cursor = conn.execute(
        """
        SELECT DISTINCT genre FROM books
    """
    )
    genres = cursor.fetchall()
    logging.info(f"Database: {len(genres)} genres found")
    return [genre[0] for genre in genres]


def get_book(book_id, conn: sqlite3.Connection):
    """
    Returns the book with the given ID.
    """
    logging.info(f"Database: Getting book: {book_id}")

    cursor = conn.execute(
        """
        SELECT * FROM books WHERE id = ?
    """,
        (book_id,),
    )
    book = cursor.fetchone()
    logging.info(f"Database: Book found: {book[1]}")
    return book


def get_book_count(conn: sqlite3.Connection):
    """
    Returns the total number of books in the database.
    """
    logging.info("Getting book count")
    cursor = conn.execute(
        """
        SELECT COUNT(*) FROM books
    """
    )
    count = cursor.fetchone()
    logging.info(f"Database: {count[0]} books found")
    return count[0]


def search_book_by_title(title, conn: sqlite3.Connection):
    """
    Given a title, returns a list of books that contain the title (case insensitive).
    """
    logging.info(f"Database: Searching book: {title}")
    cursor = conn.execute(
        """
        SELECT * FROM books WHERE title LIKE ?
    """,
        (f"%{title}%",),
    )
    books = cursor.fetchall()
    logging.info(f"Database: {len(books)} books found")
    return books


def get_books_by_genre(genre, conn: sqlite3.Connection):
    """
    Given a genre, returns a list of books that belong to the genre.
    """
    logging.info(f"Database: Getting books by genre: {genre}")
    cursor = conn.execute(
        """
        SELECT * FROM books WHERE genre = ?
    """,
        (genre,),
    )
    books = cursor.fetchall()
    logging.info(f"Database: {len(books)} books found")
    return books


def update_book(book_id, title, author, genre, conn: sqlite3.Connection):
    """
    Updates the book with the given ID. Not used in the application.
    """
    logging.info(f"Database: Updating book: {book_id}")

    conn.execute(
        """
        UPDATE books
        SET title = ?, author = ?, genre = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """,
        (title, author, genre, book_id),
    )
    conn.commit()
    logging.info(f"Database: Book updated: {title}")


def delete_book(book_id, conn: sqlite3.Connection):
    """
    Deletes the book with the given ID. Not used in the application.
    """
    logging.info(f"Database: Deleting book: {book_id}")

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
    logging.info(f"Database: Book deleted: {book_id}")


def create_user(username, password_hash, conn: sqlite3.Connection):
    """
    Creates a new user in the database.
    """
    logging.info(f"Database: Creating user: {username}")

    conn.execute(
        """
        INSERT INTO users (username, password_hash)
        VALUES (?, ?)
    """,
        (username, password_hash),
    )
    conn.commit()
    logging.info(f"Database: User created: {username}")


def get_users(conn: sqlite3.Connection):
    """
    Returns the list of all users in the database. Not used in the application.
    """
    logging.info("Getting users")

    cursor = conn.execute(
        """
        SELECT * FROM users
    """
    )
    users = cursor.fetchall()
    logging.info(f"Database: {len(users)} users found")
    return users


def get_user(user_id, conn: sqlite3.Connection):
    """
    Returns the user with the given ID.
    """
    logging.info(f"Database: Getting user: {user_id}")

    cursor = conn.execute(
        """
        SELECT * FROM users WHERE id = ?
    """,
        (user_id,),
    )
    user = cursor.fetchone()
    if user:
        logging.info(f"Database: User found: {user[1]}")
    return user


def get_user_by_username(username, conn: sqlite3.Connection):
    """
    Returns the user with the given username.
    """
    logging.info(f"Database: Getting user: {username}")

    cursor = conn.execute(
        """
        SELECT * FROM users WHERE username = ?
    """,
        (username,),
    )
    user = cursor.fetchone()
    if user:
        logging.info(f"Database: User found: {user[1]}")
    return user


def update_user(user_id, username, password_hash, conn: sqlite3.Connection):
    """
    Updates the user with the given ID. Not used in the application.
    """
    logging.info(f"Database: Updating user: {user_id}")

    conn.execute(
        """
        UPDATE users
        SET username = ?, password_hash = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """,
        (username, password_hash, user_id),
    )
    conn.commit()
    logging.info(f"Database: User updated: {username}")


def delete_user(user_id, conn: sqlite3.Connection):
    """
    Deletes the user with the given ID. Not used in the application.
    """
    logging.info(f"Database: Deleting user: {user_id}")

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
    logging.info(f"Database: User deleted: {user_id}")


def create_reading_list(
    user_id,
    book_id,
    reading_status,
    conn: sqlite3.Connection,
):
    """
    Given a user_id and a book_id, adds the book to user's library.
    """
    logging.info(
        f"Database: Adding book to reading list: {book_id} for user: {user_id}"
    )

    conn.execute(
        """
        INSERT INTO reading_list (book, user, reading_status)
        VALUES (?, ?, ?)
    """,
        (book_id, user_id, reading_status),
    )
    conn.commit()
    logging.info(f"Database: Book added to reading list: {book_id} for user: {user_id}")


def get_reading_lists(user_id, conn: sqlite3.Connection):
    """
    Given a user_id, returns the list of books in the user's library.
    """
    logging.info(f"Database: Getting reading list for user: {user_id}")

    cursor = conn.execute(
        """
        SELECT * FROM reading_list WHERE user = ?
    """,
        (user_id,),
    )
    reading_lists = cursor.fetchall()
    logging.info(f"Database: {len(reading_lists)} books found")
    return reading_lists


def get_book_in_reading_list(user_id, book_id, conn: sqlite3.Connection):
    """
    Given a user_id and a book_id, returns the book in user's library.
    """
    logging.info(
        f"Database: Getting book: {book_id} in reading list for user: {user_id}"
    )

    cursor = conn.execute(
        """
        SELECT * FROM reading_list WHERE user = ? AND book = ?
    """,
        (user_id, book_id),
    )
    book = cursor.fetchone()
    if book:
        logging.info(f"Database: Book found: {book[1]}")
    return book


def get_completed_books(user_id, conn: sqlite3.Connection):
    """
    Given a user_id, returns the list of books that the user has completed.
    """
    logging.info(f"Database: Getting completed books for user: {user_id}")

    cursor = conn.execute(
        """
        SELECT * FROM reading_list WHERE user = ?
        AND reading_status = 'complete'
    """,
        (user_id,),
    )
    completed_books = cursor.fetchall()
    logging.info(f"Database: {len(completed_books)} books found")
    return completed_books


def get_readers(book_id, conn: sqlite3.Connection):
    """
    Given a book_id, returns the list of users who have added the book to their library.
    """
    logging.info(f"Database: Getting readers for book: {book_id}")

    cursor = conn.execute(
        """
        SELECT * FROM reading_list WHERE book = ?
    """,
        (book_id,),
    )
    readers = cursor.fetchall()
    logging.info(f"Database: {len(readers)} readers found")
    return readers


def get_book_read_count(book_id, conn: sqlite3.Connection):
    """
    Given a book_id, returns the number of users who have completed the book.
    """
    logging.info(f"Database: Getting read count for book: {book_id}")

    cursor = conn.execute(
        """
        SELECT COUNT(*) FROM reading_list WHERE book = ?
        AND reading_status = 'complete'
    """,
        (book_id,),
    )
    count = cursor.fetchone()
    logging.info(f"Database: {count[0]} readers found")
    return count[0]


def remove_from_reading_list(user_id, book_id, conn: sqlite3.Connection):
    """
    Given a user_id and a book_id, removes the book from user's library.
    """
    logging.info(
        f"Database: Removing book: {book_id} from reading list for user: {user_id}"
    )

    conn.execute(
        """
        DELETE FROM reading_list WHERE book = ? AND user = ?
    """,
        (book_id, user_id),
    )
    conn.commit()
    logging.info(
        f"Database: Book removed: {book_id} from reading list for user: {user_id}"
    )


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
    logging.info(
        f"Database: Updating reading status: {reading_status} for book:"
        f"{book_id} in reading list for user: {user_id}"
    )

    conn.execute(
        """
        UPDATE reading_list
        SET reading_status = ?, updated_at = CURRENT_TIMESTAMP
        WHERE book = ? AND user = ?
    """,
        (reading_status, book_id, user_id),
    )
    conn.commit()
    logging.info(
        f"Database: Reading status updated: {reading_status} for book:"
        f"{book_id} in reading list for user: {user_id}"
    )

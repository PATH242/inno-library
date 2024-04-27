import sqlite3

def create_tables(conn: sqlite3.Connection):
    # {
    #     "title": "Book name", 
    #     "author": "author",
    #     "genre": "genre",
    # }
    conn.execute("""
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            genre TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # {
    #     "username": "admin",
    #     "password_hash": "pbkdf2:sha256:150000$1Z6Z6Z6Z$e",
    #     "name": "Name"
    # }

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()

    # {
    #     "book": 123,
    #     "user": 123,
    #     "reading_status": "not_started",
    # }
    conn.execute("""
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
    """)
    conn.commit()

def create_book(title, author, genre, conn: sqlite3.Connection):
    conn.execute("""
        INSERT INTO books (title, author, genre)
        VALUES (?, ?, ?)
    """, (title, author, genre))
    conn.commit()

def get_books(conn: sqlite3.Connection):
    cursor = conn.execute("""
        SELECT * FROM books
    """)
    books = cursor.fetchall()
    return books

def get_book(book_id, conn: sqlite3.Connection):
    cursor = conn.execute("""
        SELECT * FROM books WHERE id = ?
    """, (book_id,))
    book = cursor.fetchone()
    return book

def search_book_by_title(title, conn: sqlite3.Connection):
    cursor = conn.execute("""
        SELECT * FROM books WHERE title LIKE ?
    """, (f"%{title}%",))

def update_book(book_id, title, author, genre, conn: sqlite3.Connection):
    conn.execute("""
        UPDATE books
        SET title = ?, author = ?, genre = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (title, author, genre, book_id))
    conn.commit()

def delete_book(book_id, conn: sqlite3.Connection):
    conn.execute("""
        DELETE FROM books WHERE id = ?
    """, (book_id,))
    conn.execute("""
        DELETE FROM reading_list WHERE book = ?
    """, (book_id,))
    conn.commit()

def create_user(username, password_hash, conn: sqlite3.Connection):
    conn.execute("""
        INSERT INTO users (username, password_hash)
        VALUES (?, ?)
    """, (username, password_hash))
    conn.commit()

def get_users(conn: sqlite3.Connection):
    cursor = conn.execute("""
        SELECT * FROM users
    """)
    users = cursor.fetchall()
    return users

def get_user(user_id, conn: sqlite3.Connection):
    cursor = conn.execute("""
        SELECT * FROM users WHERE id = ?
    """, (user_id,))
    user = cursor.fetchone()
    return user

def get_user_by_username(username, conn: sqlite3.Connection):
    cursor = conn.execute("""
        SELECT * FROM users WHERE username = ?
    """, (username,))
    user = cursor.fetchone()
    return user

def update_user(user_id, username, password_hash, name, conn: sqlite3.Connection):
    conn.execute("""
        UPDATE users
        SET username = ?, password_hash = ?, name = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (username, password_hash, name, user_id))
    conn.commit()

def delete_user(user_id, conn: sqlite3.Connection):
    conn.execute("""
        DELETE FROM users WHERE id = ?
    """, (user_id,))
    conn.execute("""
        DELETE FROM reading_list WHERE user = ?
    """, (user_id,))
    conn.commit()

def create_reading_list(user_id, book_id, reading_status, conn: sqlite3.Connection):
    conn.execute("""
        INSERT INTO reading_list (book, user, reading_status)
        VALUES (?, ?, ?)
    """, (book_id, user_id, reading_status))
    conn.commit()

def get_reading_lists(user_id, conn: sqlite3.Connection):
    cursor = conn.execute("""
        SELECT * FROM reading_list WHERE user = ?
    """, (user_id,))
    reading_lists = cursor.fetchall()
    return reading_lists

def get_readers(book_id, conn: sqlite3.Connection):
    cursor = conn.execute("""
        SELECT * FROM reading_list WHERE book = ?
    """, (book_id,))
    readers = cursor.fetchall()
    return readers

def remove_from_reading_list(user_id, book_id, conn: sqlite3.Connection):
    conn.execute("""
        DELETE FROM reading_list WHERE book = ? AND user = ?
    """, (book_id, user_id))
    conn.commit()

def update_reading_status(user_id, book_id, reading_status, conn: sqlite3.Connection):
    conn.execute("""
        UPDATE reading_list
        SET reading_status = ?, updated_at = CURRENT_TIMESTAMP
        WHERE book = ? AND user = ?
    """, (reading_status, book_id, user_id))
    conn.commit()

import unittest
from unittest.mock import MagicMock
import sqlite3
import backend.database as db

class TestDatabaseBookFunctions(unittest.TestCase):

    def setUp(self):
        # Set up a mocked sqlite3 connection and cursor
        self.conn = MagicMock()
        self.cursor = MagicMock()
        self.conn.execute.return_value = self.cursor
        self.cursor.fetchall.return_value = [
            (1, 'Sample Book', 'Author A', 'Genre A'),
            (2, 'Another Book', 'Author B', 'Genre B')
        ]
        self.cursor.fetchone.return_value = (1, 'Sample Book', 'Author A', 'Genre A')

    def test_create_book(self):
        db.create_book('Test Book', 'Test Author', 'Test Genre', self.conn)
        self.conn.execute.assert_called_with(
        """
        INSERT INTO books (title, author, genre)
        VALUES (?, ?, ?)\n    """,
        ('Test Book', 'Test Author', 'Test Genre')
        )
        self.conn.commit.assert_called_once()

    def test_get_books(self):
        books = db.get_books(0, 2, self.conn)
        self.conn.execute.assert_called_with("""
        SELECT * FROM books LIMIT ? OFFSET ?
    """, (2, 0))
        self.assertEqual(books, [(1, 'Sample Book', 'Author A', 'Genre A'), (2, 'Another Book', 'Author B', 'Genre B')])
    
    def test_get_genres(self):
        self.cursor.fetchall.return_value = [('Fiction',), ('Non-Fiction',)]
        genres = db.get_genres(self.conn)
        self.conn.execute.assert_called_with("""
        SELECT DISTINCT genre FROM books
    """)
        self.assertEqual(genres, ['Fiction', 'Non-Fiction'])

    def test_get_book(self):
        book_id = 1
        book = db.get_book(book_id, self.conn)
        self.conn.execute.assert_called_with("""
        SELECT * FROM books WHERE id = ?
    """, (book_id,))
        self.assertEqual(book, (1, 'Sample Book', 'Author A', 'Genre A'))
        
    def test_get_book_count(self):
        self.cursor.fetchone.return_value = (5,)
        count = db.get_book_count(self.conn)
        self.conn.execute.assert_called_with("""
        SELECT COUNT(*) FROM books
    """)
        self.assertEqual(count, 5)
    def test_search_book_by_title(self):
        search_title = 'Sample'
        searched_books = db.search_book_by_title(search_title, self.conn)
        self.conn.execute.assert_called_with("""
        SELECT * FROM books WHERE title LIKE ?
    """, ("%Sample%",))
        self.assertEqual(searched_books, [(1, 'Sample Book', 'Author A', 'Genre A'), (2, 'Another Book', 'Author B', 'Genre B')])

    def test_get_books_by_genre(self):
        genre = 'Fiction'
        books_by_genre = db.get_books_by_genre(genre, self.conn)
        self.conn.execute.assert_called_with("""
        SELECT * FROM books WHERE genre = ?
    """, (genre,))
        self.assertEqual(books_by_genre, [(1, 'Sample Book', 'Author A', 'Genre A'), (2, 'Another Book', 'Author B', 'Genre B')])

    def test_update_book(self):
        db.update_book(1, 'Updated Book', 'Updated Author', 'Updated Genre', self.conn)
        self.conn.execute.assert_called_with("""
        UPDATE books
        SET title = ?, author = ?, genre = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, ('Updated Book', 'Updated Author', 'Updated Genre', 1)
        )
        self.conn.commit.assert_called_once()

    def test_delete_book(self):
        db.delete_book(1, self.conn)
        calls = [
            (("""
        DELETE FROM books WHERE id = ?
    """, (1,)),),
            (("""
        DELETE FROM reading_list WHERE book = ?
    """, (1,)),)
        ]
        self.conn.execute.assert_has_calls(calls, any_order=True)
        self.conn.commit.assert_called_once()

class TestDatabaseUserFunctions(unittest.TestCase):
    def setUp(self):
        # Set up a mocked sqlite3 connection and cursor
        self.conn = MagicMock()
        self.cursor = MagicMock()
        self.conn.execute.return_value = self.cursor
        self.cursor.fetchall.return_value = [
            (1, 'user1', 'hash1'),
            (2, 'user2', 'hash2')
        ]
        self.cursor.fetchone.return_value = (1, 'user1', 'hash1')

    def test_create_user(self):
            db.create_user('newuser', 'newhash', self.conn)
            self.conn.execute.assert_called_with("""
        INSERT INTO users (username, password_hash)
        VALUES (?, ?)
    """, ('newuser', 'newhash'))
            self.conn.commit.assert_called_once()

    def test_get_users(self):
        users = db.get_users(self.conn)
        self.conn.execute.assert_called_with("""
        SELECT * FROM users
    """)
        self.assertEqual(users, [(1, 'user1', 'hash1'), (2, 'user2', 'hash2')])

    def test_get_user(self):
        user_id = 1
        user = db.get_user(user_id, self.conn)
        self.conn.execute.assert_called_with("""
        SELECT * FROM users WHERE id = ?
    """, (user_id,))
        self.assertEqual(user, (1, 'user1', 'hash1'))
    
    def test_get_user_by_username(self):
        username = 'user1'
        user = db.get_user_by_username(username, self.conn)
        
        self.conn.execute.assert_called_with("""
        SELECT * FROM users WHERE username = ?
    """, (username,))
        
        self.assertEqual(user, (1, 'user1', 'hash1'))

    def test_update_user(self):
        db.update_user(1, 'updateduser', 'updatedhash',  self.conn)
        self.conn.execute.assert_called_with("""
        UPDATE users
        SET username = ?, password_hash = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, ('updateduser', 'updatedhash', 1))
        self.conn.commit.assert_called_once()

    def test_delete_user(self):
        db.delete_user(1, self.conn)
        calls = [
            (("""
        DELETE FROM users WHERE id = ?
    """, (1,)),),
            (("""
        DELETE FROM reading_list WHERE user = ?
    """, (1,)),)
        ]
        self.conn.execute.assert_has_calls(calls, any_order=True)
        self.conn.commit.assert_called_once()

class TestDatabaseReadingListFunctions(unittest.TestCase):

    def setUp(self):
        # Set up a mocked sqlite3 connection and cursor
        self.conn = MagicMock()
        self.cursor = MagicMock()
        self.conn.execute.return_value = self.cursor
        self.cursor.fetchall.return_value = [
            (1, 1, 1, 'not_started'),
            (2, 1, 2, 'in_progress')
        ]
        self.cursor.fetchone.return_value = (1, 1, 1, 'not_started')

    def test_create_reading_list(self):
        db.create_reading_list(1, 1, 'not_started', self.conn)
        self.conn.execute.assert_called_with("""
        INSERT INTO reading_list (book, user, reading_status)
        VALUES (?, ?, ?)
    """, (1, 1, 'not_started'))
        self.conn.commit.assert_called_once()

    def test_get_reading_lists(self):
        reading_lists = db.get_reading_lists(1, self.conn)
        self.conn.execute.assert_called_with("""
        SELECT * FROM reading_list WHERE user = ?
    """, (1,))
        self.assertEqual(reading_lists, [(1, 1, 1, 'not_started'), (2, 1, 2, 'in_progress')])

    def test_get_completed_books(self):
        # Change the return value for this specific test
        self.cursor.fetchall.return_value = [
            (1, 1, 1, 'complete'),
            (2, 1, 2, 'complete')
        ]
        completed_books = db.get_completed_books(1, self.conn)
        self.conn.execute.assert_called_with("""
        SELECT * FROM reading_list WHERE user = ? AND reading_status = 'complete'
    """,  (1,))
        self.assertEqual(completed_books, [(1, 1, 1, 'complete'), (2, 1, 2, 'complete')])

    def test_get_readers(self):
        readers = db.get_readers(1, self.conn)
        self.conn.execute.assert_called_with("""
        SELECT * FROM reading_list WHERE book = ?
    """, (1,))
        self.assertEqual(readers, [(1, 1, 1, 'not_started'), (2, 1, 2, 'in_progress')])

    def test_get_book_read_count(self):
        self.cursor.fetchone.return_value = (5,)
        n = db.get_book_read_count(1, self.conn)
        self.conn.execute.assert_called_with("""
        SELECT COUNT(*) FROM reading_list WHERE book = ? AND reading_status = 'complete'
    """,  (1,))
        assert n == 5

    def test_remove_from_reading_list(self):
        db.remove_from_reading_list(1, 1, self.conn)
        self.conn.execute.assert_called_with("""
        DELETE FROM reading_list WHERE book = ? AND user = ?
    """, (1, 1))
        self.conn.commit.assert_called_once()

    def test_update_reading_status(self):
        db.update_reading_status(1, 1, 'completed', self.conn)
        self.conn.execute.assert_called_with("""
        UPDATE reading_list
        SET reading_status = ?, updated_at = CURRENT_TIMESTAMP
        WHERE book = ? AND user = ?
    """, ('completed', 1, 1))
        self.conn.commit.assert_called_once()

if __name__ == "__main__":
    unittest.main()

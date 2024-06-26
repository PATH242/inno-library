import unittest
from unittest.mock import ANY, MagicMock, patch

from fastapi import HTTPException

import backend.models as models
import backend.service as service


class TestHasher(unittest.TestCase):
    def test_password_hash(self):
        password = "password242$"
        hash = service.Hasher.password_hash(password)
        self.assertTrue(isinstance(hash, str) and len(hash) > 0)

    def test_password_verification(self):
        password = "password242$"
        hash = service.Hasher.password_hash(password)
        self.assertTrue(service.Hasher.password_verification(password, hash))


class TestUser(unittest.TestCase):
    @patch("sqlite3.connect")
    @patch("backend.database.create_user")
    def test_create_user_valid(self, mock_create_user, mock_connect):
        mock_conn = MagicMock()
        mock_conn.close = MagicMock()
        mock_connect.return_value = mock_conn
        mock_create_user.return_value = None

        with patch("backend.service.User.verify_new_user", return_value=False):
            service.User.create_user("testuser", "password123", "password123")
            mock_create_user.assert_called_once_with("testuser", ANY, mock_conn)

    @patch("sqlite3.connect")
    def test_create_user_password_mismatch(self, mock_connect):
        with self.assertRaises(HTTPException) as context:
            service.User.create_user("testuser", "password123", "password321")
            mock_connect.assert_not_called()

        self.assertEqual(context.exception.status_code, 400)
        self.assertEqual(
            str(context.exception.detail), "Password and confirmation don't match!"
        )

    @patch("sqlite3.connect")
    @patch("backend.service.User.verify_new_user", return_value=True)
    def test_create_user_existing_user(self, mock_verify, mock_connect):
        mock_verify.return_value = True
        with self.assertRaises(HTTPException) as context:
            service.User.create_user("testuser", "password123", "password123")
            mock_connect.assert_not_called()
        self.assertEqual(context.exception.status_code, 400)
        self.assertEqual(str(context.exception.detail), "Username already exists!")

    @patch("sqlite3.connect")
    @patch("backend.database.get_user_by_username")
    def test_verify_new_user_exists(self, mock_get_user_by_username, mock_connect):
        mock_conn = MagicMock()
        mock_conn.close = MagicMock()
        mock_connect.return_value = mock_conn
        mock_get_user_by_username.return_value = [("user_id", "username", "hash")]

        result = service.User.verify_new_user("username")
        self.assertTrue(result)
        mock_get_user_by_username.assert_called_once_with("username", mock_conn)
        mock_conn.close.assert_called_once()

    @patch("sqlite3.connect")
    @patch("backend.database.get_user_by_username")
    def test_verify_new_user_not_exists(self, mock_get_user_by_username, mock_connect):
        mock_conn = MagicMock()
        mock_conn.close = MagicMock()
        mock_connect.return_value = mock_conn
        mock_get_user_by_username.return_value = []

        result = service.User.verify_new_user("username")
        self.assertFalse(result)
        mock_get_user_by_username.assert_called_once_with("username", mock_conn)
        mock_conn.close.assert_called_once()

    @patch("sqlite3.connect")
    @patch("backend.database.get_user_by_username")
    @patch("backend.service.Hasher.password_verification")
    def test_check_user_valid(
        self, mock_password_verification, mock_get_user_by_username, mock_connect
    ):
        mock_conn = MagicMock()
        mock_conn.close = MagicMock()
        mock_connect.return_value = mock_conn
        user_tuple = (1, "username", "hashed_password")
        mock_get_user_by_username.return_value = user_tuple
        mock_password_verification.return_value = True

        user = service.User.check_user("username", "password")
        self.assertEqual(user, user_tuple)
        mock_get_user_by_username.assert_called_once_with("username", mock_conn)
        mock_password_verification.assert_called_once_with(
            "password", "hashed_password"
        )
        mock_conn.close.assert_called_once()

    @patch("sqlite3.connect")
    @patch("backend.database.get_user_by_username")
    def test_check_user_not_found(self, mock_get_user_by_username, mock_connect):
        mock_conn = MagicMock()
        mock_conn.close = MagicMock()
        mock_connect.return_value = mock_conn
        mock_get_user_by_username.return_value = None

        with self.assertRaises(HTTPException) as context:
            service.User.check_user("username", "password")
        self.assertEqual(context.exception.status_code, 404)
        mock_get_user_by_username.assert_called_once_with("username", mock_conn)
        mock_conn.close.assert_called_once()

    @patch("sqlite3.connect")
    @patch("backend.database.get_user")
    def test_get_user(self, mock_get_user, mock_connect):
        mock_conn = MagicMock()
        mock_conn.close = MagicMock()
        mock_connect.return_value = mock_conn
        user_tuple = (1, "username")
        mock_get_user.return_value = user_tuple

        user = service.User.get_user(1)
        self.assertIsInstance(user, models.User)
        self.assertEqual(user.id, 1)
        self.assertEqual(user.username, "username")
        mock_get_user.assert_called_once_with(1, mock_conn)
        mock_conn.close.assert_called_once()


class TestBook(unittest.TestCase):
    @patch("sqlite3.connect")
    @patch("backend.database.get_book")
    @patch("backend.database.get_book_read_count")
    def test_from_db_book_found(
        self, mock_get_book_read_count, mock_get_book, mock_connect
    ):
        mock_conn = MagicMock()
        mock_conn.close = MagicMock()
        mock_connect.return_value = mock_conn
        mock_get_book.return_value = (1, "Book Title", "Author Name", "Genre")
        mock_get_book_read_count.return_value = 100

        book = service.Book.from_db(1)
        self.assertIsInstance(book, models.Book)
        self.assertEqual(book.id, 1)
        self.assertEqual(book.title, "Book Title")
        mock_get_book.assert_called_once_with(1, mock_conn)
        mock_get_book_read_count.assert_called_once_with(1, mock_conn)
        mock_conn.close.assert_called_once()

    @patch("sqlite3.connect")
    @patch("backend.database.get_book")
    def test_from_db_book_not_found(self, mock_get_book, mock_connect):
        mock_conn = MagicMock()
        mock_conn.close = MagicMock()
        mock_connect.return_value = mock_conn
        mock_get_book.return_value = None

        with self.assertRaises(HTTPException) as context:
            service.Book.from_db(1)
        self.assertEqual(context.exception.status_code, 404)
        mock_get_book.assert_called_once_with(1, mock_conn)

    @patch("sqlite3.connect")
    @patch("backend.database.get_books")
    @patch("backend.database.get_book_read_count")
    @patch("backend.database.get_book_count")
    def test_get_books(
        self,
        mock_get_book_count,
        mock_get_book_read_count,
        mock_get_books,
        mock_connect,
    ):
        mock_conn = MagicMock()
        mock_conn.close = MagicMock()
        mock_connect.return_value = mock_conn
        mock_get_books.return_value = [(1, "Book Title", "Author", "Genre")]
        mock_get_book_read_count.return_value = 100
        mock_get_book_count.return_value = 20

        books = service.Book.get_books(0, 1)
        self.assertIsInstance(books, models.Books)
        self.assertEqual(len(books.books), 1)
        self.assertEqual(books.books[0].title, "Book Title")
        self.assertEqual(books.books[0].author, "Author")
        self.assertEqual(books.books[0].genre, "Genre")

        mock_get_books.assert_called_once_with(0, 1, mock_conn)
        mock_get_book_read_count.assert_called_once_with(1, mock_conn)
        mock_conn.close.assert_called_once()

    @patch("sqlite3.connect")
    @patch("backend.database.get_book_read_count")
    @patch("backend.database.search_book_by_title")
    def test_search_book_found(
        self, mock_search_book_by_title, mock_get_book_read_count, mock_connect
    ):
        mock_conn = MagicMock()
        mock_conn.close = MagicMock()
        mock_connect.return_value = mock_conn
        mock_search_book_by_title.return_value = [(1, "Book Title", "Author", "Genre")]
        mock_get_book_read_count.return_value = 100

        books = service.Book.search_book("Book Title")
        self.assertIsInstance(books, list)
        self.assertEqual(len(books), 1)
        self.assertEqual(books[0].title, "Book Title")
        self.assertEqual(books[0].author, "Author")
        self.assertEqual(books[0].genre, "Genre")

        mock_search_book_by_title.assert_called_once_with("Book Title", mock_conn)
        mock_conn.close.assert_called_once()

    @patch("sqlite3.connect")
    @patch("backend.database.search_book_by_title")
    def test_search_book_not_found(self, mock_search_book_by_title, mock_connect):
        mock_conn = MagicMock()
        mock_conn.close = MagicMock()
        mock_connect.return_value = mock_conn
        mock_search_book_by_title.return_value = []

    @patch("sqlite3.connect")
    @patch("backend.database.get_genres")
    def test_get_genres(self, mock_get_genres, mock_connect):
        mock_conn = MagicMock()
        mock_conn.close = MagicMock()
        mock_connect.return_value = mock_conn
        genre_list = ["Fantasy", "Science Fiction", "Mystery"]
        mock_get_genres.return_value = genre_list

        genres = service.Book.get_genres()
        self.assertEqual(genres, genre_list)
        mock_get_genres.assert_called_once_with(mock_conn)
        mock_conn.close.assert_called_once()

    @patch("sqlite3.connect")
    @patch("backend.database.get_books_by_genre")
    @patch("backend.database.get_book_read_count")
    def test_get_books_by_genre(
        self, mock_get_book_read_count, mock_get_books_by_genre, mock_connect
    ):
        mock_conn = MagicMock()
        mock_conn.close = MagicMock()
        mock_connect.return_value = mock_conn
        book_data = [
            (1, "Book_1", "Author_1", "Fantasy", 10),
            (2, "Book_2", "Author_2", "Fantasy", 30),
            (3, "Book_3", "Author_3", "Fantasy", 15),
        ]
        mock_get_books_by_genre.return_value = book_data
        mock_get_book_read_count.side_effect = lambda book_id, conn: (
            10 if book_id == 1 else (20 if book_id == 2 else 15)
        )

        books = service.Book.get_books_by_genre("Fantasy")
        self.assertEqual(len(books), 3)
        # Book Two should be first due to higher reads
        self.assertEqual(books[0].id, 2)
        self.assertEqual(books[1].id, 3)
        self.assertEqual(books[2].id, 1)

        mock_get_books_by_genre.assert_called_once_with("Fantasy", mock_conn)
        calls = [((book_id, mock_conn),) for book_id in [1, 2, 3]]
        mock_get_book_read_count.assert_has_calls(calls, any_order=True)
        mock_conn.close.assert_called_once()


class TestReadingList(unittest.TestCase):
    @patch("sqlite3.connect")
    @patch("backend.service.Book.from_db")
    @patch("backend.database.get_reading_lists")
    def test_init_and_load(self, mock_get_reading_lists, mock_from_db, mock_connect):
        mock_conn = MagicMock()
        mock_conn.close = MagicMock()
        mock_connect.return_value = mock_conn
        mock_get_reading_lists.return_value = [
            (
                1,
                101,
                1,
                "complete",
                "2024-04-27T15:32:30",
                "2024-04-27T15:32:30",
            ),
            (
                2,
                102,
                1,
                "not_started",
                "2024-04-27T15:32:30",
                "2024-04-27T15:32:30",
            ),
        ]
        mock_from_db.side_effect = lambda book_id: MagicMock(
            id=book_id,
            title=f"Book {book_id}",
            author="Author A",
            genre="Fantasy",
            reads=50,
        )

        reading_list = service.ReadingList(user_id=1)
        self.assertEqual(len(reading_list.books), 2)
        mock_get_reading_lists.assert_called_once_with(1, mock_conn)
        mock_from_db.assert_has_calls(
            [unittest.mock.call(101), unittest.mock.call(102)]
        )
        mock_conn.close.assert_called_once()

    @patch("sqlite3.connect")
    @patch("backend.database.create_reading_list")
    @patch("backend.database.get_book_in_reading_list")
    def test_add_book(
        self,
        mock_get_book_in_reading_list,
        mock_create_reading_list,
        mock_connect,
    ):
        mock_conn = MagicMock()
        mock_conn.close = MagicMock()
        mock_connect.return_value = mock_conn
        mock_get_book_in_reading_list.return_value = ()

        reading_list = service.ReadingList(user_id=1)
        mock_conn.close.assert_called_once()
        reading_list.add_book(book_id=101, status=models.StatusEnum.not_started)
        mock_get_book_in_reading_list.assert_called_once_with(1, 101, mock_conn)
        mock_create_reading_list.assert_called_once_with(
            1, 101, models.StatusEnum.not_started, mock_conn
        )
        mock_conn.close.assert_has_calls(([], []))

    @patch("sqlite3.connect")
    @patch("backend.database.get_completed_books")
    def test_read_books(self, mock_get_completed_books, mock_connect):
        mock_conn = MagicMock()
        mock_conn.close = MagicMock()
        mock_connect.return_value = mock_conn
        mock_get_completed_books.return_value = ["Book 101", "Book 102"]

        reading_list = service.ReadingList(user_id=1)
        mock_conn.close.assert_called_once()
        books = reading_list.read_books()
        self.assertEqual(books, ["Book 101", "Book 102"])
        mock_get_completed_books.assert_called_once_with(1, mock_conn)
        mock_conn.close.assert_has_calls(([], []))

    @patch("sqlite3.connect")
    @patch("backend.database.remove_from_reading_list")
    def test_remove_book(self, mock_remove_from_reading_list, mock_connect):
        mock_conn = MagicMock()
        mock_conn.close = MagicMock()
        mock_connect.return_value = mock_conn

        reading_list = service.ReadingList(user_id=1)
        mock_conn.close.assert_called_once()
        reading_list.remove_book(book_id=101)
        mock_remove_from_reading_list.assert_called_once_with(1, 101, mock_conn)
        mock_conn.close.assert_has_calls(([], []))

    @patch("sqlite3.connect")
    @patch("backend.database.update_reading_status")
    def test_change_reading_status(self, mock_update_reading_status, mock_connect):
        mock_conn = MagicMock()
        mock_conn.close = MagicMock()
        mock_connect.return_value = mock_conn
        user_id = 1
        book_id = 101
        new_status = models.StatusEnum.started

        reading_list = service.ReadingList(user_id)
        mock_conn.close.assert_called_once()
        reading_list.change_reading_status(book_id, new_status)

        mock_update_reading_status.assert_called_once_with(
            user_id, book_id, new_status, mock_conn
        )
        mock_conn.close.assert_has_calls(([], []))

    @patch("sqlite3.connect")
    @patch("backend.database.get_books_by_genre")
    @patch("backend.service.ReadingList.get_genres", return_value=["Fantasy"])
    @patch("backend.service.Book.from_db")
    def test_get_recommendations(
        self, mock_from_db, mock_get_genres, mock_get_books_by_genre, mock_connect
    ):
        mock_conn = MagicMock()
        mock_conn.close = MagicMock()
        mock_connect.return_value = mock_conn

        mock_get_genres.return_value = ["Fantasy", "Science Fiction"]
        mock_get_books_by_genre.return_value = [
            (101, "Fantasy Book", "Author A", "Fantasy", 50),
            (102, "Sci-Fi Book", "Author B", "Science Fiction", 30),
        ]
        book_mocks = [
            MagicMock(id=101, genre="Fantasy", reads=50),
            MagicMock(id=102, genre="Science Fiction", reads=30),
        ]
        mock_from_db.side_effect = book_mocks

        reading_list = service.ReadingList(user_id=1)
        reading_list.books = [book_mocks[0]]
        recommendations = reading_list.get_recommendations(n=2)

        self.assertEqual(len(recommendations), 1)
        self.assertEqual(recommendations[0].id, 102)
        mock_get_books_by_genre.assert_has_calls(
            [
                unittest.mock.call("Fantasy", mock_conn),
                unittest.mock.call("Science Fiction", mock_conn),
            ]
        )
        mock_from_db.assert_has_calls(
            [unittest.mock.call(101), unittest.mock.call(102)], any_order=True
        )
        mock_conn.close.assert_has_calls(([], []))

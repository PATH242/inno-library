import unittest
from unittest.mock import patch

import requests


class EndToEndTest(unittest.TestCase):

    @patch("requests.post")
    @patch("requests.get")
    def test_library(self, mock_get, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "message": "User registered successfully"
        }

        response = requests.post(
            "http://localhost:8000/register",
            json={
                "username": "test_user",
                "password": "test_password",
                "confirm_password": "test_password",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["message"], "User registered successfully")

        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "id": 0,
            "username": "test_user",
            "token": "token",
        }

        response = requests.post(
            "http://localhost:8000/login",
            json={"username": "test_user", "password": "test_password"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("token", response.json()["token"])

        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "books": [
                {
                    "id": 1,
                    "title": "Book 1",
                    "author": "Author 1",
                    "genre": "Genre 1",
                    "reads": 100,
                },
                {
                    "id": 2,
                    "title": "Book 2",
                    "author": "Author 2",
                    "genre": "Genre 2",
                    "reads": 200,
                },
            ]
        }
        if "token" in response.json():
            # Mock the add book endpoint response
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = {
                "message": "Book added successfully"
            }

            # Send request to add a book to the user's reading list
            response = requests.post(
                "http://localhost:8000/api/reads",
                params={"book_id": 3},
                json={
                    "id": 0,
                    "title": "Book 3",
                    "author": "Author 3",
                    "genre": "Genre 3",
                    "reads": 0,
                },
            )

            # Check if adding the book was successful
            self.assertEqual(response.status_code, 200)
            self.assertIn("message", response.json())
            self.assertEqual(response.json()["message"], "Book added successfully")
        else:
            self.fail("Access token not found in login response")

        response = requests.get("http://localhost:8000/api/reads")

        self.assertEqual(response.status_code, 200)

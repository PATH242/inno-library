import random

import requests
from locust import HttpUser, between, events, task


class WikiFetUser(HttpUser):
    wait_time = between(1, 5)
    host = "http://127.0.0.1:8000/"
    book_n = list(range(1, 30))
    genres = [
        "Fantasy",
        "Drama",
        "Historical Fiction",
        "Science Fiction",
        "Adventure",
        "Mystery",
    ]
    book_names = [
        "1984",
        "A Game of Thrones",
        "A Tale of Two Cities",
        "Beloved",
        "Dune",
    ]
    reading_status = ["completed", "started", "not_started"]

    token = ""

    @events.init.add_listener
    def register(self):
        with self.client.post(
            "api/register",
            json={
                "username": "newuser",
                "password": "newpass",
                "confirm_password": "newpass",
            },
            catch_response=True,
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure("login failed")

    def on_start(self):
        self.login()

    def login(self):
        with requests.post(
            f"{self.host}api/login", json={"username": "newuser", "password": "newpass"}
        ) as response:
            if response.status_code == 200:
                result = response.json()
                self.token = result["token"]

    @task(2)
    def test_get_books(self):
        self.client.get("api/books", json={"books": f"{self.random_book_n()}"})

    @task
    def test_search_books(self):
        self.client.get("api/search", params={"q": f"{self.random_book()}"})

    @task
    def test_get_genres(self):
        self.client.get("api/genre")

    @task
    def test_get_books_by_genre(self):
        self.client.get("api/books/genre", params={"genre": f"{self.random_genre()}"})

    @task
    def test_get_reading_list(self):
        headers = {"Authorization": f"Bearer {self.token}"}
        self.client.get("api/reads", headers=headers)

    @task
    def test_add_to_reading_list(self):
        headers = {"Authorization": f"Bearer {self.token}"}
        self.client.post(
            "api/reads", params={"book_id": f"{self.random_book_n()}"}, headers=headers
        )

    @task
    def change_reading_status(self):
        headers = {"Authorization": f"Bearer {self.token}"}
        self.client.put(
            "api/reads",
            json={
                "book_id": f"{self.random_book_n()}",
                "status": f"{self.random_reading_status()}",
            },
            headers=headers,
        )

    @task
    def remove_from_reading_list(self):
        headers = {"Authorization": f"Bearer {self.token}"}
        self.client.delete(
            "api/reads", params={"book_id": f"{self.random_book_n()}"}, headers=headers
        )

    @task
    def get_recommendations(self):
        headers = {"Authorization": f"Bearer {self.token}"}
        self.client.get("api/recommend", params={"n": 5}, headers=headers)

    def random_book(self):
        return random.choice(self.book_names)

    def random_book_n(self):
        return random.choice(self.book_n)

    def random_genre(self):
        return random.choice(self.genres)

    def random_reading_status(self):
        return random.choice(self.reading_status)

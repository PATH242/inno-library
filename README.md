# Online book library

Web-based application allowing users to add books to their library, see recommended books, and track their reading progress.

## Table of contents

- [Online book library](#online-book-library)
  - [Table of contents](#table-of-contents)
  - [Features](#features)
  - [Technologies](#technologies)
  - [Setup](#setup)
  - [Development](#development)

## Features

- Search for books
- Add books to personal library
- Track reading progress
- See recommended books based on personal library

## Technologies

- Backend: FastAPI
- Database: SQLite
- Frontend: React + Typescript
- Package manager: Poetry

## Setup

1. Clone the repository
2. Install the dependencies

```bash
poetry install --only main
```
3. Run the application

```bash
poetry run uvicorn backend.app:app --reload
```

## Development

1. Clone the repository
2. Install the dependencies with the development dependencies

```bash
poetry install
```
3. Install pre-commit hooks

```bash
poetry run pre-commit install
```

4. Run tests

```bash
poetry run pytest
```

5. Run the application

```bash
poetry run uvicorn backend.app:app --reload
```

6. Run Performance testing with locust

```bash
cd tests/performance && locust --users=5 --spawn-rate=3 --run-time=500s
```

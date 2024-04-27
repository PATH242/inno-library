# Online book library

Web-based application allowing users to add books to their library, see recommended books, and track their reading progress.

## Table of contents

- [Online book library](#online-book-library)
  - [Table of contents](#table-of-contents)
  - [Technologies](#technologies)
  - [Setup](#setup)
  - [Development](#development)

## Technologies

- Backend: FastAPI
- Database: SQLite
- Frontend: Streamlit
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

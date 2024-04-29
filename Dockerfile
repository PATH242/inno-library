FROM python:3.11-slim

WORKDIR /app


RUN pip install --no-cache-dir poetry

COPY pyproject.toml poetry.lock ./
COPY backend/.env /app/backend/.env

RUN poetry config virtualenvs.create false \
    && poetry install --only main --no-interaction --no-ansi

COPY backend /app/backend

EXPOSE 8000

CMD ["poetry", "run", "uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8000"]

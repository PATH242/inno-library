FROM python:3.11-slim

WORKDIR /backend


RUN pip install --no-cache-dir poetry

COPY . .

RUN poetry config virtualenvs.create false \
    && poetry install --no-dev --no-interaction --no-ansi
EXPOSE 8000

CMD ["poetry", "run", "uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8000"]

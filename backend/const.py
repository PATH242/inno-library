import os

from dotenv import load_dotenv

BASEDIR = os.path.abspath(os.path.dirname(__file__))

load_dotenv(os.path.join(BASEDIR, ".env"))

SQLITE_DB = os.environ.get("SQLITE_DB", "db.sqlite3")

SECRET_KEY: str = os.environ.get("JWT_SECRET")  # type: ignore
ALGORITHM: str = os.environ.get("JWT_ALGORITHM")  # type: ignore
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("JWT_EXPIRE_MINUTES", 240))

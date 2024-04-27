import os
from dotenv import load_dotenv

load_dotenv()

SQLITE_DB = os.environ.get("SQLITE_DB", 'db.sqlite3')

SECRET_KEY = os.environ.get("JWT_SECRET")
ALGORITHM = os.environ.get("JWT_ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("JWT_EXPIRE_MINUTES", 240))
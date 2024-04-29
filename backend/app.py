import logging
import sqlite3

from fastapi import FastAPI
from fastapi.middleware import cors

from . import const, database
from .router import router

logging.basicConfig(
    level=logging.INFO, format="<%(asctime)s> - <%(levelname)s> - <%(message)s>"
)

app = FastAPI()

conn = sqlite3.connect(const.SQLITE_DB)
database.create_tables(conn)
conn.close()

app.include_router(router)

# Add middlewares against CORS issue
app.add_middleware(
    cors.CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def healthcheck() -> dict[str, str]:
    """
    Healtcheck route. Returns `{"status": "ok"}` if the server is running.
    """
    return {"status": "ok"}


@app.on_event("startup")
async def startup_event():
    logger = logging.getLogger("uvicorn.access")
    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter("<%(asctime)s> - <%(levelname)s> - <%(message)s>")
    )
    logger.addHandler(handler)

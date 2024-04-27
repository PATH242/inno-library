import sqlite3

from fastapi import FastAPI
from fastapi.middleware import cors

from . import const, database
from .router import router

app = FastAPI()

conn = sqlite3.connect(const.SQLITE_DB)
database.create_tables(conn)
conn.close()

app.include_router(router)

app.add_middleware(
    cors.CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def healthcheck():
    return {"status": "ok"}

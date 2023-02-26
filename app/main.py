from fastapi import FastAPI
from sqlmodel import SQLModel

from app.db.database import engine
from app.routers import exercises, musclegroups

app = FastAPI()

app.include_router(exercises.router)
app.include_router(musclegroups.router)


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


@app.get("/")
async def root():
    return {"message": "Hello World!"}

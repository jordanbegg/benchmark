import os

from dotenv import load_dotenv
from sqlmodel import create_engine, SQLModel

load_dotenv()

db_url = os.environ.get("SQLALCHEMY_DATABASE_URL")

engine = create_engine(
    db_url,
    echo=True,
    connect_args={"check_same_thread": False},
)

SQLModel.metadata.create_all(engine)

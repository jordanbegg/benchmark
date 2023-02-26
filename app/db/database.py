import os

from dotenv import load_dotenv
from sqlmodel import create_engine

load_dotenv()

engine = create_engine(
    os.environ.get("SQLALCHEMY_DATABASE_URL"),
    echo=True,
    connect_args={"check_same_thread": False},
)

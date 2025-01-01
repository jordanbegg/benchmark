from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session

from app.db.database import engine


def get_session():
    with Session(engine) as session:
        yield session


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

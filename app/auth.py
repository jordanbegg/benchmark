from datetime import datetime, timedelta, timezone
from functools import wraps
import os
from typing import Annotated

from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
import jwt
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlmodel import Session, select

from app.db.models import User
from app.dependencies import get_session, oauth2_scheme

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password):
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


load_dotenv()

SECRET_KEY = os.environ.get("TOKEN_SECRET_KEY")
ALGORITHM = "HS256"


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email_address: str | None = None


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=120)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_user(email_address: str, session: Session) -> User:
    db_user = session.exec(
        select(User).where(User.email_address == email_address.lower())
    ).first()
    return db_user


def authenticate_user(email_address: str, password: str, session: Session):
    user = get_user(email_address=email_address, session=session)
    if not user:
        return False
    if not verify_password(password, user.password_hash):
        return False
    return user


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Annotated[Session, Depends(get_session)],
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email_address: str = payload.get("sub")
        if email_address is None:
            raise credentials_exception
        token_data = TokenData(email_address=email_address)
    except InvalidTokenError:
        raise credentials_exception
    user = get_user(email_address=token_data.email_address, session=session)
    if user is None:
        raise credentials_exception
    return user


def require_permission(*permissions: str):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            current_user = kwargs.get("current_user")
            if not current_user or not any(
                current_user.has(permission) for permission in permissions
            ):
                raise HTTPException(
                    status_code=400,
                    detail=f"User does not have any of the required permission {permissions}",
                )
            return func(*args, **kwargs)

        return wrapper

    return decorator

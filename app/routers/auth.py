from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from sqlmodel import Session

from app.dependencies import get_session
from app.auth import authenticate_user, Token, create_access_token

ACCESS_TOKEN_EXPIRE_MINUTES = 120

router = APIRouter(
    prefix="/auth",
    responses={404: {"description": "Not Found"}},
)

# @router.post("/", response_model=UserRead)
# def login_user(*, session: Session = Depends(get_session), user: UserLogin):
#     db_user = session.exec(
#         select(User).where(User.email_address == user.email_address.lower())
#     ).first()
#     if not db_user or not verify_password(user.password, db_user.password_hash):
#         raise HTTPException(status_code=400, detail="Invalid credentials")
#     return db_user


@router.post("/token", response_model=Token)
async def login(
    *,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Session = Depends(get_session),
):
    db_user = authenticate_user(form_data.username, form_data.password, session=session)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": db_user.email_address}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")

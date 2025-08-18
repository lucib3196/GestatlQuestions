from backend_api.data.database import SessionDep
from backend_api.model.users import User
from typing import Annotated
from fastapi import Query
from sqlmodel import select

from collections.abc import Sequence

# Standard Library
from typing import Annotated

# FastAPI
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

# SQLAlchemy / SQLModel
from sqlalchemy.exc import IntegrityError
from backend_api.core.logging import logger

# Third-party
from jose import JWTError
from passlib.context import CryptContext
from starlette import status

# Project-specific
from backend_api.core.auth import (
    check_password,
    decode_token,
    encrypt_password,
    generate_token,
)
from backend_api.core.config import settings
from backend_api.core.logging import logger
from backend_api.data.database import SessionDep
from backend_api.model import users as users_model
from backend_api.model import token as token_model
from typing import Optional

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM

bcrypt = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def create_user(user: User, session: SessionDep) -> User:
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


async def add_user(
    user_create: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: SessionDep,
    role: users_model.UserRole = users_model.UserRole.USER,
) -> users_model.User | users_model.UserRead:
    try:
        existing_user = session.exec(
            select(users_model.User).where(
                users_model.User.username == user_create.username
            )
        ).first()
        if not existing_user:
            user_create.password = encrypt_password(user_create.password)
            db_user = users_model.User.model_validate(user_create)
            # Add user and assign role
            db_user.role = role
            await create_user(db_user, session)
            return users_model.UserRead(
                username=db_user.username, success=True, role=role
            )
    except IntegrityError as e:
        session.rollback()
        if "user.email" in str(e.orig):
            raise HTTPException(status_code=409, detail="Email already registered")
    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        ) from e
    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT, detail="User already exist"
    )


async def login_for_access_token(
    token: Annotated[OAuth2PasswordRequestForm, Depends()], session: SessionDep
) -> token_model.Token:
    user = session.exec(
        select(users_model.User).where(users_model.User.username == token.username)
    ).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incorrect username",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not check_password(token.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incorrect password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = generate_token(username=token.username)
    logger.info("Login Complete", access_token)
    return token_model.Token(access_token=access_token, token_type="bearer")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_bearer)], session: SessionDep
) -> users_model.UserRead:

    try:
        payload = decode_token(token)
        username = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        token_data = token_model.TokenData(username=username)
    except JWTError as e:
        logger.error(e)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e

    user = session.exec(
        select(users_model.User).where(users_model.User.username == token_data.username)
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return users_model.UserRead(username=user.username, email=user.email, success=True)


async def get_all_users(
    session: SessionDep, offset: int = 0, limit: Annotated[int, Query(le=100)] = 100
) -> Sequence[User]:
    result = session.exec(select(User).offset(offset).limit(limit))
    users = result.all()
    return users


async def get_user_by_name(
    username: Optional[str], email: Optional[str], session: SessionDep
):
    if username is None and email is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provide either 'username' or 'email'.",
        )

    result = None  # ✅ initialize

    if username is not None:
        result = session.exec(select(User).where(User.username == username)).first()
    elif email is not None:
        result = session.exec(select(User).where(User.email == email)).first()

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found."
        )

    return result.id


async def get_user(session: SessionDep, id: int):
    result = session.exec(select(User).where(User.id == id)).first()
    if not result:
        return {"detail": "User Not Found"}
    else:
        return result


async def delete_user(session: SessionDep, id: int):
    user = await get_user(session, id=id)
    if not isinstance(user, User):
        return {"detail", "Cannot Delete User. Does not exit"}
    session.delete(user)
    session.commit()
    return {"ok": True}

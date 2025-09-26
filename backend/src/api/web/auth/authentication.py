# ========================
# Standard Library Imports
# ========================
from typing import Union, Annotated

# ===============
# FastAPI Imports
# ===============
from fastapi import APIRouter, Depends, Header, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

# ===========================
# SQLAlchemy / SQLModel Tools
# ===========================
from sqlalchemy.orm import Session

# ======================
# Third-Party Libraries
# ======================
from passlib.context import CryptContext
from starlette import status

# =====================
# Project-Specific Code
# =====================
from src.api.core.config import settings
from src.api.core.logging import logger
from src.api.database.database import get_session, SessionDep
from src.api.models import users_model as users_model
from src.api.models import token_model as token_model
from src.api.service.auth import user as service

# ==================
# Router Declaration
# ==================
router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

# =====================
# Auth Security Schemes
# =====================
bcrypt = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="/login")


# =================
# Route: /signup
# =================
@router.post(
    "/signup",
    status_code=status.HTTP_201_CREATED,
    response_model=Union[users_model.User, users_model.UserRead],
)
async def create_user(
    user_create: users_model.UserCreate,
    session: SessionDep,
) -> Union[users_model.User, users_model.UserRead]:
    return await service.add_user(user_create, session)  # type: ignore


# =================
# Route: /login
# =================
@router.post(
    "/login",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=token_model.Token,
)
async def login_user(
    token: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Session = Depends(get_session),
) -> token_model.Token:
    return await service.login_for_access_token(token, session)  # type: ignore


# ========================
# Route: /current_user
# ========================
@router.get("/current_user")
async def get_current_user(
    token: Annotated[str, Depends(oauth2_bearer)],
    session: SessionDep,
) -> users_model.UserRead:
    return await service.get_current_user(token, session)


@router.get("/get_all_users/{limit}/{offset}")
async def get_all_users(session: SessionDep, limit: int, offset: int):
    return await service.get_all_users(session=session, offset=offset, limit=limit)

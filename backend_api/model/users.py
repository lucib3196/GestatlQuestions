from __future__ import annotations
from enum import Enum
from typing import Optional, List, TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from .questions_models import Question


class UserRole(str, Enum):
    ADMIN = "admin"
    TEACHER = "teacher"
    DEVELOPER = "moderator"
    USER = "user"


class UserBase(SQLModel):
    username: str
    role: UserRole = Field(default=UserRole.USER)
    fullname: Optional[str] = None
    email: Optional[str] = None
    disabled: Optional[bool] = None


class UserCreate(UserBase):
    password: str


class UserRead(UserBase):
    success: bool


class User(SQLModel, table=True):
    id: Optional[int] = Field(
        default=None,
        sa_column=Column(
            Integer, primary_key=True, index=True, unique=True, autoincrement=True
        ),
    )
    username: str = Field(sa_column=Column(String, unique=True, index=True))
    password: str = Field(sa_column=Column(String))
    fullname: Optional[str] = Field(default=None, sa_column=Column(String))
    email: Optional[str] = Field(default=None, sa_column=Column(String, unique=True))

    role: str = Field(default="user", sa_column=Column(String))

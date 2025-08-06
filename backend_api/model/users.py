from sqlmodel import Field, SQLModel
from sqlalchemy import Column, Integer, String
from typing import Optional


class UserBase(SQLModel):
    username: str
    fullname: Optional[str] = None
    email: Optional[str] = None
    disabled: Optional[bool] = None


class UserCreate(UserBase):
    password: str


class UserRead(UserBase):
    suceess: bool


class User(UserBase, table=True):
    id: Optional[int] = Field(
        default=None,
        sa_column=Column(
            Integer, primary_key=True, index=True, unique=True, autoincrement=True
        ),
    )
    username: str = Field(sa_column=Column(Integer, unique=True, index=True))
    password: str = Field(sa_column=Column(String))
    fullname: Optional[str] = Field(default=None, sa_column=Column(String))
    email: Optional[str] = Field(default=None, sa_column=Column(String))

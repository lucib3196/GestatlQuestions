from __future__ import annotations

from typing import List, Optional, Union, Literal, TypedDict
from uuid import UUID, uuid4
from ai_workspace.agents.question_to_json.models import QuestionBase, Solution
from sqlalchemy import Boolean, JSON, Column, text
from sqlalchemy.orm import (
    relationship as sa_relationship,
)
from sqlmodel import SQLModel, Field, Relationship
from pydantic import BaseModel, Field as PydanticField

# ----- Pydantic models -----


class CodeLanguage(BaseModel):
    language: Literal["python", "javascript"]


class QuestionMeta(BaseModel):
    question: str
    title: str
    topic: List[str]
    relevant_courses: List[str]
    tags: List[str]
    prereqs: List[str]
    isAdaptive: Union[str, bool]


class QuestionMetaNew(BaseModel):
    rendering_data: List["QuestionBase"]  # keep your import if you use it
    qtype: Optional[List[Literal["numeric", "multiple_choice"]]] = PydanticField(
        default=None
    )
    title: str
    topic: List[str]
    relevantCourses: List[str]
    tags: Optional[List[str]] = PydanticField(default_factory=list)
    prereqs: Optional[List[str]] = PydanticField(default_factory=list)
    isAdaptive: Union[str, bool]
    createdBy: Optional[str] = ""
    language: Optional[List[Literal["python", "javascript"]]] = None
    ai_generated: Optional[bool] = None


# ----- SQLModel tables -----


class File(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    filename: str
    content: Optional[Union[str, dict]] = Field(default=None, sa_column=Column(JSON))
    question_id: UUID = Field(foreign_key="question.id")


# Association table for many-to-many
class QuestionTopic(SQLModel, table=True):
    question_id: UUID = Field(foreign_key="question.id", primary_key=True, index=True)
    topic_id: UUID = Field(foreign_key="topic.id", primary_key=True, index=True)


class Question(SQLModel, table=True):

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)

    title: Optional[str] = None
    ai_generated: Optional[bool] = None

    # SQLite default TRUE -> "1" ; Postgres -> "true"
    isAdaptive: bool = Field(
        default=True,
        sa_column=Column(Boolean, nullable=False, server_default=text("1")),
    )

    language: Optional[List[Literal["python", "javascript"]]] = Field(
        default=None, sa_column=Column(JSON)
    )
    qtype: Optional[List[Literal["numeric", "multiple_choice"]]] = Field(
        default=None, sa_column=Column(JSON)
    )

    createdBy: Optional[str] = None
    user_id: Optional[int] = Field(foreign_key="user.id")

    topics: list["Topic"] = Relationship(
        sa_relationship=sa_relationship(
            "Topic",
            secondary=QuestionTopic.__table__,  # type: ignore
            back_populates="questions",
        )
    )


class Topic(SQLModel, table=True):

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(index=True, unique=True)

    questions: list["Question"] = Relationship(
        sa_relationship=sa_relationship(
            "Question",
            secondary=QuestionTopic.__table__,  # type: ignore
            back_populates="topics",
        )
    )


# (Optional) helper type for filters
class QuestionDict(TypedDict, total=False):
    id: UUID
    user_id: int
    title: str
    qtype: str
    topic: str
    isAdaptive: Union[str, bool]
    language: List[str]
    createdBy: str
    ai_generated: bool

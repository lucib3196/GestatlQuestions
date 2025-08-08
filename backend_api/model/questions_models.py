from __future__ import annotations

from uuid import UUID, uuid4
from typing import List, Optional, Union, Literal

from sqlalchemy import JSON, Column
from sqlmodel import SQLModel, Field, Relationship
from pydantic import BaseModel, Field as PydanticField

from ai_workspace.agents.question_to_json.models import (
    QuestionInput,
    Solution,
    QuestionBase,
)


class CodeLanguage(BaseModel):
    language: Literal["python", "javascript"]


# Pydantic models
class QuestionMeta(BaseModel):
    question: str
    title: str
    topic: List[str]
    relevant_courses: List[str]
    tags: List[str]
    prereqs: List[str]
    isAdaptive: Union[str, bool]


class QuestionMetaNew(BaseModel):
    rendering_data: List[QuestionBase]
    solution_render: Optional[Solution] = None
    qtype: Optional[List[Literal["numeric", "multiple_choice"]]] = PydanticField(
        default=None
    )
    title: str
    topic: List[str]
    relevantCourses: List[str]
    tags: Optional[List[str]] = []
    prereqs: Optional[List[str]] = []
    isAdaptive: Union[str, bool]
    createdBy: Optional[str] = ""
    language: Optional[List[CodeLanguage]] = None
    ai_generated: Optional[bool] = None


# SQLModel tables
class File(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    filename: str
    content: Optional[Union[str, dict]] = Field(default=None, sa_column=Column(JSON))
    question_id: UUID = Field(foreign_key="question.id")
    question: Optional["Question"] = Relationship(back_populates="files")


class Question(SQLModel, table=True):
    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        index=True,
        nullable=False,
        sa_column_kwargs={"unique": True},
    )
    files: List["File"] = Relationship(back_populates="question")

    user_id: Optional[int] = Field(foreign_key="user.id")
    user: Optional["User"] = Relationship(back_populates="questions")  # type: ignore

    qtype: Optional[List[Literal["numeric", "multiple_choice"]]] = Field(
        default=None, sa_column=Column(JSON)
    )
    title: Optional[str] = Field(default=None)
    topic: Optional[List[str]] = Field(default=None, sa_column=Column(JSON))
    isAdaptive: Optional[Union[str, bool]] = Field(default=None, sa_column=Column(JSON))
    createdBy: Optional[str] = Field(default=None)
    language: Optional[List[CodeLanguage]] = Field(default=None, sa_column=Column(JSON))
    ai_generated: Optional[bool] = Field(default=None)

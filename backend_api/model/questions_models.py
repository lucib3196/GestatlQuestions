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
from typing import TypedDict


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
    language: Optional[List[Literal["python", "javascript"]]] = None
    ai_generated: Optional[bool] = None


# SQLModel tables
class File(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    filename: str
    content: Optional[Union[str, dict]] = Field(default=None, sa_column=Column(JSON))
    question_id: UUID = Field(foreign_key="question.id")


class Question(SQLModel, table=True):
    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        index=True,
        nullable=False,
        sa_column_kwargs={"unique": True},
    )

    user_id: Optional[int] = Field(foreign_key="user.id")

    qtype: Optional[List[Literal["numeric", "multiple_choice"]]] = Field(
        default=None, sa_column=Column(JSON)
    )
    title: Optional[str] = Field(default=None)
    topic: Optional[List[str]] = Field(default=None, sa_column=Column(JSON))
    isAdaptive: Optional[Union[str, bool]] = Field(default=None, sa_column=Column(JSON))
    createdBy: Optional[str] = Field(default=None)
    language: Optional[Literal["python", "javascript"]] = Field(
        default=None, sa_column=Column(JSON)
    )
    ai_generated: Optional[bool] = Field(default=None)


# Probably Redundant But It Should Work meant for filtering
class QuestionDict(TypedDict, total=False):
    id: int
    user_id: int
    title: str
    qtype: str
    topic: str
    isAdaptive: Union[str,bool]
    language: List[str]
    createdBy: str
    ai_generated: bool

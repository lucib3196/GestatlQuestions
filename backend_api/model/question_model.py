from typing import List, Optional, Union, Literal, TypedDict
from uuid import UUID, uuid4
from ai_workspace.agents.question_to_json.models import QuestionBase, Solution
from sqlalchemy import Boolean, JSON, Column, text

from sqlmodel import SQLModel, Field, Relationship
from pydantic import BaseModel, Field as PydanticField
from .links import *
from .qtype_model import QType
from .language_model import Language
from .topic_model import Topic
from .file_model import File


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


class Question(SQLModel, table=True):
    __tablename__ = "question"  # type: ignore

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)

    title: Optional[str] = None
    ai_generated: Optional[bool] = None

    isAdaptive: bool = Field(
        default=True,
        sa_column=Column(Boolean, nullable=False, server_default=text("1")),
    )

    createdBy: Optional[str] = None
    user_id: Optional[int] = Field(foreign_key="user.id")

    # Relationships
    topics: List["Topic"] = Relationship(
        back_populates="questions",
        link_model=QuestionTopicLink,
    )

    languages: List["Language"] = Relationship(
        back_populates="questions",
        link_model=QuestionLanguageLink,
    )

    qtypes: List["QType"] = Relationship(
        back_populates="questions",
        link_model=QuestionQTypeLink,
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

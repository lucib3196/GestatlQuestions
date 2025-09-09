# Standard library
from datetime import datetime, timezone
from typing import List, Optional, Union, Literal
from uuid import UUID, uuid4

# Third-party libraries
from src.ai_workspace.models import QuestionBase
from pydantic import BaseModel, Field as PydanticField
from sqlalchemy import Boolean, Column, DateTime, func, text, UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel


# ----- Pydantic models -----
class CodeLanguage(BaseModel):
    language: Literal["python", "javascript"]


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


class QuestionMeta(BaseModel):
    id: Optional[UUID] = None
    title: Optional[str] = None
    ai_generated: Optional[bool] = None
    isAdaptive: Optional[bool] = None
    createdBy: Optional[str] = None
    user_id: Optional[int] = None
    topics: Optional[Union[List["TopicBase"], List["Topic"]]] = None
    languages: Optional[Union[List["LanguageBase"], List["Language"]]] = None
    qtypes: Optional[Union[List["QTypeBase"], List["QType"]]] = None

    class Config:
        from_attributes = True


class QuestionTopicLink(SQLModel, table=True):
    __tablename__ = "question_topic_link"  # type: ignore
    question_id: UUID = Field(foreign_key="question.id", primary_key=True)
    topic_id: UUID = Field(foreign_key="topic.id", primary_key=True)


class QuestionLanguageLink(SQLModel, table=True):
    __tablename__ = "question_language_link"  # type: ignore
    question_id: UUID = Field(foreign_key="question.id", primary_key=True)
    language_id: UUID = Field(foreign_key="language.id", primary_key=True)


class QuestionQTypeLink(SQLModel, table=True):
    __tablename__ = "question_qtype_link"  # type: ignore
    question_id: UUID = Field(foreign_key="question.id", primary_key=True)
    qtype_id: UUID = Field(foreign_key="qtype.id", primary_key=True)


class Language(SQLModel, table=True):
    __tablename__ = "language"  # type: ignore

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(index=True, unique=True)

    questions: List["Question"] = Relationship(
        back_populates="languages",
        link_model=QuestionLanguageLink,
    )


class QType(SQLModel, table=True):
    __tablename__ = "qtype"  # type: ignore

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(index=True, unique=True)

    questions: List["Question"] = Relationship(
        back_populates="qtypes",
        link_model=QuestionQTypeLink,
    )


class Topic(SQLModel, table=True):
    __tablename__ = "topic"  # type: ignore

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    name: str = Field(index=True, unique=True)

    questions: List["Question"] = Relationship(
        back_populates="topics",
        link_model=QuestionTopicLink,
    )


class Question(SQLModel, table=True):

    # Identity
    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    title: Optional[str] = Field(default=None, index=True)

    # === Cloud storage reference (Firebase Storage == GCS) ===
    bucket: Optional[str] = Field(default=None, index=True)
    blob_name: Optional[str] = Field(default=None, index=True)

    # Immutable / server metadata snapshot
    generation: Optional[str] = None
    size_bytes: Optional[int] = None
    content_type: Optional[str] = None
    md5_hash: Optional[str] = None
    storage_updated_at: Optional[datetime] = None  # set from GCS metadata when you save

    # Local convenience
    local_path: Optional[str] = None

    # Flags / ownership
    ai_generated: bool = Field(
        default=False,
        sa_column=Column(Boolean, nullable=False, server_default=text("0")),
    )
    isAdaptive: bool = Field(
        default=True,
        sa_column=Column(Boolean, nullable=False, server_default=text("1")),
    )
    createdBy: Optional[str] = None
    user_id: Optional[int] = Field(default=None, foreign_key="user.id", index=True)

    # Timestamps (Python default + DB server defaults)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=func.now(),  # DB will set if Python didn't
        ),
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(
            timezone.utc
        ),  # avoids required-arg issues
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=func.now(),  # initial value on insert
            onupdate=func.now(),  # auto-update on UPDATE
        ),
    )
    deleted_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )

    # Relationships
    topics: list["Topic"] = Relationship(
        back_populates="questions", link_model=QuestionTopicLink
    )
    languages: List["Language"] = Relationship(
        back_populates="questions", link_model=QuestionLanguageLink
    )
    qtypes: List["QType"] = Relationship(
        back_populates="questions", link_model=QuestionQTypeLink
    )

    __table_args__ = (
        UniqueConstraint("bucket", "blob_name", name="uq_question_bucket_blob"),
    )


class QTypeBase(BaseModel):
    name: str


class TopicBase(BaseModel):
    name: str


class LanguageBase(BaseModel):
    name: str

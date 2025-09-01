from typing import List, TYPE_CHECKING, Optional
from uuid import UUID, uuid4
from pydantic import BaseModel
from sqlmodel import SQLModel, Field, Relationship

from .links import QuestionQTypeLink

if TYPE_CHECKING:
    from .question_model import Question


class QTypeBase(BaseModel):
    name: str


class QType(SQLModel, table=True):
    __tablename__ = "qtype"  # type: ignore

    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(index=True, unique=True)

    questions: List["Question"] = Relationship(
        back_populates="qtypes",
        link_model=QuestionQTypeLink,
    )

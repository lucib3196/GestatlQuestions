from typing import TYPE_CHECKING, List
from typing import List
from uuid import UUID, uuid4

from sqlmodel import SQLModel, Field, Relationship
from .links import QuestionLanguageLink

if TYPE_CHECKING:
    from .question_model import Question


class Language(SQLModel, table=True):
    __tablename__ = "language"  # type: ignore

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(index=True, unique=True)

    questions: List["Question"] = Relationship(
        back_populates="languages",
        link_model=QuestionLanguageLink,
    )

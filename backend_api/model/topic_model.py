from typing import List, TYPE_CHECKING
from uuid import UUID, uuid4


from sqlmodel import SQLModel, Field, Relationship
from .links import QuestionTopicLink

if TYPE_CHECKING:
    from .question_model import Question


class Topic(SQLModel, table=True):
    __tablename__ = "topic"  # type: ignore

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(index=True, unique=True)

    questions: List["Question"] = Relationship(
        back_populates="topics",
        link_model=QuestionTopicLink,
    )

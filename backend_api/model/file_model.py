from typing import Optional, Union, TYPE_CHECKING
from uuid import UUID, uuid4
from sqlalchemy import JSON, Column

from sqlmodel import SQLModel, Field


if TYPE_CHECKING:
    from .question_model import Question


class File(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    filename: str
    content: Optional[Union[str, dict]] = Field(default=None, sa_column=Column(JSON))
    question_id: UUID = Field(foreign_key="question.id")

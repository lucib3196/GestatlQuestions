from pydantic import BaseModel
from typing import List
from src.api.models.models import Topic, QType, Language
from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from pydantic import BaseModel, Field
from typing import Sequence
from uuid import UUID


class QuestionBase(BaseModel):
    id: str | UUID | None = None
    title: Optional[str] = None
    ai_generated: Optional[bool] = None
    isAdaptive: Optional[bool] = None
    question_path: str | None = None
    model_config = ConfigDict(extra="ignore")


class QuestionMeta(QuestionBase):
    topics: List["Topic"] = Field(default_factory=list)
    languages: List["Language"] = Field(default_factory=list)
    qtypes: List["QType"] = Field(default_factory=list)


class QRelationshipData(BaseModel):
    topics: Sequence[str] = Field(default_factory=list)
    qtypes: Sequence[str] = Field(default_factory=list)
    languages: Sequence[str] = Field(default_factory=list)


class QuestionData(QuestionBase, QRelationshipData):
    pass

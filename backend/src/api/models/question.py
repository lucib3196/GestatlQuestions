from pydantic import BaseModel
from typing import List
from src.api.models.models import Topic, QType, Language


from typing import Optional, List
from pydantic import BaseModel, Field


class QuestionBase(BaseModel):
    title: Optional[str] = None
    ai_generated: Optional[bool] = None
    isAdaptive: Optional[bool] = None


class QuestionMeta(QuestionBase):
    topics: List["Topic"] = Field(default_factory=list)
    languages: List["Language"] = Field(default_factory=list)
    qtypes: List["QType"] = Field(default_factory=list)


class QRelationshipData(BaseModel):
    topics: List[str] = Field(default_factory=list)
    qtypes: List[str] = Field(default_factory=list)
    languages: List[str] = Field(default_factory=list)


class QuestionUpdate(QuestionBase, QRelationshipData):
    pass

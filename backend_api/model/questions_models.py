from pydantic import BaseModel, Field
from typing import List, Union, Optional, Literal
from ai_workspace.agents.question_to_json.models import (
    QuestionInput,
    Solution,
    QuestionBase,
)


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
    qtype: Optional[List[Literal["numeric", "multiple_choice"]]] = Field(default=None)
    title: str
    topic: List[str]
    relevantCourses: List[str]
    tags: Optional[List[str]] = []
    prereqs: Optional[List[str]] = []
    isAdaptive: Union[str, bool]
    createdBy: Optional[str] = ""
    language: Optional[List[str]] = []
    ai_generated: Optional[bool] = None

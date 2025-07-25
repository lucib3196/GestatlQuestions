from pydantic import BaseModel, Field
from typing import List, Union, Optional, Literal
from ai_workspace.agents.question_to_json.models import QuestionInput


class QuestionMeta(BaseModel):
    question: str
    title: str
    topic: List[str]
    relevant_courses: List[str]
    tags: List[str]
    prereqs: List[str]
    isAdaptive: Union[str, bool]


class QuestionRender(BaseModel):
    question_template: str
    questionInputs: List[QuestionInput]
    image: Optional[str]


class QuestionMetaNew(BaseModel):
    rendering_data: List[QuestionRender]
    qtype: Optional[Literal["numeric", "multiple_choice"]] = Field(default=None)
    title: str
    topic: List[str]
    relevantCourses: List[str]
    tags: List[str]
    prereqs: Optional[List[str]] = []
    isAdaptive: Union[str, bool]
    createdBy: Optional[str]
    language: Optional[List[str]] = []
    ai_generated: Optional[bool] = None

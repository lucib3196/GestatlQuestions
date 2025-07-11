from pydantic import BaseModel, Field
from typing import List, Union, Optional, Literal
from ai_workspace.question_to_json.models import QuestionInput


class QuestionMeta(BaseModel):
    question: str
    title: str
    topic: List[str]
    relevant_courses: List[str]
    tags: List[str]
    prereqs: List[str]
    isAdaptive: Union[str, bool]


class QuestionMetaNew(BaseModel):
    question_template: str
    qtype: Optional[Literal["numeric", "multiple_choice"]] = Field(default=None)
    image: Optional[str] = Field(default=None)
    questionInputs: List[QuestionInput]
    title: str
    topic: List[str]
    relevantCourses: List[str]
    tags: List[str]
    prereqs: Optional[List[str]] = []
    isAdaptive: Union[str, bool]

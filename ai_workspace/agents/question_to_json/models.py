from pydantic import BaseModel, Field
from typing import List, Union, Literal, Optional


c


class QuestionPayload(BaseModel):
    question: str
    questionBase: List[QuestionBase]
    title: str
    topic: List[str]
    relevantCourses: List[str]
    tags: List[str]
    isAdaptive: Union[str, bool]
    createdBy: Optional[str]


class Solution(BaseModel):
    solution_hint: List[str]

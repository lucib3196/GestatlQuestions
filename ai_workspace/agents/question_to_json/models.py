from pydantic import BaseModel, Field
from typing import List, Union, Literal, Optional


class BaseQuestionInput(BaseModel):
    name: str
    label: str
    qtype: Literal["number", "multiple_choice"]


class NumberInput(BaseQuestionInput):
    comparison: Literal["sigfig", "exact"]
    digits: Optional[int] = Field(default=3)
    units: Optional[str] = None


class MultipleChoiceOptions(BaseModel):
    name: str
    isCorrect: bool


class MultipleChoiceInput(BaseQuestionInput):
    options: List[MultipleChoiceOptions]


QuestionInput = Union[NumberInput, MultipleChoiceInput]


class QuestionBase(BaseModel):
    question_template: str = Field(..., description="The question")
    questionInputs: List[QuestionInput] = Field(
        ..., description="The inputs for the question ie what you are trying to solve"
    )
    image: Optional[str] = Field("filename of the image")


class QuestionPayload(BaseModel):
    question: str
    questionBase: List[QuestionBase]
    title: str
    topic: List[str]
    relevantCourses: List[str]
    tags: List[str]
    isAdaptive: Union[str, bool]
    createdBy: Optional[str]


# class QuestionPayload(BaseModel):
#     question_template: str
#     questionInputs: List[QuestionInput]
#     title: str
#     topic: List[str]
#     relevantCourses: List[str]
#     tags: List[str]
#     isAdaptive: Union[str, bool]
#     createdBy: Optional[str]

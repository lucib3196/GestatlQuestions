from typing import Any, Optional, List, Union, Literal

from pydantic import BaseModel, Field

from .generic import Section


# -------------------------------------------------------------------
# Files Data Model
# -------------------------------------------------------------------
class FilesData(BaseModel):
    """Holds the generated file contents related to a question."""

    question_html: str = ""
    server_js: str = ""
    server_py: str = ""
    solution_html: str = ""
    metadata: dict[str, Any] = {}


# -------------------------------------------------------------------
# Parameters
# -------------------------------------------------------------------
class ParamBase(BaseModel):
    name: str
    value: Union[int, float, str]
    units: Optional[str] = None

    def format_name(self) -> str:
        """Normalize name to snake_case."""
        self.name = self.name.lower().strip().replace(" ", "_")
        return self.name

    def format_expected(self) -> str:
        """Return a formatted string with name, value, and optional units."""
        formatted = f"Value Name: {self.format_name()} Value: {self.value}"
        if self.units:
            formatted += f" Units: {self.units}"
        return formatted


# -------------------------------------------------------------------
# Solution
# -------------------------------------------------------------------
class Solution(BaseModel):
    solution: List[Section] = Field(
        default_factory=list,
        title="Titles and descriptions for each solution step",
        description=(
            "The solution guide of the question. "
            "Any math should be delimited by $$ for block level and $ for inline."
        ),
    )
    source: Literal["ai_generate", "image_extraction", "user_provided"]


# -------------------------------------------------------------------
# Question
# -------------------------------------------------------------------
class Question(BaseModel):
    question: str = Field(
        ...,
        title="Question",
        description="A fully formed question. It should be complete and clearly stated.",
    )
    params: Optional[List[ParamBase]] = Field(
        default=None,
        description="A parameter found in the question text",
    )
    correct_answers: Optional[List[ParamBase]] = None
    source: Optional[Union[str, int]] = Field(
        default=None,
        title="Source",
        description=(
            "The source from which the question was extracted. "
            "Ideally, this is a page number or identifier from lecture content or a textbook."
        ),
    )
    requires_external_data: Optional[bool] = Field(
        default=None,
        title="Requires External Data",
        description="Whether the question depends on external data such as tables, charts, or datasets to be solved.",
    )
    requires_image: Optional[bool] = Field(
        default=None,
        title="Requires Image",
        description="Whether an image is required to fully understand the question.",
    )
    completeness: Optional[bool] = Field(
        default=None,
        title="Completeness",
        description="Whether the question or derivation is complete or requires additional steps.",
    )
    additional_information: Optional[str] = Field(
        default=None,
        title="Additional instructions for code generation",
        description="Additional instructions for code generation",
    )
    solution: Optional[Solution] = None

    @property
    def as_str(self) -> str:
        """Return question text with source and solution steps as a single string."""
        solution_steps = (
            "\n\n".join(step.as_str for step in self.solution.solution)
            if self.solution
            else None
        )
        source = f"\nSource: {self.source}" if self.source else ""
        return f"{self.question}\n{source}\n\n{solution_steps}".strip()

    @property
    def solution_as_str(self) -> str:
        """Return only solution steps as string."""
        return (
            "\n\n".join(step.as_str for step in self.solution.solution)
            if self.solution
            else ""
        )

    @property
    def format_params(self) -> str:
        """Format parameters and correct answers into strings with type labels."""
        lines = []
        for param in self.params or []:
            result = param.format_expected()
            lines.append(f"{result} Value Type: Question Parameter")
        for ans in self.correct_answers or []:
            result = ans.format_expected()
            lines.append(f"{result} Value Type: Correct Answer")
        return "\n\n".join(lines)


# -------------------------------------------------------------------
# Question Inputs
# -------------------------------------------------------------------
class BaseQuestionInput(BaseModel):
    name: str
    label: str
    qtype: Literal["number", "multiple_choice"]


class NumberInput(BaseQuestionInput):
    comparison: Literal["sigfig", "exact"]
    digits: Optional[int] = Field(default=3)
    units: Optional[str] = None


class NumberInputStatic(NumberInput):
    correct_answer: int | float


class MultipleChoiceOptions(BaseModel):
    name: str
    isCorrect: bool


class MultipleChoiceInput(BaseQuestionInput):
    options: List[MultipleChoiceOptions]


QuestionInput = Union[NumberInput, MultipleChoiceInput, NumberInputStatic]


# -------------------------------------------------------------------
# Question Base
# -------------------------------------------------------------------
class QuestionBase(BaseModel):
    question_template: str = Field(..., description="The question")
    questionInputs: List[QuestionInput] = Field(
        ...,
        description="The inputs for the question, i.e. what you are trying to solve",
    )
    image: Optional[str] = Field("filename of the image")
    solution_render: Optional[List[str]] = None

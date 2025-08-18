from pydantic import BaseModel, Field
from typing import Any, Optional, List, Union
from .generic import Section
from typing import Literal


# --- Files Data Model ---
class FilesData(BaseModel):
    """Holds the generated file contents related to a question."""

    question_html: str = ""
    server_js: str = ""
    server_py: str = ""
    solution_html: str = ""
    metadata: dict[str, Any] = {}


class ParamBase(BaseModel):
    name: str
    value: Union[int, float, str]
    units: Optional[str] = None

    def format_name(self) -> str:
        self.name = self.name.lower().strip().replace(" ", "_")
        return self.name

    def format_expected(self) -> str:
        formatted = "Value Name:" + self.format_name() + " Value: " + str(self.value)
        if self.units:
            unit_str = f" Units: {self.units}"
            formatted += unit_str
        return formatted


class Solution(BaseModel):
    solution: List[Section] = Field(
        default_factory=list,
        title="Titles and descriptions for each solution step",
        description="The solution guide of the question any math should be delimited by $$ for block level and $ for inline ",
    )
    source: Literal["ai_generate", "image_extraction", "user_provided"]


class Question(BaseModel):
    question: str = Field(
        ...,
        title="Question",
        description="A fully formed question. It should be complete and clearly stated.",
    )
    params: Optional[List[ParamBase]] = Field(
        description="A parameter found in the question text", default=None
    )
    correct_answers: Optional[List[ParamBase]] = None
    source: Optional[Union[str, int]] = Field(
        None,
        title="Source",
        description="The source from which the question was extracted. Ideally, this is a page number or identifier from lecture content or a textbook.",
    )
    requires_external_data: Optional[bool] = Field(
        None,
        title="Requires External Data",
        description="Whether the question depends on external data such as tables, charts, or datasets to be solved.",
    )
    requires_image: Optional[bool] = Field(
        None,
        title="Requires Image",
        description="Whether an image is required to fully understand the question.",
    )
    completeness: Optional[bool] = Field(
        None,
        title="Completeness",
        description="Whether the question or derivation is complete or requires additional steps.",
    )
    additional_information: Optional[str] = Field(
        None,
        title="Additional instructions for code generation",
        description="Additional instructiosn for code generation",
    )
    solution: Optional[Solution] = None

    @property
    def as_str(self) -> str:
        solution_steps = (
            "\n\n".join(solution.as_str for solution in self.solution.solution)
            if self.solution
            else None
        )
        source = f"\nSource: {self.source}" if self.source else ""
        return f"{self.question}\n{source}\n\n{solution_steps}".strip()

    @property
    def solution_as_str(self) -> str:
        return (
            "\n\n".join(solution.as_str for solution in self.solution.solution)
            if self.solution
            else ""
        )

    @property
    def format_params(self) -> str:
        lines = []
        for param in self.params or []:
            result = param.format_expected()
            if result is not None:
                lines.append(str(result + f" Value Type: Question Parameter"))
        for ans in self.correct_answers or []:
            result = ans.format_expected()
            if result is not None:
                lines.append(str(result + f" Value Type: Correct Answer"))
        return "\n\n".join(lines)

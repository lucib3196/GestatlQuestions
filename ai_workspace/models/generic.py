from pydantic import BaseModel, Field
from typing import List,Literal,Optional


class QueryList(BaseModel):
    queries: List[str] = Field(..., description="Search queries")


# General Models for Creating Sections and Subsections
class Subsection(BaseModel):
    subsection_title: str = Field(..., title="Title of the subsection")
    description: str = Field(..., title="Content of the subsection")

    @property
    def as_str(self) -> str:
        return f"### {self.subsection_title}\n\n{self.description}".strip()


class Section(BaseModel):
    section_title: str = Field(..., title="Title of the section")
    description: str = Field(..., title="Content of the section")
    subsections: Optional[List[Subsection]] = Field(
        default=None,
        title="Titles and descriptions for each subsection."
    )

    @property
    def as_str(self) -> str:
        subsections = "\n\n".join(
            f"### {subsection.subsection_title}\n\n{subsection.description}"
            for subsection in self.subsections or []
        )
        return f"## {self.section_title}\n\n{self.description}\n\n{subsections}".strip()


class BinaryScore(BaseModel):
    binary_score: Literal["yes", "no"]

class CodeResponse(BaseModel):
    """Output schema from the LLM for code generation."""

    code: str = Field(..., description="The generated code. Only return the code.")

from pydantic import BaseModel, Field
from typing import Any, Literal, List, Optional


class HtmlTag(BaseModel):
    name: Literal["div", "p", "form", "input", "label", "fieldset", "legend"] = Field(
        ...,
        description="The name of the HTML tag (e.g., 'input', 'label', or 'fieldset').",
    )
    attributes: dict[str, str] = Field(
        ...,
        description="A dictionary of HTML attributes to apply to the tag (e.g., 'class', 'type', 'id').",
    )
    mapping: dict[str, str] = Field(
        ...,
        description="A mapping of HTML tag attribute names to their corresponding replacements or aliases.",
    )


class Config(BaseModel):
    separate_forms_per_input: bool = Field(
        default=False,
        description="If True, each input is wrapped in its own <form>. If False, all inputs are placed in a single shared form.",
    )
    path_image: Optional[str] = Field(default=None, description="The path for images")


class TagConfig(BaseModel):
    target_tag: str = Field(
        ...,
        description="The name of the tag in the original content that should be transformed.",
    )
    render_role: Literal["input", "decorative", "other"]
    mapping: List[HtmlTag] = Field(
        ...,
        description="A list of HtmlTag objects defining how the target_tag should be replaced or rendered.",
    )
    example: Optional[str] = Field(
        ...,
        description="An example snippet showing how the target_tag is used in context.",
    )

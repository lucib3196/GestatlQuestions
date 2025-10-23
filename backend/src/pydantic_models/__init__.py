from pydantic import BaseModel, Field

class PageRange(BaseModel):
    start_page: int = Field(
        ..., description="Page number where the section or reference begins."
    )
    end_page: int = Field(
        ..., description="Page number where the section or reference ends."
    )

from typing import Union, Optional, List
from pydantic import BaseModel, field_validator
from src.api.models.file_model import File


class SuccessFileResponse(BaseModel):
    status: Union[str, int]
    detail: Optional[str] = None
    file_obj: List[File]

    @field_validator("file_obj", mode="before")
    def ensure_list(cls, v):
        if isinstance(v, File):
            return [v]
        return v

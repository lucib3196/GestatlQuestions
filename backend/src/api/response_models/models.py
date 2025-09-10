from typing import Union, Optional, List, Any
from pydantic import BaseModel, field_validator
from src.api.models.file_model import File


class FileData(BaseModel):
    filename: str
    content: dict | str | Any


class FilesData(BaseModel):
    files: List[FileData]


class SuccessfulResponse(BaseModel):
    """Base success response shared by all API responses."""

    status: int  # keep this strict (HTTP status codes are int)
    detail: str


class SuccessDataResponse(SuccessfulResponse):
    """Success response with a file system path included."""

    data: str | None


class SuccessFileResponse(SuccessfulResponse):
    """Success response with one or more file objects."""

    files: List[FileData] | List[File] | List[str]

    @field_validator("files", mode="before")
    def ensure_list(cls, v):
        """Always coerce single File into a list of File objects."""
        if v is None:
            return []
        if isinstance(v, File):
            return [v]
        return v

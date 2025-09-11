# --- Standard Library ---
from pathlib import Path
from typing import Any, List, Optional, Union
from uuid import UUID

# --- Third-Party ---
from pydantic import BaseModel, Field, field_validator

# --- Internal ---
from src.api.models.file_model import File
from src.api.models.question_model import QuestionMeta


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

    files: List[FileData] | List[str] = []
    file_paths: List[str] | List[Path] = []

    @field_validator("files", mode="before")
    def ensure_list(cls, v):
        """Always coerce single File into a list of File objects."""
        if v is None:
            return []
        if isinstance(v, File):
            return [v]
        return v


class Response(BaseModel):
    status: int
    detail: str


class QuestionReadResponse(BaseModel):
    status: int
    question: QuestionMeta
    files: List[FileData] | List[str] = []
    detail: str


class UpdateFile(BaseModel):
    question_id: str | UUID
    filename: str
    new_content: str | dict


class AdditionalQMeta(BaseModel):
    topics: Optional[List[str]] = None
    languages: Optional[List[str]] = None
    qtype: Optional[List[str]] = None

from typing import List, Sequence

from src.api.models.models import Question
from src.api.models import *
from typing import Literal

from typing import Sequence


SyncStatus = Literal[
    "missing_metadata",  # metadata.json not found
    "invalid_metadata_json",  # JSON decode error
    "missing_id",  # ID field not found in metadata
    "not_in_database",  # Metadata ID not found in DB
    "invalid question schema",  # Question model is invalide
    "failed to create question",
    "success",  # Sync Status was successful
]


class UnsyncedQuestion(BaseModel):
    question_name: str
    question_path: str
    detail: str
    status: SyncStatus
    metadata: str | None


class SyncMetrics(BaseModel):
    total_found: int
    synced: int
    failed: int


class SyncResponse(BaseModel):
    metrics: SyncMetrics
    synced_questions: Sequence["Question"]
    skipped_questions: List["UnsyncedQuestion"]
    failed_questions: List[str]  # store file name or reason


class FolderCheckMetrics(BaseModel):
    total_checked: int
    deleted_from_db: int
    still_valid: int
    bug: int | None = None


class FolderCheckResponse(BaseModel):
    metrics: FolderCheckMetrics
    remaining_questions: Sequence[Question]

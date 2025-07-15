from pydantic import BaseModel
from typing import Any
# --- Files Data Model ---
class FilesData(BaseModel):
    """Holds the generated file contents related to a question."""

    question_html: str = ""
    server_js: str = ""
    server_py: str = ""
    solution_html: str = ""
    metadata: dict[str, Any] = {}
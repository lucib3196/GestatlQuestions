from pathlib import Path
from typing import Union, List
import os
from src.utils import safe_dir_name
from src.api.core import logger


class DirectoryService:
    """Responsible only for path creation, validation and cleanup"""

    def __init__(self, base_dir: Union[str, Path] = "questions"):
        self.base_dir = Path(base_dir).resolve()

    def ensure_base_exist(self) -> None:
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def get_question_dir(self, question_identifier: str) -> Path:
        return self.base_dir / safe_dir_name(str(question_identifier))

    def set_directory(self, question_identifier: str, relative: bool = True) -> Path:
        q_dir = self.get_question_dir(question_identifier)
        q_dir.mkdir(parents=True, exist_ok=True)
        if relative:
            return q_dir.relative_to(self.base_dir)
        else:
            return q_dir

    def get_file(self, question_identifier: str, filename: str) -> Path | None:
        target = self.get_question_dir(question_identifier) / filename
        if target.exists() and target.is_file():
            logger.info("File found: %s", target)
            return target
        logger.warning("File not found: %s", target)
        return None

    def list_file_paths(self, question_identifier: str) -> List[Path]:
        q_dir = self.get_question_dir(question_identifier)
        if not q_dir.exists():
            return []
        return [f for f in q_dir.iterdir() if f.is_file]

    def list_files_names(self, question_identifier: str) -> List[str]:
        return [f.name for f in self.list_file_paths(question_identifier)]

    def remove_question_dir(self, question_id: str) -> None:
        """Remove an entire question directory (use with caution)."""
        q_dir = self.get_question_dir(question_id)
        if q_dir.exists():
            for f in q_dir.iterdir():
                if f.is_file():
                    f.unlink()
            os.rmdir(q_dir)

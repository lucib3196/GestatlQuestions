# --- Standard Library ---
import json
from pathlib import Path
from typing import List, Union

# --- Internal ---
from .base import StorageService
from src.api.service.storage.directory_service import DirectoryService


class LocalStorageService(StorageService):
    def __init__(self, base_path: str | Path):
        self.dir_service = DirectoryService(base_path)
        self.dir_service.ensure_base_exist()

    def create_directory(self, identifier) -> Path:
        return self.dir_service.set_directory(identifier, relative=False)

    def save_file(
        self,
        identifier: str,
        filename: str,
        content: Union[str, dict, list, bytes, bytearray],
        overwrite: bool = True,
    ) -> Path:
        file_path = self.dir_service.get_question_dir(identifier) / filename

        if not overwrite and file_path.exists():
            raise ValueError(f"Cannot overwrite file {file_path}")

        if isinstance(content, (dict, list)):
            file_path.write_text(json.dumps(content, indent=2))
        elif isinstance(content, (bytes, bytearray)):
            mode = "wb" if overwrite else "xb"
            with open(file_path, mode) as f:
                f.write(content)
        else:
            file_path.write_text(str(content))

        return file_path

    def get_file(self, identifier: str, filename: str) -> bytes | None:
        file_path = self.dir_service.get_file(identifier, filename)
        if file_path and file_path.exists():
            return file_path.read_bytes()
        return None

    def get_files_names(self, identifier: str) -> list[str]:
        return self.dir_service.list_files_names(identifier)

    def get_files_paths(self, identifier: str) -> List[Path]:
        return self.dir_service.list_file_paths(identifier)

    def delete_file(self, identifier: str, filename: str) -> None:
        file_path = self.dir_service.get_file(identifier, filename)
        if file_path and file_path.exists():
            file_path.unlink()

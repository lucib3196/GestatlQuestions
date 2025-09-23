# --- Standard Library ---
import json
from pathlib import Path
from typing import List, Union
import shutil

# --- Internal ---
from .base import StorageService
from src.api.service.storage.directory_service import DirectoryService


class LocalStorageService(StorageService):
    def __init__(self, base_name: str | Path):
        self.dir_service = DirectoryService(base_name)
        self.dir_service.ensure_base_exist()
        self.base_dir = self.dir_service.base_dir

    def get_directory(self, identifier: str) -> Path:
        return self.dir_service.get_question_dir(identifier)

    def create_directory(self, identifier) -> Path:
        return self.dir_service.set_directory(identifier, relative=False)

    def get_filepath(self, identifier: str, filename: str) -> Path:
        return super().get_filepath(identifier, filename)

    def does_directory_exist(self, identifier: str) -> bool:
        return self.get_directory(identifier).exists()

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

    def delete_all(self, identifier: str) -> None:
        dir = self.get_directory(identifier)
        if dir.exists() and dir.is_dir():
            shutil.rmtree(dir)

# --- Standard Library ---
import json
from pathlib import Path
from typing import List, Union
import shutil

# --- Internal ---
from .base import StorageService
from src.api.service.storage.directory_service import DirectoryService
from fastapi.responses import StreamingResponse
import io, zipfile, pathlib
from src.api.core import logger
from src.api.service.file_handler import FileService


class LocalStorageService(StorageService):
    """
    Local storage implementation of StorageService.

    Handles file operations (create, save, delete, download) on the local filesystem.
    Uses DirectoryService for directory management and FileService for file zipping.
    """

    # --- Init / Lifecycle ---

    def __init__(self, base_name: str | Path):
        """Initialize the LocalStorageService with a base directory."""
        self.dir_service = DirectoryService(base_name)
        self.dir_service.ensure_base_exist()
        self.base_dir: Path = self.dir_service.base_dir
        download_path = self.base_dir / "downloads"
        self.file_service = FileService(download_path)

    # --- Directory Management ---

    def get_basename(self) -> str | Path:
        return self.base_dir

    def get_directory(self, identifier: str) -> Path:
        """Return the directory path for a given identifier."""
        return self.dir_service.get_question_dir(identifier)

    def create_directory(self, identifier: str) -> Path:
        """Create a directory for the given identifier."""
        return self.dir_service.set_directory(identifier, relative=False)

    def does_directory_exist(self, identifier: str) -> bool:
        """Check whether a directory exists for the given identifier."""
        return self.get_directory(identifier).exists()

    # --- File Access ---

    def get_filepath(self, identifier: str, filename: str) -> Path:
        """Return the full file path for a given identifier and filename."""
        return super().get_filepath(identifier, filename)

    def save_file(
        self,
        identifier: str,
        filename: str,
        content: Union[str, dict, list, bytes, bytearray],
        overwrite: bool = True,
    ) -> Path:
        """Save a file to the given identifier's directory."""
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
        """Retrieve a file's contents if it exists."""
        file_path = self.dir_service.get_file(identifier, filename)
        if file_path and file_path.exists():
            return file_path.read_bytes()
        return None

    def get_files_names(self, identifier: str) -> list[str]:
        """Return the names of all files under the given identifier directory."""
        return self.dir_service.list_files_names(identifier)

    def get_files_paths(self, identifier: str) -> List[Path]:
        """Return the full paths of all files under the given identifier directory."""
        return self.dir_service.list_file_paths(identifier)

    # --- File Deletion ---

    def delete_file(self, identifier: str, filename: str) -> None:
        """Delete a file under the given identifier directory."""
        file_path = self.dir_service.get_file(identifier, filename)
        if file_path and file_path.exists():
            file_path.unlink()

    def delete_all(self, identifier: str) -> None:
        """Delete all files under the given identifier directory."""
        dir_path = self.get_directory(identifier)
        if dir_path.exists() and dir_path.is_dir():
            shutil.rmtree(dir_path)

    def hard_delete(self) -> None:
        """Delete the entire storage (not implemented in LocalStorageService)."""
        return super().hard_delete()

    # --- Download Helpers ---

    async def download_question(self, identifier: str) -> bytes:
        """
        Bundle all files for a given identifier into a zip archive (in-memory).
        """
        logger.debug("Attempting to download questions")
        files = self.get_files_paths(identifier)
        logger.debug(f"Preparing download for {identifier}")
        return await self.file_service.download_zip(files, folder_name=identifier)

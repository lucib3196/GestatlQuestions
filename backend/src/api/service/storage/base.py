from abc import ABC, abstractmethod
from pathlib import Path
from typing import Union
from google.cloud.storage.blob import Blob


class StorageService:
    """Base storage interface. Subclasses may override methods they need."""

    def get_basename(self) -> str | Path:
        raise NotImplementedError("get_basename must be implemented by subclass")

    def get_directory(self, identifier: str) -> Path:
        raise NotImplementedError("get_directory must be implemented by subclass")

    def create_directory(self, identifier: str) -> Path | Blob:
        raise NotImplementedError("create_directory must be implemented by subclass")

    def does_directory_exist(self, identifier: str) -> bool:
        raise NotImplementedError(
            "does_directory_exist must be implemented by subclass"
        )

    def get_filepath(self, identifier: str, filename: str) -> Path:
        raise NotImplementedError("get_filepath must be implemented by subclass")

    def save_file(
        self,
        identifier: str,
        filename: str,
        content: Union[str, dict, list, bytes, bytearray],
        overwrite: bool = True,
    ) -> Path:
        raise NotImplementedError("save_file must be implemented by subclass")

    def get_file(self, identifier: str, filename: str) -> bytes | None:
        raise NotImplementedError("get_file must be implemented by subclass")

    def get_files_names(self, identifier: str) -> list[str]:
        raise NotImplementedError("get_files_names must be implemented by subclass")

    def delete_file(self, identifier: str, filename: str) -> None:
        raise NotImplementedError("delete_file must be implemented by subclass")

    def delete_all(self, identifier: str) -> None:
        raise NotImplementedError("delete_all must be implemented by subclass")

    def hard_delete(self) -> None:
        raise NotImplementedError("hard_delete must be implemented by subclass")

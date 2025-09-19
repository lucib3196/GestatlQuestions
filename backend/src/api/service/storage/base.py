from abc import ABC, abstractmethod
from pathlib import Path
from typing import Union


class StorageService(ABC):
    """Abstract storage interface. All storage backends must implement these."""

    @abstractmethod
    def save_file(
        self,
        identifier: str,
        filename: str,
        content: Union[str, dict, list, bytes, bytearray],
        overwrite: bool = True,
    ) -> Path:
        pass

    @abstractmethod
    def get_file(self, identifier: str, filename: str) -> bytes | None:
        pass

    @abstractmethod
    def get_files_names(self, identifier: str) -> list[str]:
        pass

    @abstractmethod
    def delete_file(self, identifier: str, filename: str) -> None:
        pass

from abc import ABC, abstractmethod
from pathlib import Path


class EncoderBase(ABC):

    @abstractmethod
    def encode_base64(self, path: str | Path) -> str:
        """Convert input data into encoded form."""
        pass

    @abstractmethod
    def decode_base64(self, encoded_str: str, output_path: str | Path) -> Path:
        """Convert input data into encoded form."""
        pass

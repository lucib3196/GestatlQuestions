from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Literal, Dict
from typing import Sequence

MimeType = Literal["image/png", "image/jpeg", "application/pdf"]


class EncoderBase(ABC):

    @abstractmethod
    def encode_base64(self, path: str | Path | bytes) -> str:
        """Convert input data into encoded form."""
        pass

    @abstractmethod
    def decode_base64(self, encoded_str: str, output_path: str | Path) -> Path:
        """Convert input data into encoded form."""
        pass

    @abstractmethod
    def prepare_llm_payload(
        self, paths: Sequence[str | Path | bytes]
    ) -> List[Dict[str, str]]:
        pass

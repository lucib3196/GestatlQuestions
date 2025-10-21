from pathlib import Path
import base64
from .EncoderBase import EncoderBase


class ImageEncoder(EncoderBase):
    def __init__(self):
        pass

    def encode_base64(self, path: str | Path) -> str:
        path = Path(path).resolve()
        if not path.exists():
            raise ValueError(f"Image path {path} not found")
        bytes = path.read_bytes()
        encoded = base64.b64encode(bytes).decode("utf-8")
        return encoded

    def decode_base64(self, encoded_str: str, output_path: str | Path) -> Path:
        output_path = Path(output_path).resolve()
        bytes = base64.b64decode(encoded_str.encode("utf-8"))
        output_path.write_bytes(bytes)
        return output_path

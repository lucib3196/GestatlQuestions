from pathlib import Path
import base64
from typing import List
from .EncoderBase import EncoderBase, MimeType
from typing import Literal


class ImageEncoder(EncoderBase):
 

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

    def prepare_llm_payload(self, paths: List[str | Path]):
        encoded_payload = [
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{self.encode_base64(p)}"},
            }
            for p in paths
        ]
        return encoded_payload


if __name__ == "__main__":
    image_path = Path(r"src\app_test\test_assets\images\test_image.png")
    paylod = ImageEncoder().prepare_llm_payload(
        paths=[image_path], 
    )

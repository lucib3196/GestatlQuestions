from typing import Union
from pathlib import Path

def normalize_path(path: Union[str, Path] | None) -> Path:
    if path is None:
        raise ValueError("No path provided")

    if isinstance(path, str):
        s = path.strip()
        if not s:
            raise ValueError("Empty path string")
        return Path(s)

    if isinstance(path, Path):
        return path

    raise TypeError(f"Unsupported path type: {type(path).__name__}")
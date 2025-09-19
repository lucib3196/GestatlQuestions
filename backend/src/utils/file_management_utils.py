import re
from pathlib import Path

_filename_safe_re = re.compile(r"[^A-Za-z0-9._-]+")


def safe_dir_name(name: str, max_length: int = 100) -> str:
    name = Path(name).name
    name = name.strip().replace(" ", "_")
    name = name = _filename_safe_re.sub("-", name)
    if not name or name.startswith("."):
        raise ValueError("Could not generate safe name")
    if len(name) > max_length:
        name = name[:max_length]
    return name

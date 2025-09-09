import re

_filename_safe_re = re.compile(r"[^A-Za-z0-9._-]+")


def safe_name(name: str) -> str:
    name = name.strip().replace(" ", "_")
    name = name = _filename_safe_re.sub("-", name)
    if not name or name.startswith("."):
        raise ValueError("Could not generate safe name")
    return name

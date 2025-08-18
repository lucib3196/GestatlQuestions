from typing import Any
from typing import Optional
_TRUE = {"true", "1", "yes", "y", "on", "t"}
_FALSE = {"false", "0", "no", "n", "off", "f"}


def to_bool(v: Any, *, default: bool | None = None) -> bool:
    if isinstance(v, bool):
        return v
    if v is None:
        if default is None:
            raise ValueError("isAdaptive is missing")
        return default
    if isinstance(v, (int, float)) and v in (0, 1):
        return bool(v)
    if isinstance(v, str):
        s = v.strip().lower()
        if s in _TRUE:
            return True
        if s in _FALSE:
            return False
    raise ValueError(f"Cannot interpret {v!r} as boolean")

def _normalize_topic_name(name: Optional[str]) -> Optional[str]:
    if not name:
        return None
    s = name.strip()
    return s or None
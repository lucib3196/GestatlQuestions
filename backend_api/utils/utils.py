from typing import Any
from typing import Optional
from typing import List, Sequence, Union, Iterable, Optional

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


def normalize_names(items: Iterable[str]) -> List[str]:
    return [s.strip().lower() for s in items if isinstance(s, str) and s.strip()]

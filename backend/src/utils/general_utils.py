from typing import Any, Iterable, List, Optional, Sequence, Union
from typing import Any

_TRUE = {"true", "1", "yes", "y", "on", "t"}
_FALSE = {"false", "0", "no", "n", "off", "f"}


def normalize_values(vals: Iterable) -> List[Any]:
    """Normalize values by stripping whitespace from strings and removing Nones."""
    out = []
    for v in vals:
        if v is None:
            continue
        if isinstance(v, str):
            s = v.strip().lower()
            if not s:
                continue
            out.append(s)
        else:
            out.append(v)
    return out


def normset(seq):
    return {s.strip().lower() for s in seq}


def names(objs):
    return {o.name for o in objs}


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


def to_list(value: Any):
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, (set, tuple, Iterable)):
        return list(value)
    else:
        return [value]


def pick(obj, *keys, default=None):
    """
    Get the first present key/attr from `keys` on either a dict or an object.
    """
    for k in keys:
        if isinstance(obj, dict):
            if k in obj:
                return obj[k]
        else:
            if hasattr(obj, k):
                return getattr(obj, k)
    return default

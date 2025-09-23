# --- Standard Library ---
import json
from typing import Any, Iterable, List, Optional, Sequence, Type

# --- Third-Party ---
from pydantic import BaseModel

# --- Constants ---
_TRUE = {"true", "1", "yes", "y", "on", "t"}
_FALSE = {"false", "0", "no", "n", "off", "f"}


# --- Conversion Utilities ---
def to_bool(v: Any, *, default: Optional[bool] = None) -> bool:
    """
    Convert a value to boolean.

    Accepts booleans, numbers (0/1), and string variants.
    Raises ValueError if the value cannot be interpreted.
    """
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


def to_list(value: Any) -> list[Any]:
    """Ensure the value is returned as a list."""
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, (set, tuple, Iterable)):
        return list(value)
    return [value]


def normalize_json_content(value: Any) -> Any:
    """
    Normalize JSON-like content.

    If the value is a string, attempt to parse as JSON.
    Returns the original string if parsing fails.
    """
    if isinstance(value, str):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value
    return value


def serialized_to_dict(data: Any, obj: Type[BaseModel]) -> dict:
    """
    Normalize arbitrary input into a dictionary.

    Accepts a JSON string, a Pydantic model instance, or a dict.
    Returns a standardized `dict` representation.
    """
    if isinstance(data, str):
        return json.loads(data)
    if isinstance(data, obj):
        return data.model_dump()
    if isinstance(data, dict):
        return data
    raise ValueError(f"Could not normalize data received {data} of type {type(data)}")

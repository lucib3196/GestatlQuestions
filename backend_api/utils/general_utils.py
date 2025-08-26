from typing import Iterable, List, Optional
from typing import Any


def normalize_values(vals: Iterable) -> List[Any]:
    """_summary_

    Args:
        vals (Iterable): A list of values

    Returns:
        List[Any]: Normalizes values by stripping white space out of strings
        and removing none values.
    """
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
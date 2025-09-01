# Stdlib
from typing import Any, Dict, List, Union
from uuid import UUID

# Third-party
from pydantic import BaseModel
from sqlalchemy import String, cast, func
from sqlalchemy.inspection import inspect
from sqlalchemy.orm.exc import UnmappedInstanceError
from sqlalchemy.orm.properties import RelationshipProperty
from sqlmodel import select

# Internal
from backend_api.data.database import SessionDep


def get_uuid(val: Union[str, UUID]) -> UUID:
    """Validate and convert a question_id to UUID or raise HTTP 400."""
    try:
        if isinstance(val, UUID):
            return val
        else:
            return UUID(val)
    except Exception as e:
        raise ValueError("Could not convert id to UUID")


def is_relationship(model: type, attr_name: str) -> bool:
    """True if model.attr_name is a relationship."""
    try:
        prop = inspect(model).get_property(attr_name)
        return isinstance(prop, RelationshipProperty)
    except UnmappedInstanceError:
        return False


def pick_related_label_col(target_cls):
    """
    Try to pick a 'label' column on the related class for string lookups.
    Preference: .name -> .title -> first String column -> primary key.
    """
    if hasattr(target_cls, "name"):
        return getattr(target_cls, "name")
    if hasattr(target_cls, "title"):
        return getattr(target_cls, "title")


def string_condition(col, raw_val: str, partial: bool = True):
    """
    Case-insensitive string filter. If partial=True, uses ILIKE %v%,
    else equality on lower().
    """
    if partial:
        return func.lower(cast(col, String)).like(f"%{raw_val.lower()}%")
    return func.lower(cast(col, String)) == raw_val.lower()


def resolve_or_create(
    session: SessionDep,
    target_cls,
    value,
    create_field: bool = True,
    lookup_field: str = "name",
):
    stmt = select(target_cls).where(
        func.lower(getattr(target_cls, lookup_field)) == value.lower().strip()
    )
    result = session.exec(stmt).first()
    if result:
        return result
    if create_field:
        obj = target_cls(**{lookup_field: value.lower().strip()})
        session.add(obj)
        session.commit()
        session.refresh(obj)
        return obj
    else:
        return None


def get_model_relationship_data(model, relationships: List[str]):
    if not hasattr(model, "model_dump"):
        raise ValueError("Must be valid model")
    data: Dict[str, Any] = model.model_dump(exclude_none=True)
    for rel in relationships:
        value = getattr(model, rel, None)
        if value is None:
            data[rel] = None

        # Relationship lists (InstrumentedList behaves like list)
        elif hasattr(value, "__iter__") and not isinstance(value, (str, bytes)):
            data[rel] = [
                (
                    item.model_dump(exclude_none=True)
                    if hasattr(item, "model_dump")
                    else item
                )
                for item in value
            ]
        # Single related object
        elif not hasattr(value, "__iter__") and isinstance(value, BaseModel):
            data[rel] = (
                value.model_dump(exclude_none=True)
                if hasattr(value, "model_dump")
                else value
            )
    return data


def normalize_kwargs(kwargs: dict):
    normalized = {}
    for key, value in kwargs.items():
        if isinstance(value, list):
            f = [v.get("name") for v in value if isinstance(v, dict)]
            normalized[key] = f
        else:
            normalized[key] = value
    return normalized

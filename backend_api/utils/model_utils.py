from sqlalchemy.inspection import inspect
from sqlalchemy.orm.exc import UnmappedInstanceError
from sqlalchemy.orm.properties import RelationshipProperty
from sqlalchemy import func, cast, String
from sqlalchemy.orm.properties import RelationshipProperty
from uuid import UUID
from typing import Union
from backend_api.data.database import SessionDep
from sqlmodel import select
from sqlalchemy import func


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

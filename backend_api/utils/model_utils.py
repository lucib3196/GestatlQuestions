from sqlalchemy.inspection import inspect
from sqlalchemy.orm.exc import UnmappedInstanceError
from sqlalchemy.orm.properties import RelationshipProperty
from sqlalchemy import func, cast, String
from sqlalchemy.orm.properties import RelationshipProperty
from uuid import UUID
from typing import Union


def get_question_id_UUID(question_id) -> Union[UUID, None]:
    """Validate and convert a question_id to UUID or raise HTTP 400."""
    try:
        if isinstance(question_id, UUID):
            return question_id
        else:
            return UUID(question_id)
    except ValueError:
        return None


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

# Stdlib
from typing import Dict, List, Optional, Type, TypeVar, Union
from uuid import UUID

# Third-party
from sqlalchemy import String, cast, func
from sqlalchemy.inspection import inspect
from sqlalchemy.orm.properties import RelationshipProperty
from sqlmodel import SQLModel

# Local
from datetime import datetime


def convert_uuid(uuid: str | UUID) -> UUID:
    try:
        if isinstance(uuid, UUID):
            return uuid
        else:
            return UUID(uuid)
    except Exception as e:
        raise ValueError(f"Could not convert {type(uuid)} into UUID")


T = TypeVar("T", bound=SQLModel)


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


def normalize_kwargs(kwargs: dict):
    normalized = {}
    for key, value in kwargs.items():
        if isinstance(value, list):
            for v in value:
                if isinstance(v, dict):
                    f = [v.get("name")]
                else:
                    f = [v]

                normalized[key] = f

        else:
            normalized[key] = value
    return normalized


def safe_python_type(col):
    try:
        return col.type.python_type
    except (NotImplementedError, AttributeError):
        return object


def normalize_timestamps(data: dict) -> dict:
    for field in ("created_at", "updated_at", "deleted_at", "storage_updated_at"):
        if field in data and isinstance(data[field], str):
            try:
                data[field] = datetime.fromisoformat(data[field])
            except ValueError:
                # fallback: drop invalid date or log warning
                data[field] = None
    return data

from typing import Sequence, Union, List
from sqlmodel import select
from sqlalchemy import func

from backend_api.model.question_model import QType
from backend_api.data.database import SessionDep


def create_qtype(session: SessionDep, name: str) -> QType:
    """
    Create (or fetch existing) question type by name.
    Normalizes to lowercase and trims whitespace.
    """
    if not name or not str(name).lower().strip():
        raise ValueError("QType name cannot be empty")
    canon = str(name).lower().strip()

    existing = session.exec(
        select(QType).where(func.lower(QType.name) == canon)
    ).first()

    if existing:
        return existing

    qt = QType(name=canon)
    session.add(qt)
    session.commit()
    session.refresh(qt)
    return qt


def list_qtypes(session: SessionDep) -> Sequence[QType]:
    """Return all qtypes."""
    return session.exec(select(QType)).all()


def get_qtype_by_name(session: SessionDep, name: str) -> Union[QType, None]:
    """Fetch a qtype by case-insensitive name; returns None if not found."""
    if not name:
        return None
    canon = str(name).lower().strip()
    return session.exec(select(QType).where(func.lower(QType.name) == canon)).first()

def get_qtypes_by_name(session: SessionDep, names: List[str])->List[QType]:
    if not names: 
        return []
    qtypes = []
    for n in names: 
        if not n:
            continue
        qtype = get_qtype_by_name(session,n)
        if qtype:
            qtypes.append(qtype)
    return qtypes

def delete_qtype(session: SessionDep, qtype: QType) -> None:
    """Delete a specific qtype."""
    session.delete(qtype)
    session.commit()


def delete_all_qtypes(session: SessionDep) -> None:
    """Delete all qtypes."""
    for qt in session.exec(select(QType)).all():
        delete_qtype(session, qt)

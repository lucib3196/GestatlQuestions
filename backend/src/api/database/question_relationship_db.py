from typing import List, Sequence, Union

from sqlalchemy import func
from sqlmodel import select

from src.api.database import SessionDep
from src.api.models.question_model import Language, QType, Topic
from src.utils import normalize_name


# --------------------
# QType CRUD
# --------------------
def create_qtype(session: SessionDep, name: str) -> QType:
    """
    Create (or fetch existing) question type by name.
    Normalizes to lowercase and trims whitespace.
    """
    canon = normalize_name(name)
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
    canon = normalize_name(name)
    return session.exec(select(QType).where(func.lower(QType.name) == canon)).first()


def get_qtypes_by_name(session: SessionDep, names: List[str]) -> List[QType]:
    if not names:
        return []
    qtypes: List[QType] = []
    for n in names:
        if not n:
            continue
        qtype = get_qtype_by_name(session, n)
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


# --------------------
# Language CRUD
# --------------------
def create_language(session: SessionDep, name: str) -> Language:
    canon = normalize_name(name)
    existing = session.exec(
        select(Language).where(func.lower(Language.name) == canon)
    ).first()
    if existing:
        return existing

    lang = Language(name=canon)
    session.add(lang)
    session.commit()
    session.refresh(lang)
    return lang


def list_languages(session: SessionDep) -> Sequence[Language]:
    return session.exec(select(Language)).all()


def get_language_by_name(session: SessionDep, name: str) -> Union[Language, None]:
    canon = normalize_name(name)
    stmt = select(Language).where(func.lower(Language.name) == canon)
    return session.exec(stmt).first()


def get_languages_by_name(session: SessionDep, names: List[str]) -> List[Language]:
    if not names:
        return []
    languages: List[Language] = []
    for n in names:
        if not n:
            continue
        language = get_language_by_name(session, n)
        if language:
            languages.append(language)
    return languages


def delete_language(session: SessionDep, language: Language) -> None:
    session.delete(language)
    session.commit()


def delete_all_languages(session: SessionDep) -> None:
    for lang in session.exec(select(Language)).all():
        delete_language(session, lang)


# --------------------
# Topic CRUD
# --------------------
def create_topic(session: SessionDep, name: str) -> Topic:
    canon = normalize_name(name)
    result = session.exec(select(Topic).where(func.lower(Topic.name) == canon)).first()
    if result:
        return result

    t = Topic(name=canon)
    session.add(t)
    session.commit()
    session.refresh(t)
    return t


def list_topics(session: SessionDep) -> Sequence[Topic]:
    return session.exec(select(Topic)).all()


def get_topic_by_name(session: SessionDep, name: str) -> Union[Topic, None]:
    canon = normalize_name(name)
    stmt = select(Topic).where(func.lower(Topic.name) == canon)
    return session.exec(stmt).first()


def get_topics_by_name(session: SessionDep, names: Sequence[str]) -> List[Topic]:
    """
    Return a list of Topic objects that match the given names.
    Ignores None/empty strings in names.
    """
    if not names:
        return []

    topics: List[Topic] = []
    for n in names:
        if not n:
            continue
        topic = get_topic_by_name(session, n)
        if topic:
            topics.append(topic)
    return topics


def delete_topic(session: SessionDep, topic: Topic) -> None:
    session.delete(topic)
    session.commit()
    session.flush()


def delete_all_topics(session: SessionDep) -> None:
    results = session.exec(select(Topic)).all()
    for t in results:
        delete_topic(session, t)

from typing import Sequence, Union
from sqlmodel import select
from sqlalchemy import func
from typing import List

from api.models.question_model import Language
from api.data.database import SessionDep


def create_language(session: SessionDep, name: str) -> Language:
    if not name or not name.lower().strip():
        raise ValueError("Language name cannot be empty")
    name = name.lower().strip()

    existing = session.exec(
        select(Language).where(func.lower(Language.name) == name)
    ).first()

    if not existing:
        lang = Language(name=name)
        session.add(lang)
        session.commit()
        session.refresh(lang)
        return lang
    else:
        return existing


def list_languages(session: SessionDep) -> Sequence[Language]:
    return session.exec(select(Language)).all()


def get_language_by_name(session: SessionDep, name: str) -> Union[Language, None]:
    stmt = select(Language).where(func.lower(Language.name) == name.lower().strip())
    return session.exec(stmt).first()


def get_languages_by_name(session: SessionDep, names: List[str]) -> List[Language]:
    if not names:
        return []
    languages = []
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

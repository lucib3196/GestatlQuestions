import pytest
from api.data import language_db as language_service
from backend.src.app_test.unit.database.conftest import  db_session


# ----------------------
# Language Creation
# ----------------------


@pytest.mark.parametrize(
    "language_name",
    [
        "Python",
        "JavaScript",
        "TypeScript    ",  # trailing whitespace should be stripped
    ],
)
def test_create_language(db_session, language_name):
    lang = language_service.create_language(db_session, name=language_name)
    assert lang.id is not None
    assert lang.name == language_name.lower().strip()


@pytest.mark.parametrize("language_name", [None, "", "    "])
def test_create_language_no_name(db_session, language_name):
    with pytest.raises(ValueError, match=r"^Language name cannot be empty$"):
        language_service.create_language(db_session, language_name)


def test_create_duplicate_language_return_existing(db_session):
    lang1 = language_service.create_language(db_session, name="Python")
    lang2 = language_service.create_language(db_session, name="python")

    assert lang2.id == lang1.id
    assert lang2.name.lower() == lang1.name.lower()

    language_service.delete_all_languages(db_session)  # Cleanup


# ----------------------
# Language Retrieval
# ----------------------


@pytest.mark.parametrize("names", [["Python", "JavaScript", "Rust", "Go"]])
def test_list_languages_returns_all(db_session, names):
    language_service.delete_all_languages(db_session)  # Cleanup

    for n in names:
        language_service.create_language(db_session, name=n)

    result = language_service.list_languages(db_session)
    returned_names = [l.name for l in result]

    assert set(returned_names) == {n.lower().strip() for n in names}


def test_get_language_by_name_found(db_session):
    created = language_service.create_language(db_session, name="C++")
    fetched = language_service.get_language_by_name(db_session, name="c++")

    assert fetched is not None
    assert fetched.id == created.id


def test_get_language_by_name_not_found_none_return(db_session):
    assert language_service.get_language_by_name(db_session, "UnknownLang") is None


# ----------------------
# Language Deletion
# ----------------------


def test_delete_language_success(db_session):
    lang = language_service.create_language(db_session, name="Ruby")

    retrieved = language_service.get_language_by_name(db_session, lang.name)
    assert retrieved == lang

    language_service.delete_language(db_session, language=lang)
    assert language_service.get_language_by_name(db_session, lang.name) is None


def test_delete_all_languages(db_session):
    language_service.delete_all_languages(db_session)
    assert language_service.list_languages(db_session) == []

import pytest
from backend_api.data import qtype as qtype_service
from app_test.conftest import engine as db_session


# ----------------------
# QType Creation
# ----------------------


@pytest.mark.parametrize(
    "qtype_name",
    [
        "Numerical",
        "Multiple Choice",
        "True/False    ",  # trailing whitespace should be stripped
    ],
)
def test_create_qtype(db_session, qtype_name):
    qt = qtype_service.create_qtype(db_session, name=qtype_name)
    assert qt.id is not None
    assert qt.name == qtype_name.lower().strip()


@pytest.mark.parametrize("qtype_name", [None, "", "    "])
def test_create_qtype_no_name(db_session, qtype_name):
    with pytest.raises(ValueError, match=r"^QType name cannot be empty$"):
        qtype_service.create_qtype(db_session, qtype_name)


def test_create_duplicate_qtype_return_existing(db_session):
    qt1 = qtype_service.create_qtype(db_session, name="Numerical")
    qt2 = qtype_service.create_qtype(db_session, name="numerical")

    assert qt2.id == qt1.id
    assert qt2.name.lower() == qt1.name.lower()

    qtype_service.delete_all_qtypes(db_session)  # Cleanup


# ----------------------
# QType Retrieval
# ----------------------


@pytest.mark.parametrize(
    "names", [["Numerical", "Multiple Choice", "True/False", "Short Answer"]]
)
def test_list_qtypes_returns_all(db_session, names):
    qtype_service.delete_all_qtypes(db_session)  # Cleanup

    for n in names:
        qtype_service.create_qtype(db_session, name=n)

    result = qtype_service.list_qtypes(db_session)
    returned_names = [q.name for q in result]

    assert set(returned_names) == {n.lower().strip() for n in names}


def test_get_qtype_by_name_found(db_session):
    created = qtype_service.create_qtype(db_session, name="Multiple Choice")
    fetched = qtype_service.get_qtype_by_name(db_session, name="multiple choice")

    assert fetched is not None
    assert fetched.id == created.id


def test_get_qtype_by_name_not_found_none_return(db_session):
    assert qtype_service.get_qtype_by_name(db_session, "Fill in the Blank") is None


# ----------------------
# QType Deletion
# ----------------------


def test_delete_qtype_success(db_session):
    qt = qtype_service.create_qtype(db_session, name="Short Answer")

    retrieved = qtype_service.get_qtype_by_name(db_session, qt.name)
    assert retrieved == qt

    qtype_service.delete_qtype(db_session, qtype=qt)
    assert qtype_service.get_qtype_by_name(db_session, qt.name) is None


def test_delete_all_qtypes(db_session):
    qtype_service.delete_all_qtypes(db_session)
    assert qtype_service.list_qtypes(db_session) == []

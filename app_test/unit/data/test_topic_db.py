import pytest
from backend_api.data import topic_db as topic_service
from app_test.conftest import engine as db_session


# ----------------------
# Topic Creation
# ----------------------
@pytest.mark.parametrize(
    "topic_name",
    [
        "Kinematics",
        "Machine Learning",
        "Some topic with white space    ",
    ],
)
def test_create_topic(db_session, topic_name):
    topic = topic_service.create_topic(db_session, name=topic_name)
    assert topic.id is not None
    assert topic.name == topic_name.lower().strip()


@pytest.mark.parametrize("topic_name", [None, "", "    "])
def test_create_topic_no_name(db_session, topic_name):
    with pytest.raises(ValueError, match=r"^Topic name cannot be empty$"):
        topic_service.create_topic(db_session, topic_name)


def test_create_duplicate_topic_return_existing(db_session):
    topic1 = topic_service.create_topic(db_session, name="Thermodynamics")
    topic2 = topic_service.create_topic(db_session, name="thermodynamics")

    assert topic2.id == topic1.id
    assert topic2.name.lower() == topic1.name.lower()

    topic_service.delete_all_topics(db_session)  # Cleanup


# ----------------------
# Topic Retrieval
# ----------------------


@pytest.mark.parametrize(
    "names", [["Kinematics", "Machine Learning", "Heat Transfer", "Thermodynamics"]]
)
def test_list_topics_returns_all(db_session, names):
    topic_service.delete_all_topics(db_session)  # Cleanup

    for n in names:
        topic_service.create_topic(db_session, name=n)

    result = topic_service.list_topics(db_session)
    returned_names = [t.name for t in result]

    assert set(returned_names) == {n.lower().strip() for n in names}


def test_get_topic_by_name_found(db_session):
    created = topic_service.create_topic(db_session, name="Quantum Mechanics")
    fetched = topic_service.get_topic_by_name(db_session, name="quantum mechanics")

    assert fetched is not None
    assert fetched.id == created.id


def test_get_topic_by_name_not_found_none_return(db_session):
    assert topic_service.get_topic_by_name(db_session, "Unknown Topic") is None


# ----------------------
# Topic Deletion
# ----------------------


def test_delete_topic_success(db_session):
    topic = topic_service.create_topic(db_session, name="Classical Mechanics")

    retrieved_topic = topic_service.get_topic_by_name(db_session, topic.name)
    assert retrieved_topic == topic

    topic_service.delete_topic(db_session, topic=topic)
    assert topic_service.get_topic_by_name(db_session, topic.name) is None


def test_delete_all_topics(db_session):
    topic_service.delete_all_topics(db_session)
    assert topic_service.list_topics(db_session) == []

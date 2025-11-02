from src.api.models.models import Question
from src.api.database import generic_db as gdb
import pytest
from src.api.models.models import Topic,Language, QType

def test_get_all_model_relationships():
    question_relationships = ["topics", "languages", "qtypes", "created_by"]
    all_relationships = gdb.get_all_model_relationships(Question)
    assert set(all_relationships.keys()) == set(question_relationships)

@pytest.mark.asyncio
async def test_get_model_relationship_data(
    create_question_with_relationship, relationship_payload
):
    q = await create_question_with_relationship
    for rel_name, data in relationship_payload.items():
        data = getattr(q, rel_name)
        assert [d.name in relationship_payload[rel_name] for d in data]


@pytest.mark.asyncio
async def test_get_all_model_relationship_data(
    create_question_with_relationship, relationship_payload
):
    q = await create_question_with_relationship
    rel_data = gdb.get_all_model_relationship_data(q, Question)
    assert rel_data
    for rel_name, data in rel_data.items():
        # There may be relationships that the payload does not have so skip these
        if rel_name not in relationship_payload:
            continue
        assert set(relationship_payload[rel_name]) == set([d.name for d in data])



@pytest.mark.parametrize(
    "payload",
    [
        {"target_cls": Topic, "value": "Not a Topic", "lookup_field": "name"},
        {"target_cls": Language, "value": "Not a Language", "lookup_field": "name"},
        {"target_cls": QType, "value": "Not a Qtype", "lookup_field": "name"},
    ],
)
def test_create_or_resolve(db_session, payload):
    # Act
    created_model, existed = gdb.create_or_resolve(
        target_cls=payload["target_cls"],
        target_value=payload["value"],
        session=db_session,
        lookup_field=payload["lookup_field"],
    )

    # Assert
    assert created_model is not None
    assert existed is False
    assert created_model.id is not None
    assert created_model.name.lower().strip() == payload["value"].lower().strip()


@pytest.mark.parametrize(
    "rel_attributes",
    [
        {"target_model": Question, "target_rel": "topics"},
        {"target_model": Question, "target_rel": "languages"},
        {"target_model": Question, "target_rel": "qtypes"},
    ],
)
def test_is_relationship(rel_attributes):
    assert gdb.is_relationship(
        model=rel_attributes["target_model"], attr_name=rel_attributes["target_rel"]
    )



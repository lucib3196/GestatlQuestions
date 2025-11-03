import pytest
from fastapi import HTTPException

@pytest.mark.asyncio
@pytest.fixture
async def qm_create_question(question_payload, question_manager):
    qcreated = await question_manager.create_question(question_payload)
    assert qcreated
    return qcreated


@pytest.mark.asyncio
async def test_question_creation(qm_create_question):
    assert await qm_create_question


@pytest.mark.asyncio
async def test_get_question_(qm_create_question, question_manager):
    qcreated = await qm_create_question
    assert qcreated == question_manager.get_question(qcreated.id)


@pytest.mark.asyncio
async def test_delete_question(qm_create_question, question_manager):
    qcreated = await qm_create_question
    assert qcreated == question_manager.get_question(qcreated.id)
    assert question_manager.delete_question(qcreated.id)
    with pytest.raises(HTTPException) as exc_info:
        question_manager.get_question(qcreated.id)
    assert "does not exist" in str(exc_info.value.detail).lower()
import pytest
from src.app_test.fixtures.fixture_code_generation import *
from src.api.service.ai_generation import code_generation
from src.api.service.crud import question_crud


@pytest.mark.asyncio
@pytest.mark.parametrize("payload_index", range(1))  # adjust to len(question_payloads)
async def test_run_text_each(
    db_session, question_payloads, payload_index, patch_questions_path, question_manager_test
):
    payload = question_payloads[payload_index]

    result = await code_generation.run_text(
        text=payload["question"],
        session=db_session,
        additional_meta=payload["additional_meta"],
        qm=question_manager_test,
    )

    assert result["success"] is True
    assert "questions" in result
    print(result["questions"])


@pytest.mark.asyncio
async def test_run_text_bulk(
    db_session, question_payloads, patch_questions_path, question_manager
):
    for payload in question_payloads:
        result = await code_generation.run_text(
            text=payload["question"],
            session=db_session,
            additional_meta=payload["additional_meta"],
            qm=question_manager,
        )
        assert result["success"] is True
        assert "questions" in result


@pytest.mark.asyncio
@pytest.mark.parametrize("payload_index", range(1))  # adjust to len(question_payloads)
async def test_run_test_check_db(
    db_session, question_payloads, payload_index, patch_questions_path, question_manager
):
    payload = question_payloads[payload_index]

    result = await code_generation.run_text(
        text=payload["question"],
        session=db_session,
        additional_meta=payload["additional_meta"],
        qm=question_manager,
    )
    assert "questions" in result

    question_list: list = result.get("questions", [])
    for q in question_list:
        question_uuid = q.get("id")
        q_retrieved = await question_crud.get_question_by_id(
            question_uuid, session=db_session
        )
        assert q_retrieved is not None

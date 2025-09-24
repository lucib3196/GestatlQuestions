# --- Standard Library ---
from pathlib import Path
from typing import Dict, Tuple

# --- Third-Party ---
import pytest
import json
# --- Internal ---
from src.api.core import settings, logger


# Test
@pytest.mark.asyncio
async def test_create_question(
    question_manager_cloud, db_session, question_payload_minimal_dict, tmp_path
):
    qcreated = await question_manager_cloud.create_question(question_payload_minimal_dict, db_session)

    assert qcreated
    assert qcreated.title == question_payload_minimal_dict["title"]

    assert Path(qcreated.blob_name) == Path("integration_test") / question_payload_minimal_dict["title"]


@pytest.mark.asyncio
async def test_create_question_duplicate(
    question_manager_cloud, db_session, question_payload_minimal_dict, tmp_path
):
    q1 = await question_manager_cloud.create_question(question_payload_minimal_dict, db_session)
    logger.debug(f"This is q1{q1}")
    q2 = await question_manager_cloud.create_question(question_payload_minimal_dict, db_session)
    
    logger.debug(f"This is q2{q2}")

    expected_path =  Path("integration_test")/ f"{question_payload_minimal_dict['title']}_{q2.id}"
    assert Path(q2.blob_name) == expected_path
    
@pytest.mark.asyncio
async def test_get_question(question_manager_cloud, db_session, question_payload_minimal_dict):
    q1 = await question_manager_cloud.create_question(question_payload_minimal_dict, db_session)
    q_retrieved = await question_manager_cloud.get_question(q1.id, db_session)

    assert q1 == q_retrieved
    
@pytest.mark.asyncio
async def test_get_question_identifier(question_manager_cloud, db_session, question_payload_minimal_dict):
    q1 = await question_manager_cloud.create_question(question_payload_minimal_dict, db_session)
    retrieved_identifier = await question_manager_cloud.get_question_identifier(
        q1.id, db_session
    )

    assert retrieved_identifier == q1.title
    
@pytest.mark.asyncio
async def test_get_question_identifier_duplicate(
    question_manager_cloud, db_session, question_payload_minimal_dict
):
    await question_manager_cloud.create_question(question_payload_minimal_dict, db_session)
    q2 = await question_manager_cloud.create_question(question_payload_minimal_dict, db_session)

    expected_identifier = f"{q2.title}_{q2.id}"
    retrieved_identifier = await question_manager_cloud.get_question_identifier(
        q2.id, db_session
    )

    assert retrieved_identifier == expected_identifier
    
@pytest.mark.asyncio
async def test_save_file_to_question(
    question_manager_cloud, db_session, question_payload_minimal_dict, file_data_payload
):
    q1 = await question_manager_cloud.create_question(question_payload_minimal_dict, db_session)

    for f in file_data_payload:
        result = await question_manager_cloud.save_file_to_question(q1.id, db_session, f)
        assert result
        
@pytest.mark.asyncio
async def test_get_file(question_manager_cloud, db_session, question_payload_minimal_dict, file_data_payload):
    q1 = await question_manager_cloud.create_question(question_payload_minimal_dict, db_session)
    await question_manager_cloud.save_files_to_question(q1.id, db_session, file_data_payload)

    for f in file_data_payload:
        content = await question_manager_cloud.get_file(q1.id, db_session, f.filename)
        assert content

        if isinstance(f.content, dict):
            assert f.content == json.loads(content)
        elif isinstance(f.content, (bytes, bytearray)):
            assert f.content == content
            
@pytest.mark.asyncio
async def test_get_all_files(
    question_manager_cloud, db_session, question_payload_minimal_dict, file_data_payload
):
    q1 = await question_manager_cloud.create_question(question_payload_minimal_dict, db_session)
    await question_manager_cloud.save_files_to_question(q1.id, db_session, file_data_payload)

    all_files = await question_manager_cloud.get_all_files(q1.id, db_session)

    assert len(all_files) == len(file_data_payload)
    assert {f.filename for f in file_data_payload} == set(all_files)
    
@pytest.mark.asyncio
async def test_delete_file(
    question_manager_cloud, db_session, question_payload_minimal_dict, file_data_payload
):
    q1 = await question_manager_cloud.create_question(question_payload_minimal_dict, db_session)
    await question_manager_cloud.save_files_to_question(q1.id, db_session, file_data_payload)

    for f in file_data_payload:
        await question_manager_cloud.delete_question_file(
            q1.id, db_session, filename=f.filename
        )
        assert await question_manager_cloud.get_file(q1.id, db_session, f.filename) is None
        

@pytest.mark.asyncio
async def test_delete_question(
    question_manager_cloud, db_session, question_payload_minimal_dict, file_data_payload
):
    q1 = await question_manager_cloud.create_question(question_payload_minimal_dict, db_session)
    await question_manager_cloud.save_files_to_question(q1.id, db_session, file_data_payload)

    await question_manager_cloud.delete_question(q1.id, db_session)
    assert await question_manager_cloud.get_question(q1.id, db_session) is None


@pytest.mark.asyncio
async def test_update_question(question_manager_cloud, db_session, question_payload_minimal_dict):
    q1 = await question_manager_cloud.create_question(question_payload_minimal_dict, db_session)
    qupdated = await question_manager_cloud.update_question(
        question_id=q1.id, session=db_session, title="NewTitle"
    )
    logger.debug(f"This is the updated question {qupdated}")
    qretrieved = await question_manager_cloud.get_question(q1.id, db_session)
    assert q1.title == "NewTitle"

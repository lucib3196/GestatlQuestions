# --- Standard Library ---
from pathlib import Path

# --- Third-Party ---
import pytest

# --- Internal ---

@pytest.mark.asyncio
async def test_create_question(question_manager, db_session, question_payload_minimal_dict, tmp_path):
    qcreated = await question_manager.create_question(question_payload_minimal_dict, db_session)
    assert qcreated
    assert qcreated.title == question_payload_minimal_dict["title"]

    if question_manager.storage_type == "cloud":
        expected = Path("integration_test") / question_payload_minimal_dict["title"]
        assert Path(qcreated.blob_name) == expected
    else:  # local
        expected = tmp_path / "questions" / question_payload_minimal_dict["title"]
        assert Path(qcreated.local_path) == expected


@pytest.mark.asyncio
async def test_create_question_duplicate(question_manager, db_session, question_payload_minimal_dict, tmp_path):
    await question_manager.create_question(question_payload_minimal_dict, db_session)
    q2 = await question_manager.create_question(question_payload_minimal_dict, db_session)

    if question_manager.storage_type == "cloud":
        expected = Path("integration_test") / f"{question_payload_minimal_dict['title']}_{q2.id}"
        assert Path(q2.blob_name) == expected
    else:  # local
        expected = tmp_path / "questions" / f"{question_payload_minimal_dict['title']}_{q2.id}"
        assert Path(q2.local_path) == expected

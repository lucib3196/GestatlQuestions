# --- Standard Library ---
import json
from typing import List

# --- Third-Party ---
import pytest

# --- Internal ---
from src.api.core import logger
from src.utils.test_utils import prepare_file_uploads
from src.api.response_models import FileData
from fastapi.encoders import jsonable_encoder


@pytest.mark.parametrize("file_fixture", ["file_data_payload", "question_file_payload"])
def test_update_file(
    request, test_client, db_session, question_payload_minimal_dict, file_fixture
):
    """
    Ensure that uploaded files for a question can be updated (overwritten)
    and that the new content is retrievable.
    """
    # Arrange: create a question with uploaded files
    data = {"question": json.dumps(question_payload_minimal_dict)}
    files_data: List[FileData] = request.getfixturevalue(file_fixture)
    files = prepare_file_uploads(files_data)

    creation_resp = test_client.post("/questions/", data=data, files=files)
    body = creation_resp.json()
    qid = body["question"]["id"]

    # Act + Assert: update each file and verify new content
    for f in files_data:
        new_content = f"Updated content for {f.filename}"
        update_payload = {
            "question_id": qid,
            "filename": f.filename,
            "new_content": new_content,
        }

        update_resp = test_client.put("/questions/update_file", json=update_payload)
        assert update_resp.status_code == 200, update_resp.text

        # Retrieve the updated file
        retrieval_resp = test_client.get(f"/questions/{qid}/files/{f.filename}")
        assert retrieval_resp.status_code == 200
        retrieved_content = retrieval_resp.json()

        logger.debug("File %s retrieved content: %s", f.filename, retrieved_content)
        assert retrieved_content == new_content


@pytest.mark.asyncio
async def test_update_question_meta_title_and_isadaptive(
    test_client, create_question_minimal_response
):
    """
    Creates a single question, then PATCHes metadata (title, isAdaptive).
    Verifies the route returns the updated object.
    """
    create_resp = create_question_minimal_response
    assert create_resp.status_code == 200
    created = create_resp.json()
    assert "question" in created
    quid = created["question"]["id"]

    # 2) Patch its metadata
    updates = {
        "title": "Updated Title",
        "isAdaptive": True,
    }
    patch_resp = test_client.patch(
        f"/questions/update_question/{quid}",
        json=updates,
    )
    assert patch_resp.status_code == 201

    updated = patch_resp.json()
    # Depending on your edit_question_meta return shape, this may be a dict with the fields
    assert updated["id"] == quid
    assert updated["title"] == "Updated Title"
    assert updated["isAdaptive"] is True

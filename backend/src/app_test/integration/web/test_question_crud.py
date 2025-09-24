from fastapi.encoders import jsonable_encoder
from uuid import UUID
from uuid import uuid4
from fastapi import HTTPException
from src.utils import pick


def test_get_question_data_meta_no_files(
    test_client, create_question_response_no_files
):
    create_resp, _ = create_question_response_no_files
    qid = create_resp.json()["question"]["id"]

    r = test_client.get(f"/question_crud/get_question_data_meta/{qid}")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == 200
    assert body["question"]["id"] == qid
    assert body["files"] == []  # this route intentionally returns files=None


def test_get_question_data_meta_with_files(
    test_client, create_question_response_with_files
):
    create_resp, expected_q, _ = create_question_response_with_files
    qid = create_resp.json()["question"]["id"]

    r = test_client.get(f"/question_crud/get_question_data_meta/{qid}")
    assert r.status_code == 200
    body = r.json()
    q = body["question"]

    # Base fields
    assert body["status"] == 200
    assert isinstance(body["files"], list)
    assert body["files"] == []
    assert q["id"] == qid
    assert q["title"] == expected_q["title"]
    assert q["ai_generated"] == expected_q["ai_generated"]
    assert q["isAdaptive"] == expected_q["isAdaptive"]
    assert q["createdBy"] == expected_q["createdBy"]
    assert q["user_id"] == expected_q["user_id"]


def test_get_question_data_meta_with_additional_meta(
    test_client, create_question_response_with_additional_meta
):
    create_resp, expected_q, _, expected_meta = (
        create_question_response_with_additional_meta
    )
    qid = create_resp.json()["question"]["id"]

    r = test_client.get(f"/question_crud/get_question_data_meta/{qid}")
    assert r.status_code == 200
    body = r.json()
    q = body["question"]

    # Base fields
    assert body["status"] == 200
    assert body["files"] == []
    assert q["id"] == qid
    assert q["title"] == expected_q["title"]
    assert q["ai_generated"] == expected_q["ai_generated"]
    assert q["isAdaptive"] == expected_q["isAdaptive"]
    assert q["createdBy"] == expected_q["createdBy"]
    assert q["user_id"] == expected_q["user_id"]

    # Additional metadata (supports dict or string responses)
    if expected_meta.get("topics"):
        got = [t["name"] if isinstance(t, dict) else t for t in q.get("topics", [])]
        for v in expected_meta["topics"]:
            assert v.lower() in got
    if expected_meta.get("languages"):
        got = [l["name"] if isinstance(l, dict) else l for l in q.get("languages", [])]
        for v in expected_meta["languages"]:
            assert v in got
    if expected_meta.get("qtypes"):
        got = [x["name"] if isinstance(x, dict) else x for x in q.get("qtypes", [])]
        for v in expected_meta["qtypes"]:
            assert v in got


def test_get_question_data_meta_not_found(test_client):
    bad_id = uuid4()
    r = test_client.get(f"/question_crud/get_question_data_meta/{bad_id}")
    assert r.status_code == 404


# ---------------------------
# /get_question_data_all/{qid}
# ---------------------------


def test_get_question_data_all_no_files(test_client, create_question_response_no_files):
    create_resp, _ = create_question_response_no_files
    qid = create_resp.json()["question"]["id"]

    r = test_client.get(f"/question_crud/get_question_data_all/{qid}")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == 200
    assert body["question"]["id"] == qid
    # depending on your API, this may be [] or None when no files exist
    assert body.get("files") in (None, [], {})


def test_get_question_data_all_with_files(
    test_client, create_question_response_with_files
):
    create_resp, expected_q, expected_files = create_question_response_with_files
    qid = create_resp.json()["question"]["id"]

    r = test_client.get(f"/question_crud/get_question_data_all/{qid}")
    assert r.status_code == 200
    body = r.json()
    q = body["question"]

    # Base
    assert body["status"] == 200
    assert q["id"] == qid
    assert q["title"] == expected_q["title"]
    assert q["ai_generated"] == expected_q["ai_generated"]
    assert q["isAdaptive"] == expected_q["isAdaptive"]
    assert q["createdBy"] == expected_q["createdBy"]
    assert q["user_id"] == expected_q["user_id"]

    # Files
    files = body["files"]
    assert isinstance(files, list)
    assert len(files) == len(expected_files)
    resp_names = {f["filename"] for f in files}
    exp_names = {f["filename"] for f in expected_files}
    assert resp_names == exp_names


def test_get_question_data_all_with_additional_meta(
    test_client, create_question_response_with_additional_meta
):
    create_resp, expected_q, expected_files, expected_meta = (
        create_question_response_with_additional_meta
    )
    qid = create_resp.json()["question"]["id"]

    r = test_client.get(f"/question_crud/get_question_data_all/{qid}")
    assert r.status_code == 200
    body = r.json()
    q = body["question"]

    # Base
    assert body["status"] == 200
    assert q["id"] == qid
    assert q["title"] == expected_q["title"]
    assert q["ai_generated"] == expected_q["ai_generated"]
    assert q["isAdaptive"] == expected_q["isAdaptive"]
    assert q["createdBy"] == expected_q["createdBy"]
    assert q["user_id"] == expected_q["user_id"]

    # Metadata
    if expected_meta.get("topics"):
        got = [t["name"] if isinstance(t, dict) else t for t in q.get("topics", [])]
        for v in expected_meta["topics"]:
            assert v.lower() in got
    if expected_meta.get("languages"):
        got = [l["name"] if isinstance(l, dict) else l for l in q.get("languages", [])]
        for v in expected_meta["languages"]:
            assert v in got
    if expected_meta.get("qtypes"):
        got = [x["name"] if isinstance(x, dict) else x for x in q.get("qtypes", [])]
        for v in expected_meta["qtypes"]:
            assert v in got

    # Files
    files = body["files"]
    assert isinstance(files, list)
    assert len(files) == len(expected_files)
    resp_names = {f["filename"] for f in files}
    exp_names = {f["filename"] for f in expected_files}
    assert resp_names == exp_names


def test_get_question_data_all_not_found(test_client):
    bad_id = uuid4()
    r = test_client.get(f"/question_crud/get_question_data_all/{bad_id}")
    assert r.status_code == 404





# Testing getting all the questions
@pytest.mark.asyncio
async def test_get_all_questions_simple(test_client, create_multiple_questions):
    response = test_client.get("/question_crud/get_all_questions_simple/0/100")
    number_questions = 3
    question_list = response.json()
    assert response.status_code == 200
    assert isinstance(question_list, list)
    assert len(question_list) == number_questions


# Test Filtering Questions
### Notes: This test needs to be a bit more robuts but basically it just checks to make sure that the
### Routes runs and asserts its a list
@pytest.mark.asyncio
async def test_question_filter(test_client, create_multiple_questions):
    payload = {
        "title": "Sample",  # substring to search in title
    }

    response = test_client.post("/question_crud/filter_questions/", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert all("title" in q for q in data)


@pytest.mark.asyncio
async def test_filter_questions_by_title_and_flags(
    test_client, create_multiple_questions
):
    """
    Filters by a substring in title + ai_generated + createdBy.
    Uses the questions inserted by the create_multiple_questions fixture.
    """
    payload = {
        "title": "Question",  # should match "QuestionWithFiles"
        "ai_generated": True,
        "createdBy": "tester",
        # don't include isAdaptive here; your fixtures set it False
        # add "user_id": 1 if your filter requires it
    }

    resp = test_client.post(
        "/question_crud/filter_questions/",
        json=payload,
    )
    assert resp.status_code == 200

    data = resp.json()
    assert isinstance(data, list)
    assert len(data) >= 1

    # Basic sanity checks on the filtered results
    for q in data:
        assert "title" in q
        assert "createdBy" in q
        assert q["ai_generated"] is True
        assert "Question" in q["title"]
        assert q["createdBy"] == "tester"


@pytest.mark.asyncio
async def test_update_question_meta_title_and_isadaptive(
    test_client, question_payload_model_no_files
):
    """
    Creates a single question, then PATCHes metadata (title, isAdaptive).
    Verifies the route returns the updated object.
    """
    # 1) Create a question to get its id
    create_resp = test_client.post(
        "/question_crud/create_question/text/",
        json=jsonable_encoder(question_payload_model_no_files),
    )
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
        f"/question_crud/update_question/{quid}",
        json=updates,
    )
    assert patch_resp.status_code == 200

    updated = patch_resp.json()
    # Depending on your edit_question_meta return shape, this may be a dict with the fields
    assert updated["id"] == quid
    assert updated["title"] == "Updated Title"
    assert updated["isAdaptive"] is True

# # --- Standard Library ---
# from typing import List
# from uuid import uuid4

# # --- Third-Party ---
# import pytest

# # --- Internal ---
# from src.api.core import logger
# from src.utils.test_utils import prepare_file_uploads
# from src.api.models import FileData
# from src.utils.normalization_utils import to_serializable

# from src.api.models.models import Question
# from src.utils import normalize_content

# from app_test.fixtures.fixture_crud import (
#     create_question,
#     retrieve_files,
#     retrieve_single_file,
# )

# QUESTION_KEYS = ["title", "ai_generated", "isAdaptive", "createdBy"]


# # Helpers


# # File Retrieval
# @pytest.mark.parametrize("file_fixture", ["file_data_payload", "question_file_payload"])
# def test_list_question_files(
#     request, test_client, db_session, question_payload_minimal_dict, file_fixture
# ):
#     """
#     Ensure that uploaded files for a question are listed correctly.
#     """
#     # Arrange: create a question with uploaded files
#     files_data: List[FileData] = request.getfixturevalue(file_fixture)
#     files = prepare_file_uploads(files_data)
#     question = create_question(
#         test_client, payload=question_payload_minimal_dict, files=files
#     )
#     # Act: retrieve the list of files
#     validated = retrieve_files(test_client, question.id, route_arg="files")
#     retrieved = validated.filepaths

#     logger.debug("These are the retreived files", retrieved)
#     assert len([f.filename for f in files_data]) == len(retrieved)
#     assert {f.filename for f in files_data} == set(retrieved)


# @pytest.mark.parametrize("file_fixture", ["file_data_payload", "question_file_payload"])
# def test_list_question_files_data(
#     request, test_client, db_session, question_payload_minimal_dict, file_fixture
# ):
#     """
#     Ensure that uploaded files are returned with their data (filename + content).
#     """

#     files_data: List[FileData] = request.getfixturevalue(file_fixture)
#     files = prepare_file_uploads(files_data)

#     # Create the question with attached files
#     question = create_question(
#         test_client,
#         payload=question_payload_minimal_dict,
#         files=files,
#     )

#     # Act
#     validated = retrieve_files(test_client, question.id, route_arg="files_data")
#     retrieved_files: List[FileData] = validated.filedata

#     logger.debug("Retrieved file data: %s", retrieved_files)

#     # Assert: Count consistency
#     assert len(retrieved_files) == len(
#         files_data
#     ), f"Expected {len(files_data)} files, got {len(retrieved_files)}"

#     # Assert: Filenames match
#     uploaded_names = {f.filename for f in files_data}
#     retrieved_names = {f.filename for f in retrieved_files}
#     assert (
#         uploaded_names == retrieved_names
#     ), f"Mismatched filenames: {uploaded_names ^ retrieved_names}"

#     # Assert: Content integrity
#     for uploaded, retrieved in zip(
#         sorted(files_data, key=lambda f: f.filename),
#         sorted(retrieved_files, key=lambda f: f.filename),
#     ):
#         uploaded_content = normalize_content(uploaded.content)
#         retrieved_content = normalize_content(retrieved.content)

#         assert (
#             uploaded_content == retrieved_content
#         ), f"Content mismatch in file '{uploaded.filename}'"

#     logger.info("File data validated successfully for %d files.", len(retrieved_files))


# @pytest.mark.parametrize("file_fixture", ["file_data_payload", "question_file_payload"])
# def test_read_question_file(
#     request, test_client, db_session, question_payload_minimal_dict, file_fixture
# ):
#     """
#     Ensure that each uploaded file can be retrieved individually by filename.
#     """
#     files_data: List[FileData] = request.getfixturevalue(file_fixture)
#     files = prepare_file_uploads(files_data)

#     # Create the question with attached files
#     question = create_question(
#         test_client,
#         payload=question_payload_minimal_dict,
#         files=files,
#     )

#     # Act & Assert
#     for f in files_data:
#         retrieved_content = retrieve_single_file(
#             test_client, question.id, filename=f.filename
#         )
#         assert retrieved_content == normalize_content(f.content)


# # --- Standard Library ---
# from typing import List

# # --- Third-Party ---
# import pytest

# # --- Internal ---
# from src.utils.test_utils import prepare_file_uploads
# from src.api.models import FileData
# from app_test.fixtures.fixture_crud import (
#     create_question,
#     retrieve_single_file,
# )
# from src.utils import to_serializable, normalize_content


# @pytest.mark.parametrize("file_fixture", ["file_data_payload", "question_file_payload"])
# def test_update_file(
#     request, test_client, db_session, question_payload_minimal_dict, file_fixture
# ):
#     """
#     Ensure that uploaded files for a question can be updated (overwritten)
#     and that the new content is retrievable.
#     """
#     # Arrange: create a question with uploaded files
#     files_data: List[FileData] = request.getfixturevalue(file_fixture)
#     files = prepare_file_uploads(files_data)

#     # Create the question with attached files
#     question = create_question(
#         test_client,
#         payload=question_payload_minimal_dict,
#         files=files,
#     )

#     # Act + Assert: update each file and verify new content
#     for f in files_data:
#         new_content = f"Updated content for {f.filename}"
#         update_payload = {
#             "question_id": to_serializable(question.id),
#             "filename": f.filename,
#             "new_content": new_content,
#         }

#         update_resp = test_client.put("/questions/update_file", json=update_payload)
#         assert update_resp.status_code == 200, update_resp.text

#         # Retrieve the updated file
#         retrieved_content = retrieve_single_file(test_client, question.id, f.filename)
#         assert retrieved_content == normalize_content(new_content)




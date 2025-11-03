from uuid import uuid4
from src.api.core import logger



# TODO Fix this
# def test_delete_all(test_client, create_multiple_question, all_question_payloads):
#     """
#     Ensure all questions can be deleted successfully.
#     - Verify initial retrieval returns the expected number of questions.
#     - Call delete endpoint to remove all questions.
#     - Verify subsequent retrieval shows no questions left.
#     """
#     # --- Arrange / Act 1: Retrieve minimal list of questions ---
#     offset, limit = 0, 100
#     response = test_client.get(f"/questions/get_all/{offset}/{limit}/minimal")
#     assert response.status_code == 200, response.text

#     questions = response.json()
#     assert isinstance(questions, list), "Expected response to be a list"
#     assert len(questions) == len(
#         all_question_payloads
#     ), f"Expected {len(all_question_payloads)} questions, got {len(questions)}"
#     logger.info("these are the questions %s", questions)
#     # --- Act 2: Delete all questions ---
#     delete_response = test_client.delete("/questions/delete_all_questions")
#     delete_body = delete_response.json()

#     logger.info("This is the delete body", delete_body)


#     # --- Act 3: Verify no questions remain ---
#     response_after_delete = test_client.get(
#         f"/questions/get_all/{offset}/{limit}/minimal"
#     )
#     assert response_after_delete.status_code == 200, response_after_delete.text
#     questions_after_delete = response_after_delete.json()


#     assert isinstance(questions_after_delete, list)
#     assert len(questions_after_delete) == 0, "Expected all questions to be deleted"

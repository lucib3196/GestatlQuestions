
# # Test Filtering
# def test_question_filtering(db_session):
#     # Arrange: clean slate

#     q1 = question.create_question(
#         {
#             "title": "AutoCreate",
#             "ai_generated": True,
#             "isAdaptive": False,
#             "createdBy": "Alice",
#             "user_id": 1,
#             "topics": ["topic1", "topic2"],
#         },
#         db_session,
#     )

#     q2 = question.create_question(
#         {
#             "title": "Other Question",
#             "ai_generated": False,
#             "isAdaptive": True,
#             "createdBy": "Bob",
#             "user_id": 2,
#             "topics": ["topic3"],
#         },
#         db_session,
#     )

#     # AND across keys: title + ai_generated + topic name
#     res = question.filter_questions(
#         db_session, title="autocreate", ai_generated=True, topics="topic1"
#     )
#     assert isinstance(res, list)
#     assert {r.id for r in res} == {q1.id}
#     assert all("autocreate" in r.title.lower() for r in res)
#     assert all(r.ai_generated is True for r in res)
#     assert all(any(t.name == "topic1" for t in r.topics) for r in res)

#     # OR within a single key (topics): either topic1 OR topic3
#     res_or = question.filter_questions(db_session, topics=["topic1", "topic3"])
#     assert {r.id for r in res_or} == {q1.id, q2.id}

#     # Negative case: no match when AND condition fails
#     res_none = question.filter_questions(
#         db_session, title="AutoCreate", ai_generated=False
#     )
#     assert res_none == []

import pytest
from src.api.service.code_running import question_running_service
from src.code_runner.models import CodeRunResponse, QuizData
from src.app_test.fixtures.fixture_question_running_service import *
from src.utils import logs_contain
from fastapi import HTTPException


@pytest.mark.asyncio
async def test_running_server_js_check_response_model(
    create_question_with_code_file_serverjs, db_session
):
    question = await create_question_with_code_file_serverjs
    result = await question_running_service.run_server(
        question_id=question.id,
        code_language="javascript",
        session=db_session,
        qm=
    )
    assert CodeRunResponse.model_validate(result)


@pytest.mark.asyncio
async def test_running_server_js_check_successful_response(
    create_question_with_code_file_serverjs, db_session
):
    question = await create_question_with_code_file_serverjs
    result = await question_running_service.run_server(
        question_id=question.id,
        code_language="javascript",
        session=db_session,
    )
    assert result.success == True


@pytest.mark.asyncio
async def test_running_server_js_check_error_none(
    create_question_with_code_file_serverjs, db_session
):
    question = await create_question_with_code_file_serverjs
    result = await question_running_service.run_server(
        question_id=question.id,
        code_language="javascript",
        session=db_session,
    )
    assert result.error == None


@pytest.mark.asyncio
async def test_running_server_js_check_quiz_data(
    create_question_with_code_file_serverjs, db_session
):
    question = await create_question_with_code_file_serverjs
    result = await question_running_service.run_server(
        question_id=question.id,
        code_language="javascript",
        session=db_session,
    )
    quiz_data = result.quiz_response
    assert QuizData.model_validate(quiz_data)


@pytest.mark.asyncio
async def test_running_server_js_check_quiz_params(
    create_question_with_code_file_serverjs, db_session
):
    question = await create_question_with_code_file_serverjs
    result = await question_running_service.run_server(
        question_id=question.id,
        code_language="javascript",
        session=db_session,
    )

    quiz_data = result.quiz_response
    assert quiz_data != None
    params = quiz_data.params
    assert params == {"a": 1, "b": 2}


@pytest.mark.asyncio
async def test_running_server_js_check_quiz_correct_answers(
    create_question_with_code_file_serverjs, db_session
):
    question = await create_question_with_code_file_serverjs
    result = await question_running_service.run_server(
        question_id=question.id,
        code_language="javascript",
        session=db_session,
    )
    quiz_data = result.quiz_response
    assert quiz_data != None
    correct_answers = quiz_data.correct_answers
    assert correct_answers == {"sum": 3}


@pytest.mark.asyncio
async def test_running_server_js_check_quiz_logs(
    create_question_with_code_file_serverjs, db_session
):
    question = await create_question_with_code_file_serverjs
    result = await question_running_service.run_server(
        question_id=question.id,
        code_language="javascript",
        session=db_session,
    )
    quiz_data = result.quiz_response
    assert quiz_data != None
    logs = quiz_data.logs

    # value logs
    assert logs_contain(logs, "This is the value of a", "1")
    assert logs_contain(logs, "This is the value of b", "2")
    assert logs_contain(logs, "Here is a structure")
    assert logs_contain(logs, "Here is a structure") and (
        logs_contain(logs, "Here is a structure", '"a"', "1")  # JSON-ish
        or logs_contain(logs, "Here is a structure", "a", "1")  # loose fallback
    )


@pytest.mark.asyncio
async def test_running_server_py_check_response_model(
    create_question_with_code_file_serverpy, db_session
):
    question = await create_question_with_code_file_serverpy
    result = await question_running_service.run_server(
        question_id=question.id,
        code_language="python",
        session=db_session,
    )
    assert CodeRunResponse.model_validate(result)


@pytest.mark.asyncio
async def test_running_server_py_check_successful_response(
    create_question_with_code_file_serverpy, db_session
):
    question = await create_question_with_code_file_serverpy
    result = await question_running_service.run_server(
        question_id=question.id,
        code_language="python",
        session=db_session,
    )
    assert result.success == True


@pytest.mark.asyncio
async def test_running_server_py_check_error_none(
    create_question_with_code_file_serverpy, db_session
):
    question = await create_question_with_code_file_serverpy
    result = await question_running_service.run_server(
        question_id=question.id,
        code_language="python",
        session=db_session,
    )
    assert result.error == None


@pytest.mark.asyncio
async def test_running_server_py_check_quiz_data(
    create_question_with_code_file_serverpy, db_session
):
    question = await create_question_with_code_file_serverpy
    result = await question_running_service.run_server(
        question_id=question.id,
        code_language="python",
        session=db_session,
    )
    quiz_data = result.quiz_response
    assert QuizData.model_validate(quiz_data)


@pytest.mark.asyncio
async def test_running_server_py_check_quiz_params(
    create_question_with_code_file_serverpy, db_session
):
    question = await create_question_with_code_file_serverpy
    result = await question_running_service.run_server(
        question_id=question.id,
        code_language="python",
        session=db_session,
    )

    quiz_data = result.quiz_response
    assert quiz_data != None
    params = quiz_data.params
    assert params == {"a": 1, "b": 2}


@pytest.mark.asyncio
async def test_running_server_py_check_quiz_correct_answers(
    create_question_with_code_file_serverpy, db_session
):
    question = await create_question_with_code_file_serverpy
    result = await question_running_service.run_server(
        question_id=question.id,
        code_language="python",
        session=db_session,
    )
    quiz_data = result.quiz_response
    assert quiz_data != None
    correct_answers = quiz_data.correct_answers
    assert correct_answers == {"sum": 3}


@pytest.mark.asyncio
async def test_running_server_py_check_quiz_logs(
    create_question_with_code_file_serverpy, db_session
):
    question = await create_question_with_code_file_serverpy
    result = await question_running_service.run_server(
        question_id=question.id,
        code_language="python",
        session=db_session,
    )
    quiz_data = result.quiz_response
    assert quiz_data != None
    logs = quiz_data.logs

    # value logs
    # value logs
    assert logs_contain(logs, "This is the value of a", "1")
    assert logs_contain(logs, "This is the value of b", "2")

    # structure log (Python repr): "This is a structure {'params': {'a': 1, 'b': 2}}"
    assert logs_contain(logs, "This is a structure", "'params'")
    assert logs_contain(logs, "This is a structure", "'a'", "1")
    assert logs_contain(logs, "This is a structure", "'b'", "2")


# Testing Error Handlings


## No Files Present
@pytest.mark.asyncio
async def test_running_server_non_supported_language(
    create_question_no_code, db_session
):
    with pytest.raises(HTTPException) as excinfo:
        question = create_question_no_code
        await question_running_service.run_server(
            question_id=question.id,
            code_language="C++",  # type: ignore
            session=db_session,
        )
    assert excinfo.value.status_code == 400
    assert "Unsupported code language" in excinfo.value.detail


@pytest.mark.asyncio
async def test_running_server_no_file_present_python(
    create_question_no_code, db_session
):
    with pytest.raises(HTTPException) as excinfo:
        question = create_question_no_code
        await question_running_service.run_server(
            question_id=question.id,
            code_language="python",
            session=db_session,
        )
    assert excinfo.value.status_code == 400
    assert "no question path" in excinfo.value.detail.lower()


@pytest.mark.asyncio
async def test_running_server_no_file_present_javascript(
    create_question_no_code, db_session
):
    with pytest.raises(HTTPException) as excinfo:
        question = create_question_no_code
        await question_running_service.run_server(
            question_id=question.id,
            code_language="javascript",
            session=db_session,
        )
    assert excinfo.value.status_code == 400
    print("This is the detail")
    print(excinfo.value.detail)
    assert "no question path" in excinfo.value.detail.lower()


@pytest.mark.asyncio
async def test_running_server_no_content_python(
    create_question_empty_file_python, db_session
):
    question = await create_question_empty_file_python
    result = await question_running_service.run_server(
        question_id=question.id,
        code_language="python",
        session=db_session,
    )
    assert CodeRunResponse.model_validate(result)
    assert result.success == False


@pytest.mark.asyncio
async def test_running_server_no_content_javascript(
    create_question_empty_file_js, db_session
):
    question = await create_question_empty_file_js

    result = await question_running_service.run_server(
        question_id=question.id,
        code_language="javascript",
        session=db_session,
    )
    assert CodeRunResponse.model_validate(result)
    assert result.success == False

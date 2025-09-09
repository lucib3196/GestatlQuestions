from pathlib import Path
import pytest
from api.models import Question, File
from api.data import question_db
from api.data import file_db
from backend.src.app_test.unit.database.conftest import db_session


@pytest.fixture
def create_question_with_code_file_serverjs(db_session):
    q_title = "Test_JavaScriptCode"
    filename = "server.js"
    q = Question(
        title=q_title,
        ai_generated=True,
        isAdaptive=False,
        createdBy="Luciano",
        user_id=1,
    )
    q_created = question_db.create_question(q, db_session)
    print("Created question succsefully")
    javascript_path = Path(r"app_test\code_scripts\test.js").resolve()
    f = File(
        filename=filename,
        content=javascript_path.read_text(),
        question_id=q_created.id,
    )
    file_db.add_file(f, db_session)
    return q_created


@pytest.fixture
def create_question_with_code_file_serverpy(db_session):
    q_title = "Test_PythonCode"
    filename = "server.py"
    q = Question(
        title=q_title,
        ai_generated=True,
        isAdaptive=False,
        createdBy="Luciano",
        user_id=1,
    )
    q_created = question_db.create_question(q, db_session)
    python_path = Path(r"app_test\code_scripts\test.py").resolve()
    f = File(
        filename=filename,
        content=python_path.read_text(),
        question_id=q_created.id,
    )
    file_db.add_file(f, db_session)
    return q_created


@pytest.fixture
def create_question_no_code(db_session):
    q_title = "Test_NoCode"
    q = Question(
        title=q_title,
        ai_generated=True,
        isAdaptive=False,
        createdBy="Luciano",
        user_id=1,
    )
    q_created = question_db.create_question(q, db_session)
    print("Created question succsefully")
    return q_created


@pytest.fixture
def create_question_empty_file_python(db_session):
    q_title = "Test_PythonEmpty"
    filename = "server.py"
    q = Question(
        title=q_title,
        ai_generated=True,
        isAdaptive=False,
        createdBy="Luciano",
        user_id=1,
    )
    q_created = question_db.create_question(q, db_session)
    print("Created question succsefully")
    f = File(
        filename=filename,
        content="",
        question_id=q_created.id,
    )
    file_db.add_file(f, db_session)
    print(f"Added {q_title} and {filename} to db returning question ")
    return q_created


@pytest.fixture
def create_question_empty_file_js(db_session):
    q_title = "Test_JavaScriptEmpty"
    filename = "server.js"
    q = Question(
        title=q_title,
        ai_generated=True,
        isAdaptive=False,
        createdBy="Luciano",
        user_id=1,
    )
    q_created = question_db.create_question(q, db_session)
    print("Created question succsefully")
    f = File(
        filename=filename,
        content="",
        question_id=q_created.id,
    )
    file_db.add_file(f, db_session)
    print(f"Added {q_title} and {filename} to db returning question ")
    return q_created

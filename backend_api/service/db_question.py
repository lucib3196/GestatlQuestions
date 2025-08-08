from backend_api.model.questions_models import QuestionMetaNew
from backend_api.model.questions_models import Question, File
from backend_api.data.database import SessionDep
import json
from typing import Union, List


async def add_question(question: Question, session: SessionDep):
    session.add(question)
    session.commit()
    session.refresh(question)
    return question


async def add_file(file_obj: File, session: SessionDep):
    if isinstance(file_obj.content, dict):
        file_obj.content = json.dumps(file_obj.content)
    session.add(file_obj)
    session.commit()
    session.refresh(file_obj)
    return file_obj


async def add_question_and_files(
    question: Question, files: dict[str, Union[str, dict]], session: SessionDep
) -> Question:
    question = await add_question(question, session)
    for filename, contents in files.items():
        if isinstance(contents, (dict, list)):
            contents = json.dumps(contents)

            file_obj = File(
                filename=filename, content=contents, question_id=question.id
            )

            await add_file(file_obj, session)
    return question

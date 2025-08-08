from pathlib import Path
import json
from typing import List, Literal, Union
from backend_api.model.questions_models import QuestionMeta, QuestionMetaNew
from code_runner.run_server import run_generate
from fastapi import HTTPException
from collections import Counter
from fastapi.staticfiles import StaticFiles
from pydantic import ValidationError

# Loads up directory and get all the questions
local_questions = Path.cwd() / "./local_questions"
if not local_questions.exists():
    local_questions.mkdir()

questions = [f for f in local_questions.iterdir() if f.is_dir]


def get_question_meta(q):
    metadata_path = Path(q) / "info.json"
    data = json.loads(metadata_path.read_text(encoding="utf-8"))
    return QuestionMeta(**data)


def get_question_meta_new(q):
    qmeta = Path(q) / "qmeta.json"
    if qmeta.exists():
        try:
            data = json.loads(qmeta.read_text(encoding="utf-8"))
            return QuestionMetaNew(**data)
        except Exception as e:
            print(f"Failed to parse {qmeta}: {e}")
    else:
        print(f"Missing file: {qmeta}")
    return None


def get_all_question_meta(questions: list[Path] = questions) -> List[QuestionMeta]:
    return [get_question_meta(q) for q in questions]


def get_all_question_meta_new(
    questions: list[Path] = questions,
) -> List[QuestionMetaNew]:
    return [qmeta for q in questions if (qmeta := get_question_meta_new(q)) is not None]


def filter_questions_new(qfilter: dict):
    all_questions = get_all_question_meta_new()

    def match(q: Union[QuestionMeta, QuestionMetaNew]):
        for key, value in qfilter.items():
            if not hasattr(q, key):
                continue
            attr = getattr(q, key)

            if isinstance(attr, list):

                if any(value.lower() == a.lower() for a in attr):
                    return True
                else:
                    return False
            else:
                if str(attr).lower() != str(value).lower():
                    return False
        return True

    return [q for q in all_questions if match(q)]


def filter_questions(qfilter: dict):
    all_questions = get_all_question_meta()

    def match(q: Union[QuestionMeta, QuestionMetaNew]):
        for key, value in qfilter.items():
            if not hasattr(q, key):
                continue
            attr = getattr(q, key)

            if isinstance(attr, list):
                if value not in attr:
                    return False
            else:
                if str(attr).lower() != str(value).lower():
                    return False
        return True

    return [q for q in all_questions if match(q)]


def get_unique_values_with_counts(key: str):
    all_questions = get_all_question_meta()
    value_counter = Counter()

    for q in all_questions:
        if not hasattr(q, key):
            continue
        attr = getattr(q, key)
        if isinstance(attr, list):
            for val in attr:
                value_counter[str(val).lower()] += 1
        else:
            value_counter[str(attr).lower()] += 1

    return {
        "key": key,
        "values": [
            {"value": val, "count": count}
            for val, count in sorted(value_counter.items(), key=lambda x: -x[1])
        ],
    }


def get_question_by_title(qtitle: str):
    # check if path exist
    question_path = local_questions / qtitle
    if not question_path.exists():
        raise NotADirectoryError(
            f"Question of title: {qtitle} does not exist in directoy {local_questions}"
        )
    return question_path


def run_server(
    question_title: str, server_type: Literal["javascript", "python"] = "javascript"
):
    try:
        question_path = get_question_by_title(question_title)
    except NotADirectoryError as e:
        raise HTTPException(status_code=400, detail=str(e))

    file_map = {"javascript": "server.js", "python": "server.py"}

    server_filename = file_map.get(server_type)
    if not server_filename:
        raise ValueError(f"Unsupported server typy {server_type}")

    server_path = question_path / server_filename
    try:
        return run_generate(server_path)
    except Exception as e:
        raise RuntimeError(f"Could not run the server file at {server_path}: {e}")


async def get_question_files(question_title: str):
    try:
        question_path = get_question_by_title(question_title)
    except NotADirectoryError as e:
        raise HTTPException(status_code=400, detail=str(e))

    files = [f.name for f in question_path.iterdir() if f.is_file()]

    # check if there are any images
    question_images_path = question_path / "clientFilesQuestion"

    if question_images_path.exists():
        images = [
            Path("clientFilesQuestion") / f.name
            for f in question_images_path.iterdir()
            if f.is_file()
        ]
        files.extend([str(img) for img in images])
    return files


async def get_file(question_title: str, filename: str):
    try:
        question_path = get_question_by_title(question_title)
    except NotADirectoryError as e:
        raise HTTPException(status_code=400, detail=str(e))

    filepath = question_path / str(filename)
    if filepath.exists():
        content = filepath.read_text()
        if isinstance(content, dict):
            content = json.loads(content)
        return content
    else:
        raise HTTPException(
            status_code=400, detail="Something went wrong reading the file content"
        )


def get_question_html(question_title: str) -> str:
    try:
        question_path = get_question_by_title(question_title)
    except NotADirectoryError as e:
        raise HTTPException(status_code=400, detail=str(e))

    question_filename = question_path / "question.html"
    if not question_filename:
        raise HTTPException(
            status_code=404, detail=f"Question {question_title} not found"
        )
    return question_filename.read_text()


def get_question_newformat(question_title: str):
    try:
        question_path = get_question_by_title(question_title)
    except NotADirectoryError as e:
        raise HTTPException(status_code=400, detail=str(e))

    question_filename = question_path / "qmeta.json"
    if not question_filename:
        if not question_filename:
            raise HTTPException(
                status_code=404,
                detail=f"Question {question_title} not found or not formatted for new render",
            )
    return question_filename.read_text()


def update_file(question_title: str, filename: str, newcontent: str):
    try:
        question_path = get_question_by_title(question_title)
    except NotADirectoryError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Handle content type
    if isinstance(newcontent, dict):
        newcontent = json.dumps(newcontent)
    filepath = question_path / str(filename)
    if filepath.exists():
        filepath.write_text(newcontent, encoding="utf-8")
        return {"detail": "File updated successfully"}
    else:
        raise HTTPException(
            status_code=400, detail="Failed to update file. File does not exist"
        )


async def create_file(question_title: str, filename: str):
    """
    Creates a new empty file under the given question's directory.
    Raises an error if the file already exists or if the question path is invalid.
    """
    try:
        question_path = get_question_by_title(question_title)  # Should return a Path
    except NotADirectoryError as e:
        raise HTTPException(status_code=400, detail=str(e))

    filepath = question_path / filename

    if filepath.exists():
        raise HTTPException(status_code=409, detail="File already exists")

    filepath.write_text("")
    return {"detail": "File added"}


from .file_management import validate_file
from fastapi import UploadFile


async def upload_question_file(file: UploadFile, question_title: str):

    try:
        question_path = get_question_by_title(question_title)  # Should return a Path
    except NotADirectoryError as e:
        raise HTTPException(status_code=400, detail=str(e))

    try:
        await validate_file(file)

        filename = file.filename
        content = await file.read()

        if file.content_type == "image/jpeg":
            image_path = question_path / "clientFilesQuestion" / str(filename)
            image_path.parent.mkdir(parents=True, exist_ok=True)

            image_path.write_bytes(content)
        else:
            filepath = question_path / str(filename)
            filepath.write_bytes(content)
        return {"detail": "File uploaded successfully", "filename": filename}

    except Exception as e:
        raise HTTPException(status_code=400, detail=e)

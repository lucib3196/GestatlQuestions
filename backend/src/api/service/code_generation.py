import asyncio
import json
import os
import shutil
import tempfile
from typing import Any, Dict, List, Sequence, Tuple

from fastapi import HTTPException, UploadFile, status
from pydantic import ValidationError

from src.ai_workspace.agents.code_generators.v5.main_image import (
    State as ImageState,
    app as image_generator_v5,
)
from src.ai_workspace.agents.code_generators.v5.main_text import (
    CodeGenFinal,
    State as TextState,
    app as text_generator_v5,
)
from src.ai_workspace.utils import to_serializable, validate_llm_output
from src.api.models import FileData, QuestionData
from src.utils import to_bool


def validate_data(gc: CodeGenFinal | dict) -> CodeGenFinal:
    """
    Validates or converts the input into a CodeGenFinal model.
    Accepts either a dict or an existing CodeGenFinal instance.
    """
    try:
        if isinstance(gc, dict):
            gc = CodeGenFinal.model_validate(gc)
        elif not isinstance(gc, CodeGenFinal):
            raise TypeError(f"Unexpected type: {type(gc)}")
        return gc
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not validate CodeGenFinal. Received type: {type(gc)}. Error: {e}",
        )


def process_question_data(gc: CodeGenFinal | dict) -> QuestionData:
    gc = validate_data(gc)
    metadata = gc.metadata
    if not metadata:
        raise ValueError("Metadata for question is empty")
    qpayload = QuestionData(
        title=metadata.title,
        ai_generated=True,
        isAdaptive=to_bool(metadata.isAdaptive),
        topics=metadata.topics,
        languages=metadata.language or [],
        qtypes=metadata.qtype or [],
    )
    return qpayload


def process_code_files(gc: CodeGenFinal | dict) -> List[FileData]:
    try:
        gc = validate_data(gc)
        files_data: Dict[str, Any] = dict(gc.files_data or {})

        # Get the question payload
        files_data["raw_data.json"] = to_serializable(gc)
        fd_list: List[FileData] = [
            FileData(filename=filename, content=to_serializable(content))
            for filename, content in files_data.items()
        ]
        return fd_list
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not get filedata {e}",
        )


async def process_gestalt_data(gc: CodeGenFinal) -> Tuple[List[FileData], QuestionData]:
    file_data = process_code_files(gc)
    question_data = process_question_data(gc)
    file_data.append(
        FileData(
            filename="info.json", content=json.dumps(to_serializable(question_data))
        )
    )
    return (file_data, question_data)


async def run_text(
    text: str,
) -> Sequence[Tuple[List[FileData], QuestionData]]:
    """Generate questions from input text, store them, and return results.

    1. Calls the text generator with the given text.
    2. Validates the output using TextState model.
    3. Processes each generated question via `process_output`.
    4. Handles and wraps exceptions in HTTP-friendly errors.

    Args:
        text: The prompt or source text for generating questions.
        session: Database session dependency.
        additional_meta: Optional metadata to attach to each created question.

    Returns:
        A dict with 'success': True and 'questions': list of created question records.

    Raises:
        HTTPException:
            - 400: For validation or missing metadata errors.
            - 500: For unexpected server errors.
    """
    try:
        llm_out = await text_generator_v5.ainvoke(TextState(text=text))
        results: TextState = validate_llm_output(llm_out, TextState)
        tasks = [process_gestalt_data(gc) for gc in results.gestalt_code]
        data = await asyncio.gather(*tasks)
        return data

    except (ValidationError, ValueError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid generated output: {e}",
        )
    except HTTPException:
        # Re-raise for upstream handling
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


async def run_image(
    files: List[UploadFile],
) -> Sequence[Tuple[List[FileData], QuestionData]]:
    try:

        temp_filepaths = []
        with tempfile.TemporaryDirectory() as tmpdir:
            for f in files:
                temp_path = os.path.join(tmpdir, str(f.filename))
                with open(temp_path, "wb") as buffer:
                    shutil.copyfileobj(f.file, buffer)
                temp_filepaths.append(temp_path)
            results = await image_generator_v5.ainvoke(
                ImageState(image_paths=temp_filepaths)
            )

            validated_results: ImageState = validate_llm_output(results, ImageState)
            tasks = [
                process_gestalt_data(
                    gc,
                )
                for gc in validated_results.gestalt_code
            ]
            data = await asyncio.gather(*tasks)
            return data
    except (ValidationError, ValueError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid generated output: {e}",
        )
    except HTTPException:
        # Re-raise for upstream handling
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )

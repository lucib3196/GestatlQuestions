# --- Standard Library ---
import asyncio
import os
import shutil
import tempfile
from copy import deepcopy
from typing import Any, Dict, List, Optional

# --- Third-Party ---
from fastapi import HTTPException, UploadFile, status
from pydantic import ValidationError
from src.utils import to_bool

# --- Internal ---
from ai_workspace.utils import to_serializable, validate_llm_output
from ai_workspace.agents.code_generators.v5.main_text import (
    app as text_generator_v5,
    CodeGenFinal,
    State as TextState,
)
from ai_workspace.agents.code_generators.v5.main_image import (
    app as image_generator_v5,
    State as ImageState,
)
from src.api.database import SessionDep
from . import question_crud, question_storage_service


async def process_output(
    gc: CodeGenFinal,
    session: SessionDep,
    meta: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Process a generated question, persist it, and return created question data.

    Args:
        gc: A CodeGenFinal object containing question files and metadata.
        session: Database session dependency.
        meta: Optional metadata dict (e.g., createdBy, user_id).

    Returns:
        A dictionary containing the created question data.

    Raises:
        ValueError: If the generated question lacks necessary metadata.
    """
    meta = deepcopy(meta) if meta else {}
    files_data: Dict[str, Any] = dict(gc.files_data or {})

    if not gc.metadata:
        raise ValueError("Metadata not present in question")

    metadata = gc.metadata
    question_payload = gc.question_payload

    files_data["metadata.json"] = to_serializable(metadata)
    files_data["question_payload.json"] = to_serializable(question_payload)

    q_payload: Dict[str, Any] = {
        "title": meta.get("title") or metadata.title,
        "ai_generated": True,
        "isAdaptive": to_bool(metadata.isAdaptive),
        "createdBy": meta.get("createdBy"),
        "user_id": meta.get("user_id"),
        "topics": metadata.topics,
        "languages": metadata.language,
        "qtypes": metadata.qtype,
    }

    q = await question_crud.create_question(q_payload, session)
    for filename, content in files_data.items():
        question_storage_service.add_file_to_question(
            question_id=q.id,
            filename=filename,
            content=content,
            session=session,
        )

    created = await question_crud.get_question_data(question_id=q.id, session=session)
    return created


async def run_text(
    text: str,
    session: SessionDep,
    additional_meta: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
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
    meta = deepcopy(additional_meta) if additional_meta else {}

    try:
        llm_out = await text_generator_v5.ainvoke(TextState(text=text))
        results: TextState = validate_llm_output(llm_out, TextState)

        tasks = [
            process_output(gc, session=session, meta=meta)
            for gc in results.gestalt_code
        ]
        created_questions: List[Dict[str, Any]] = await asyncio.gather(*tasks)

        return {"success": True, "questions": created_questions}

    except (ValidationError, ValueError) as e:
        # Clear, user-facing 400-level error for bad LLM output or missing metadata
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid generated output: {e}",
        )
    except HTTPException:
        # Re-raise for upstream handling
        raise
    except Exception as e:
        # Unanticipated errors — return a generic 500
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


async def run_image(
    files: List[UploadFile], session: SessionDep, meta: Optional[Dict[str, Any]] = None
):
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
                process_output(gc, session=session, meta=meta)
                for gc in validated_results.gestalt_code
            ]
            created_questions: List[Dict[str, Any]] = await asyncio.gather(*tasks)

            return {"success": True, "questions": created_questions}
    except (ValidationError, ValueError) as e:
        # Clear, user-facing 400-level error for bad LLM output or missing metadata
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid generated output: {e}",
        )
    except HTTPException:
        # Re-raise for upstream handling
        raise
    except Exception as e:
        # Unanticipated errors — return a generic 500
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )

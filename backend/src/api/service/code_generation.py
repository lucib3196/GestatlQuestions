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

# --- Internal / Project ---
from src.ai_workspace.agents.code_generators.v5.main_image import (
    app as image_generator_v5,
    State as ImageState,
)
from src.ai_workspace.agents.code_generators.v5.main_text import (
    app as text_generator_v5,
    CodeGenFinal,
    State as TextState,
)
from src.ai_workspace.utils import to_serializable, validate_llm_output
from src.api.database import SessionDep
from src.api.models import FileData
from src.utils import to_bool
from src.api.models.question import QuestionData


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


# async def run_text(
#     text: str,
#     session: SessionDep,
#     qm: QuestionManagerDependency,
#     additional_meta: Optional[Dict[str, Any]] = None,
# ) -> Dict[str, Any]:
#     """Generate questions from input text, store them, and return results.

#     1. Calls the text generator with the given text.
#     2. Validates the output using TextState model.
#     3. Processes each generated question via `process_output`.
#     4. Handles and wraps exceptions in HTTP-friendly errors.

#     Args:
#         text: The prompt or source text for generating questions.
#         session: Database session dependency.
#         additional_meta: Optional metadata to attach to each created question.

#     Returns:
#         A dict with 'success': True and 'questions': list of created question records.

#     Raises:
#         HTTPException:
#             - 400: For validation or missing metadata errors.
#             - 500: For unexpected server errors.
#     """
#     meta = deepcopy(additional_meta) if additional_meta else {}

#     try:
#         llm_out = await text_generator_v5.ainvoke(TextState(text=text))
#         results: TextState = validate_llm_output(llm_out, TextState)

#         tasks = [
#             process_output(gc, session=session, meta=meta, qm=qm)
#             for gc in results.gestalt_code
#         ]
#         created_questions: List[Dict[str, Any]] = await asyncio.gather(*tasks)

#         return {"success": True, "questions": created_questions}

#     except (ValidationError, ValueError) as e:
#         # Clear, user-facing 400-level error for bad LLM output or missing metadata
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail=f"Invalid generated output: {e}",
#         )
#     except HTTPException:
#         # Re-raise for upstream handling
#         raise
#     except Exception as e:
#         # Unanticipated errors — return a generic 500
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=str(e),
#         )


# async def run_image(
#     files: List[UploadFile],
#     session: SessionDep,
#     qm: QuestionManagerDependency,
#     meta: Optional[Dict[str, Any]] = None,
# ):
#     try:

#         temp_filepaths = []
#         with tempfile.TemporaryDirectory() as tmpdir:
#             for f in files:
#                 temp_path = os.path.join(tmpdir, str(f.filename))
#                 with open(temp_path, "wb") as buffer:
#                     shutil.copyfileobj(f.file, buffer)
#                 temp_filepaths.append(temp_path)
#             results = await image_generator_v5.ainvoke(
#                 ImageState(image_paths=temp_filepaths)
#             )

#             validated_results: ImageState = validate_llm_output(results, ImageState)
#             tasks = [
#                 process_output(gc, session=session, meta=meta, qm=qm)
#                 for gc in validated_results.gestalt_code
#             ]
#             created_questions: List[Dict[str, Any]] = await asyncio.gather(*tasks)

#             return {"success": True, "questions": created_questions}
#     except (ValidationError, ValueError) as e:
#         # Clear, user-facing 400-level error for bad LLM output or missing metadata
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail=f"Invalid generated output: {e}",
#         )
#     except HTTPException:
#         # Re-raise for upstream handling
#         raise
#     except Exception as e:
#         # Unanticipated errors — return a generic 500
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=str(e),
#         )

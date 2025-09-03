from __future__ import annotations

# Stdlib
from typing import Optional
from fastapi import Body

# Third-party
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,  # <-- FastAPI's file parameter helper
)
from starlette import status
from pydantic import BaseModel

# Internal
from backend_api.data.database import get_session
from backend_api.service import user

router = APIRouter(prefix="/codegenerator")

from backend_api.service.code_generation import run_text


# Loads up directory and get all the questions
class TextGenInput(BaseModel):
    question_title: Optional[str] = None
    question: str


@router.post("/v5/text_gen")
async def generate_question_v5(
    data: TextGenInput = Body(..., embed=True),
    current_user=Depends(user.get_current_user),
    session=Depends(get_session),
):
    user_id = await user.get_user_by_name(
        username=current_user.username,
        email=current_user.email,
        session=session,
    )
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Must be logged in to use generation",
        )
    additional_meta = {
        "createdBy": current_user.email,
        "user_id": user_id,
        "title": data.question_title or None,
    }
    try:
        return await run_text(
            text=data.question, session=session, additional_meta=additional_meta
        )
    except HTTPException as e:
        raise e


# @router.post("/v4/text_gen/")
# async def generate_question_v4(
#     data: List[TextGenInput] = Body(..., embed=True),
#     current_user=Depends(user.get_current_user),
#     session=Depends(get_session),
# ):
#     user_id = await user.get_user_by_name(
#         username=current_user.username,
#         email=current_user.email,
#         session=session,
#     )
#     if not user_id:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Must be logged in to use generation",
#         )

#     # 1) Run all extractions concurrently
#     extraction_results = await asyncio.gather(
#         *(text_gen.ainvoke(InputState(text=item.question)) for item in data)
#     )

#     # 2) Validate/normalize, collect DB-save tasks
#     save_tasks = []
#     for i, res in enumerate(extraction_results):
#         state = IntermediateState.model_validate(res)
#         raw_list = state.code_results or []
#         code_results = raw_list if isinstance(raw_list, list) else [raw_list]

#         title = (
#             data[i].question_title or ""
#         )  # may be None; pass through or set a default
#         for cr in code_results:
#             save_tasks.append(
#                 generated_code_repository.add_generated_db(
#                     cr,
#                     user_id=user_id,
#                     title=title,
#                     session=session,
#                 )
#             )

#     # 3) Save everything concurrently and return
#     questions = await asyncio.gather(*save_tasks)
#     return questions


# @router.post("/v4/image_gen/")
# async def generate_question_image_v4(
#     files: List[UploadFile],
#     session=Depends(get_session),
#     current_user=Depends(user.get_current_user),
# ):
#     logger.debug("This is the current user", current_user)
#     # Validate user data
#     user_id = await user.get_user_by_name(
#         username=current_user.username,
#         email=current_user.email,
#         session=session,
#     )

#     if not user_id:
#         return HTTPException(
#             status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
#             detail="Must be logged in to use generation",
#         )

#     temp_filepaths = []
#     with tempfile.TemporaryDirectory() as tmpdir:
#         for f in files:
#             temp_path = os.path.join(tmpdir, str(f.filename))
#             with open(temp_path, "wb") as buffer:
#                 shutil.copyfileobj(f.file, buffer)
#             temp_filepaths.append(temp_path)
#         results = await image_gen.ainvoke(ImageInputState(image_paths=temp_filepaths))  # type: ignore
#         state = ImageOutputState.model_validate(results)
#         raw_list = state.code_results or []
#         code_results = raw_list if isinstance(raw_list, list) else [raw_list]
#         tasks = [
#             generated_code_repository.add_generated_db(
#                 cr, user_id=user_id, title="", session=session
#             )
#             for cr in code_results
#         ]
#         questions = await asyncio.gather(*tasks)
#     return questions

# --- Standard Library ---
from typing import Optional

# --- Third-Party ---
from fastapi import APIRouter, HTTPException, UploadFile
from starlette import status

# --- Internal ---
from src.api.core.config import get_settings
from src.api.core import logger
from src.api.service.question_manager import QuestionManagerDependency
from src.api.service.storage_manager import StorageDependency
from src.api.models.models import Question
from src.api.models import *
from src.api.service.file_service import FileService
from src.utils import serialized_to_dict
from src.utils import safe_dir_name


router = APIRouter(
    prefix="/questions",
    tags=[
        "questions",
    ],
)


app_settings = get_settings()


def parse_question_payload(
    question: str | dict | Question,
    additional_metadata: Optional[str | AdditionalQMeta],
):
    logger.debug(f"Received question {question} type of {type(question)}")
    question = serialized_to_dict(question, Question)
    if additional_metadata:
        question.update(serialized_to_dict(additional_metadata, AdditionalQMeta))
    return question


async def parse_file_upload(file: UploadFile) -> FileData:
    f = await FileService("").validate_file(file)
    content = await f.read()
    await f.seek(0)
    fd = FileData(filename=str(f.filename), content=content)
    return fd


@router.post("/")
async def create_question(
    qm: QuestionManagerDependency,
    storage: StorageDependency,
    question: QuestionData,
) -> Question:
    """
    Create a new question, store it in the database, and initialize its corresponding storage path.

    This function performs three main operations:
    1. Creates a new `Question` entry in the database via the `QuestionManagerDependency`.
    2. Generates a sanitized directory name for the question based on its title and ID.
    3. Initializes the appropriate storage path (local or cloud) and updates the database record
       with the correct relative path reference.

    Args:
        qm (QuestionManagerDependency): Manages database interactions for creating and committing the question.
        storage (StorageDependency): Handles file system or cloud storage initialization for the question.
        question (QuestionData): Input data model containing details of the question to be created.

    Returns:
        Question: The created `Question` SQLModel instance with updated storage path information.

    Raises:
        Exception: Propagates any error encountered during creation or storage initialization.
    """
    try:
        qcreated = await qm.create_question(question)

        # Handles the directoru creation for the question
        path_name = safe_dir_name(f"{qcreated.title}_{str(qcreated.id)[:8]}")

        # Creates the actual path
        path = storage.create_storage_path(path_name)

        # Storing the relative path in db
        relative_path = storage.get_relative_storage_path(path)
        if app_settings.STORAGE_SERVICE == "local":
            qcreated.local_path = Path(str(relative_path)).as_posix()
        elif app_settings.STORAGE_SERVICE == "cloud":
            qcreated.blob_path = Path(str(relative_path)).as_posix()
        # Commit the changes
        qm.session.commit()

        return qcreated
    except Exception:
        raise


@router.delete("/")
async def delete_all(
    qm: QuestionManagerDependency,
    storage: StorageDependency,
    delete_storage: bool = False,
):
    """
    Delete all questions from the database, with an optional flag to remove the entire storage directory.

    This endpoint removes every question record from the database. When the `delete_storage` flag is set to `True`,
    it additionally deletes the entire storage directory associated with question files.
    **Use caution**: enabling this flag will permanently remove *all* files and subdirectories under the storage path.

    Args:
        qm (QuestionManagerDependency): Handles bulk deletion of all question records from the database.
        storage (StorageDependency): Provides access to the file storage system (local or cloud).
        delete_storage (bool, optional): When `True`, deletes the entire storage directory on disk or in cloud storage.
            This operation is irreversible and should be used only when you are certain that all files can be removed.
            Defaults to `False`.

    Returns:
        dict: A confirmation message indicating successful deletion of all questions (and optionally the storage).

    Raises:
        Exception: Propagates any database or file system errors encountered during deletion.
    """
    try:
        qm.delete_all_questions()
        path = Path(storage.get_base_path())
        if delete_storage:
            logger.info("Deleting storage")
            storage.hard_delete()
        return {"status": "ok", "detail": "Deleted all questions"}
    except Exception as e:
        raise


@router.get("/{offset}/{limit}")
async def get_all_questions(
    qm: QuestionManagerDependency, offset: int = 0, limit: int = 100
) -> Sequence[Question]:
    """
    Retrieve a paginated list of all questions stored in the database.

    This endpoint queries the database for all available questions using pagination controls.
    It is primarily used for listing or browsing questions in bulk, supporting efficient
    batch retrieval through the `offset` and `limit` parameters.

    Args:
        qm (QuestionManagerDependency): Dependency responsible for database queries related to questions.
        offset (int, optional): The starting index for pagination. Defaults to 0.
        limit (int, optional): The maximum number of questions to retrieve. Defaults to 100.

    Returns:
        Sequence[Question]: A sequence of `Question` SQLModel instances representing the retrieved questions.

    Raises:
        Exception: Propagates any unexpected database or query-related errors during retrieval.
    """
    try:
        return qm.get_all_questions(offset, limit)
    except Exception:
        raise


@router.get("/{id}")
async def get_question(id: str | UUID, qm: QuestionManagerDependency) -> Question:
    """
    Retrieve a single question from the database by its ID.

    This endpoint queries the database for a specific `Question` instance.
    If no question is found matching the provided identifier, an HTTP 404 error is raised.

    Args:
        id (str | UUID): The unique identifier of the question to retrieve.
        qm (QuestionManagerDependency): Manages database operations for question retrieval.

    Returns:
        Question: The retrieved `Question` SQLModel instance.

    Raises:
        HTTPException: If the question does not exist in the database.
        Exception: Propagates any unexpected database or retrieval errors.
    """
    try:
        question = qm.get_question(id)
        if not question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Could not find question {id}",
            )
        return question
    except Exception:
        raise


@router.get("/{id}/all_data")
async def get_question_all_data(
    id: str | UUID, qm: QuestionManagerDependency
) -> QuestionMeta:
    """
    Retrieve a question and all associated metadata by its ID.

    This function fetches both the question record and its related metadata
    (such as relationships, tags, and supplemental data) for comprehensive inspection.

    Args:
        id (str | UUID): The unique identifier of the question to retrieve.
        qm (QuestionManagerDependency): Provides access to detailed question data and metadata.

    Returns:
        QuestionMeta: The combined question and metadata information.

    Raises:
        Exception: Propagates any database or data access errors encountered during retrieval.
    """
    try:
        return await qm.get_question_data(id)
    except Exception:
        raise


@router.delete("/{id}")
async def delete_question(
    id: str | UUID, qm: QuestionManagerDependency, storage: StorageDependency
):
    """
    Delete a question from the database and remove any associated stored files.

    This endpoint performs two operations:
    1. Retrieves the question by ID and ensures it exists.
    2. Deletes the database record and removes its storage location (local or cloud),
       depending on the active storage backend.

    If the question exists in the DB but does not have an associated storage path,
    the question is still deleted from the database, and a warning is logged to indicate
    that storage cleanup could not be performed.

    Args:
        id (str | UUID): The unique identifier of the question to delete.
        qm (QuestionManagerDependency): Handles database deletion of the question.
        storage (StorageDependency): Deletes storage resources, either locally or in cloud storage.

    Returns:
        dict: A confirmation response indicating successful deletion.

    Raises:
        HTTPException: If the question does not exist.
        Exception: Propagates any unexpected errors encountered during deletion.
    """
    try:
        question = await get_question(id, qm)
        if not question:
            raise HTTPException(
                status_code=404, detail="Question not found nothing to delete"
            )
        question_path = None
        if app_settings.STORAGE_SERVICE == "cloud":
            question_path = question.blob_path
        elif app_settings.STORAGE_SERVICE == "local":
            question_path = Path(str(question.local_path)).resolve()

        assert qm.delete_question(id)
        if not question_path:
            logger.warning(
                "Question of ID: {question.id} Title: {question.title} does not have a storage path will still delete from database but may cause issues"
            )
            return {"status": "ok", "detail": "Deleted Question"}

        storage.delete_storage(question_path)
        return {"status": "ok", "detail": "Deleted Question"}

    except Exception:
        raise


@router.put("/{id}")
async def update_question(
    id: str | UUID, update: QuestionData, qm: QuestionManagerDependency
):
    try:
        return await qm.update_question(id, update)
    except Exception:
        raise




# @router.get("/{qid}/files", status_code=status.HTTP_200_OK)
# async def get_question_files(
#     qid: str | UUID, session: SessionDep, qm: QuestionManagerDependency
# ) -> SuccessFileResponse:
#     try:
#         files = await qm.get_all_files(qid, session)
#         return SuccessFileResponse(
#             status=200,
#             detail="Retrieved files succesfully",
#             filedata=[],
#             filepaths=files,
#         )

#     except HTTPException:
#         raise
#     except Exception as e:
#         # Log here if possible
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Could not retrieve files names: {e}",
#         )


# @router.get("/{qid}/files/{filename}", status_code=status.HTTP_200_OK)
# async def read_question_file(
#     qid: str | UUID, filename: str, session: SessionDep, qm: QuestionManagerDependency
# ) -> SuccessDataResponse:
#     try:
#         data = await qm.read_file(qid, session, filename)
#         assert data
#         data = data.decode("utf-8")
#         return SuccessDataResponse(
#             status=status.HTTP_200_OK, detail="Successful", data=data
#         )
#     except HTTPException:
#         raise
#     except Exception as e:
#         # Log here if possible
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Could not retrieve files names: {e}",
#         )


# @router.get("/{qid}/files_data", status_code=status.HTTP_200_OK)
# async def get_question_files_data(
#     qid: str | UUID, session: SessionDep, qm: QuestionManagerDependency
# ) -> SuccessFileResponse:
#     try:
#         logger.debug("Attempting to retrieve filedata")

#         filedata = await qm.read_all_files(qid, session)
#         return SuccessFileResponse(
#             status=200,
#             detail="Retrieved files succesfully",
#             filedata=filedata,
#             filepaths=[],
#         )
#     except HTTPException:
#         raise
#     except Exception as e:

#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Could not retrieve files data: {e}",
#         )


# # Update
# @router.put("/update_file", status_code=200)
# async def update_file(
#     payload: UpdateFile, session: SessionDep, qm: QuestionManagerDependency
# ):
#     try:
#         new_content = FileData(filename=payload.filename, content=payload.new_content)
#         result = await qm.save_file_to_question(
#             payload.question_id, session, new_content, overwrite=True
#         )
#         return {"success": True, "result": result}
#     except HTTPException:
#         raise
#     except Exception as e:
#         # Log here if possible
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Could not write file content: {e}",
#         )


# # TODO add test web
# @router.patch("/update_question/{quid}", status_code=200)
# async def update_question(
#     quid: Union[str, UUID],
#     session: SessionDep,
#     updates: QuestionMeta,
#     qm: QuestionManagerDependency,
# ):
#     try:
#         kwargs = updates.model_dump(exclude_none=True)
#         norm_k = normalize_kwargs(kwargs)
#         result = await qm.update_question(question_id=quid, session=session, **norm_k)
#         return result
#     except HTTPException as e:
#         raise e
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
#         )


# # Special


# @router.post("/filter_questions")
# async def filter_questions(
#     session: SessionDep,
#     filters: QuestionMeta,
#     qm: QuestionManagerDependency,
# ):
#     """
#     Filter questions based on metadata.

#     Args:
#         session (SessionDep): Database session dependency.
#         filters (QuestionMeta): Filter criteria.
#     """
#     try:
#         logger.debug("Filtering questions")
#         kwargs = filters.model_dump(exclude_none=True)
#         norm_k = normalize_kwargs(kwargs)
#         result = await qm.filter_questions(session, **norm_k)
#         return result
#     except HTTPException as e:
#         raise e
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
#         )


# # TODO complete this
# @router.post("/{qid}/files")
# async def upload_files_to_question(
#     qid: str | UUID,
#     files: List[UploadFile],
#     session: SessionDep,
#     qm: QuestionManagerDependency,
# ):
#     try:
#         fd_list = (
#             await asyncio.gather(*[parse_file_upload(f) for f in files])
#             if files
#             else []
#         )
#         await qm.save_files_to_question(qid, session, fd_list, overwrite=True)
#         return SuccessfulResponse(
#             status=200,
#             detail="Uploaded files succesfully",
#         )
#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Could not upload files to question: {e}",
#         )


# @router.post("/{qid}/download")
# async def download_question(
#     qid: str | UUID, session: SessionDep, qm: QuestionManagerDependency
# ):
#     try:
#         data = await qm.download_question(session, qid)
#         if not isinstance(data, io.BytesIO):
#             buffer = io.BytesIO(data)
#         else:
#             buffer = data

#         zip_name = await qm.get_question_identifier(qid, session)

#         return StreamingResponse(
#             buffer,
#             media_type="application/zip",
#             headers={"Content-Disposition": f'attachment; filename="{zip_name}.zip"'},
#         )
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="Could not download question",
#         )


# import zipfile


# # TODO: Add test
# @router.post("/download_starter")
# async def download_starter(qm: QuestionManagerDependency):
#     try:
#         data = await qm.download_starter_templates()

#         # Create a new in-memory buffer
#         buffer = io.BytesIO()

#         # Open a ZipFile to write into that buffer
#         with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
#             for folder, bdata in data.items():
#                 # Ensure bdata is BytesIO or bytes
#                 if isinstance(bdata, io.BytesIO):
#                     content = bdata.getvalue()
#                 else:
#                     content = bdata

#                 # Write it into the zip archive
#                 zf.writestr(f"{folder}.zip", content)

#         # Reset pointer so StreamingResponse can read from start
#         buffer.seek(0)

#         return StreamingResponse(
#             buffer,
#             media_type="application/zip",
#             headers={
#                 "Content-Disposition": 'attachment; filename="starter_templates.zip"'
#             },
#         )
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Could not download starter: {e}",
#         )

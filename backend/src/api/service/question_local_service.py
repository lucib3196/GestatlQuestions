from __future__ import annotations

# --- Standard Library ---
import asyncio
from pathlib import Path
import json

# --- Third-Party ---
from sqlmodel import select
from src.utils import pick

# --- Internal ---
from src.api.core import settings
from src.api.database import SessionDep, get_session
from src.api.models.question_model import Question
from src.api.service import question_storage_service as qs
from src.api.service import question_crud as qc
from src.utils import normalize_kwargs
from fastapi import HTTPException
from src.api.core import logger
from src.api.response_models import FileData
from src.utils import convert_uuid
from src.utils import normalize_timestamps
from src.ai_workspace.utils import to_serializable


async def read_file_async(path: Path) -> str:
    loop = asyncio.get_running_loop()
    # offload file IO
    return await loop.run_in_executor(None, path.read_text, "utf-8")


def check_for_new_folders(session: SessionDep):
    base_dir = Path(settings.QUESTIONS_PATH).resolve()

    all_q = session.exec(select(Question)).all()
    db_folders = {
        parts[1]
        for q in all_q
        if q.local_path and (parts := str(q.local_path).split("/")) and len(parts) > 1
    }
    disk_folders = {p.name for p in base_dir.iterdir() if p.is_dir()}

    new_folders = disk_folders - db_folders

    metadata_not_found = []
    metadata_found = []
    for folder in new_folders:
        metadata_path = base_dir / folder / "metadata.json"
        if not metadata_path.exists():
            metadata_not_found.append(folder)
        else:
            metadata_found.append(folder)

    return metadata_not_found, metadata_found


async def handle_metadata_found(metadata_found: list[str], session: SessionDep):
    base_dir = Path(settings.QUESTIONS_PATH).resolve()
    for m in metadata_found:
        metadata_path = base_dir / m / "metadata.json"

        if not metadata_path.exists():
            logger.warning(f"Metadata file not found: {metadata_path}")
            continue

        try:
            text = await read_file_async(metadata_path)
            content = json.loads(text)
        except Exception as e:
            logger.error(f"Failed to read/parse {metadata_path}: {e}")
            continue

        content = json.loads(metadata_path.read_text(encoding="utf-8"))

        # get question id
        question_id = convert_uuid(content.get("id", ""))
        is_question = False
        # Check if exists, or if 404 → treat appropriately
        if question_id:
            try:
                await qc.get_question_by_id(question_id, session=session)
                is_question = True
            except HTTPException as e:
                if e.status_code == 404:
                    is_question = False
                else:
                    # some other error, log and skip?
                    logger.error(f"Error retrieving question by id {question_id}: {e}")
                    continue

        try:
            if not is_question:
                # create new
                await qs.create_question_full(content, session, existing=True)
            else:
                # edit meta
                content.pop("id", None)
                content = normalize_timestamps(content)

                # Now normalize the rest of the fields
                data = await qc.edit_question_meta(
                    question_id,
                    session,
                    **normalize_kwargs(content),
                )
                metadata = FileData(
                    filename="metadata.json", content=json.dumps(data, default=str)
                )
                await qs.write_files_to_directory(
                    question_id=question_id, files_data=[metadata], session=session
                )
        except Exception as e:
            logger.error(
                f"Failed to process metadata for {metadata_path}: {e}, content: {content}"
            )
            continue


if __name__ == "__main__":

    async def main():
        session_gen = get_session()
        session = next(session_gen)
        try:
            _, found = check_for_new_folders(session)
            await handle_metadata_found(found, session)

        finally:
            session.close()  # finalize generator try: next(session_gen) except StopIteration: pass

    asyncio.run(main())

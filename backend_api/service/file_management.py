from typing import Annotated
from fastapi import UploadFile, HTTPException
from typing import List
import os
import asyncio

# Configuration for file size and filetypes
MAX_FILE_SIZE_MB = 5
ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".pdf", ".txt"}
ALLOWED_CONTENT_TYPES = {"image/png", "image/jpeg", "application/pdf"}


async def validate_file(file: UploadFile) -> UploadFile:
    if not file.filename:
        raise HTTPException(status_code=400, detail="There is no file")
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"File of Content type {file.content_type} is not allowed",
        )
    _, ext = os.path.splitext(file.filename)
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Invalid file extension: {ext}")

    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(
            status_code=400, detail=f"{file.filename} exceeds {MAX_FILE_SIZE_MB}MB"
        )
    return file


async def upload_file(file: UploadFile):
    try:
        file = await validate_file(file)
        return {file: file.filename}
    except Exception as e:
        raise HTTPException(status_code=400, detail=e)


async def upload_folder(files: List[UploadFile]):
    upload_dir = "uploaded_folder"
    for f in files:
        f = await validate_file(f)
        contents = await f.read()
        filepath = os.path.join(upload_dir, f.filename or "unnamed_file.txt")
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "wb") as f:
            f.write(contents)
    return {"message": f"Uploaded {len(files)} files successfully"}

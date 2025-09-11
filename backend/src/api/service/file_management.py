from fastapi import UploadFile, HTTPException
from typing import List
import os
from starlette import status
from fastapi import UploadFile, HTTPException
from pathlib import Path
import zipfile

# Configuration for file size and filetypes
MAX_FILE_SIZE_MB = 5
ALLOWED_EXTENSIONS = {
    # Images
    ".png",
    ".jpg",
    ".jpeg",
    # Documents
    ".pdf",
    ".txt",
    ".html",
    ".json",
    # Code
    ".py",
    ".js",
}
ALLOWED_MIME_TYPES = {
    "image/png",
    "image/jpeg",
    "application/pdf",
    "text/plain",
    "text/html",
    "application/json",
    "text/x-python",
    "application/javascript",
    "text/javascript",
}
ALLOWED_ZIP_EXTENSIONS = {"application/zip", "application/x-zip-compressed"}


async def validate_file(file: UploadFile) -> UploadFile:
    if not file.filename:
        raise HTTPException(status_code=400, detail="There is no file")
    if not file.content_type:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="Cannot determine the file's content type",
        )

    if file.content_type.lower() not in ALLOWED_MIME_TYPES:
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
    await file.seek(0)
    return file


def safe_extract(zip_path: Path, extract_to: Path):
    with zipfile.ZipFile(zip_path, "r") as zf:
        for member in zf.namelist():
            dest = extract_to / member
            if not str(dest.resolve()).startswith(str(extract_to.resolve())):
                raise HTTPException(status_code=400, detail="Unsafe path in zip file")
        zf.extractall(extract_to)


# async def upload_zip(
#     folders: List[UploadFile], background: Optional[BackgroundTasks] = None
# ):
#     for f in folders:
#         if f.content_type not in ALLOWED_ZIP_EXTENSIONS:
#             if not f.filename or not f.filename.lower().endswith(".zip"):
#                 raise HTTPException(
#                     status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
#                     detail="Expected a .zip file",
#                 )
#         tmp_dir = Path(tempfile.mkdtemp(prefix="zip_in"))
#         zip_path = tmp_dir / str(f.filename)


async def upload_files(files: List[UploadFile]):
    data = {}
    try:
        for f in files:
            f = await validate_file(f)
            data[f.filename] = "ok"
        return data
    except Exception as e:
        raise HTTPException(status_code=400, detail=e)


async def upload_folder(files: List[UploadFile]):
    upload_dir = "uploaded_folder"
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir, exist_ok=True)
    for f in files:
        f = await validate_file(f)
        contents = await f.read()
        filepath = os.path.join(upload_dir, f.filename or "unnamed_file.txt")
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "wb") as f:
            f.write(contents)
    return {"message": f"Uploaded {len(files)} files successfully"}

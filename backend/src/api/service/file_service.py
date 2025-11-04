import asyncio
import io
import json
import shutil
import zipfile
from pathlib import Path
from typing import Annotated, List, Optional, Sequence, Union

from fastapi import Depends, HTTPException, UploadFile
from starlette import status


from src.api.core import logger
from src.api.core.config import get_settings
from src.api.models import SuccessfulResponse


settings = get_settings()


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
    ".bin",
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
    "application/octet-stream",
    "text/javascript",
}
ALLOWED_ZIP_EXTENSIONS = {"application/zip", "application/x-zip-compressed"}


class SuccessFileServiceResponse(SuccessfulResponse):
    path: str | Path


class FileService:
    async def validate_file(self, file: UploadFile) -> UploadFile:
        if not file.filename:
            raise HTTPException(status_code=400, detail="There is no file")
        file = await self.validate_file_size(file)
        return file

    async def save_file(self, file: UploadFile, destination: str | Path) -> str:
        """
        Save an uploaded file to the specified destination.

        This method validates the uploaded file, ensures the target directory exists,
        and writes the file contents to disk.

        Args:
            file (UploadFile): The uploaded file received from the client.
            destination (str | Path): The target file path where the upload will be saved.

        Returns:
            str: The absolute path (as a POSIX string) to the saved file.

        Raises:
            HTTPException: If file validation or writing fails.
            OSError: For unexpected file system errors.
        """
        try:
            # Validate upload before saving
            await self.validate_file(file)

            # Normalize to a Path object
            filename = file.filename or "unknownFile.txt"
            destination_path = Path(destination).resolve() / filename
            try:
                # your file or folder creation logic
                destination_path.parent.mkdir(parents=True, exist_ok=True)
            except PermissionError as e:
                logger.error(
                    "Permission denied creating path %s: %s", destination_path, e
                )
                raise

            logger.info("Saving file %s to %s", file.filename, destination_path)

            # Write file content to disk
            with open(destination_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            logger.info("Successfully saved file: %s", destination_path)
            return destination_path.as_posix()

        except Exception as e:
            logger.exception("Error saving file %s: %s", file.filename, e)
            raise

    async def convert_to_uploadfile(
        self, path: Union[Path, str, UploadFile]
    ) -> UploadFile:

        if isinstance(path, UploadFile):
            return path

        path = Path(path)
        upload_file = UploadFile(
            filename=path.name,
            file=open(path, "rb"),  # important: open in binary mode
        )
        await self.validate_file(upload_file)
        return upload_file

    async def save_files(
        self, files: List[UploadFile], destination: str | Path
    ) -> SuccessFileServiceResponse:
        try:
            await asyncio.gather(*[self.save_file(f, destination) for f in files])
            return SuccessFileServiceResponse(
                status=status.HTTP_200_OK,
                detail="Saved files succesfully",
                path=destination,
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Could not process file uploads {str(e)}",
            )

    async def download_zip(
        self,
        files: Sequence[Union[Path, str]],
        folder_name: Optional[str],
    ) -> bytes:
        """Bundle multiple files into a zip and return as StreamingResponse."""
        buffer = io.BytesIO()
        folder_name = folder_name or "Untitled_Content"
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as z:
            for path in files:
                path = Path(path)
                if path.is_dir():
                    for subfile in path.rglob("*"):
                        if subfile.is_file():
                            arcname = (
                                f"{folder_name}/{subfile.relative_to(path.parent)}"
                            )
                            with open(subfile, "rb") as f:
                                z.writestr(str(arcname), f.read())
                elif path.is_file():
                    arcname = f"{folder_name}/{path.name}"
                    with open(path, "rb") as f:
                        z.writestr(arcname, f.read())
                else:
                    logger.warning(f"[WARN] Skipping invalid path: {path}")
        buffer.seek(0)
        return buffer.getvalue()  # type: bytes

    # Helpers
    async def validate_file_size(self, file: UploadFile) -> UploadFile:
        try:
            contents = await file.read()
            if len(contents) > MAX_FILE_SIZE_MB * 1024 * 1024:
                raise HTTPException(
                    status_code=400,
                    detail=f"{file.filename} exceeds {MAX_FILE_SIZE_MB}MB",
                )
            await file.seek(0)
            return file
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Could not read file contents {str(e)}",
            )

    async def validate_file_contents(self, file: UploadFile) -> bool:
        try:
            assert file.filename
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
            ext = Path(file.filename).suffix.lower()

            if ext not in ALLOWED_EXTENSIONS:
                raise HTTPException(
                    status_code=400, detail=f"Invalid file extension: {ext}"
                )
            return True
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Could not validate file contents {str(e)}",
            )


def get_file_service() -> FileService:
    return FileService()


FileServiceDep = Annotated[FileService, Depends(get_file_service)]

CONTENT_TYPE_MAPPING = {
    # Text
    ".txt": "text/plain",
    ".csv": "text/csv",
    ".json": "application/json",
    ".xml": "application/xml",
    # Web
    ".html": "text/html",
    ".htm": "text/html",
    ".css": "text/css",
    ".js": "application/javascript",
    ".ts": "application/typescript",
    ".jsx": "text/jsx",
    ".tsx": "text/tsx",
    # Images
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".svg": "image/svg+xml",
    ".ico": "image/vnd.microsoft.icon",
    ".webp": "image/webp",
    # Documents
    ".pdf": "application/pdf",
    ".doc": "application/msword",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".ppt": "application/vnd.ms-powerpoint",
    ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    ".xls": "application/vnd.ms-excel",
    ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    # Code
    ".py": "text/x-python",
    ".java": "text/x-java-source",
    ".c": "text/x-c",
    ".cpp": "text/x-c++",
    ".h": "text/x-c",
    ".hpp": "text/x-c++",
    # Compressed
    ".zip": "application/zip",
    ".tar": "application/x-tar",
    ".gz": "application/gzip",
    ".rar": "application/vnd.rar",
    ".7z": "application/x-7z-compressed",
}


def get_content_type(filename: str) -> str:
    """Return MIME type based on file extension, defaults to octet-stream."""
    import os

    ext = os.path.splitext(filename)[1].lower()
    return CONTENT_TYPE_MAPPING.get(ext, "application/octet-stream")
